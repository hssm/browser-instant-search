# https://github.com/hssm/browser-instant-search
# Version 1.0

from aqt import *
from aqt.theme import theme_manager
from threading import Thread
import time

class InstantSearch:

    def __init__(self):
        self.last_search = ''
        self.save_at = 0

    def browser_will_show(self, browser):
        self.browser = browser
        # Text box changes
        self.browser.form.searchEdit.lineEdit().textEdited.connect(self.on_text_edited)
        # Drop-down selection
        self.browser.form.searchEdit.currentIndexChanged.connect(self.on_current_index_changed)

    def on_text_edited(self):
        """Textbox text has changed. Do a search."""
        text = self.browser.current_search()
        if text != self.last_search:
            try:
                self.last_search = text
                normed = self.browser.col.build_search_string(text)
                self.browser.table.search(normed)
                self.browser.form.searchEdit.setStyleSheet("")
                self.maybe_save_history(text)
            except Exception as err:
                self.save_at = None
                if theme_manager.night_mode:
                    self.browser.form.searchEdit.setStyleSheet("QComboBox {background-color: #4a3a36;}")
                else:
                    self.browser.form.searchEdit.setStyleSheet("QComboBox {background-color: #ffc9b9;}")

    def maybe_save_history(self, text):
        """Schedule for saving with a debounce"""
        if not text:
            self.save_at = None
            return
        saver = Thread(target=self.update_history, args=[text])
        self.save_at = time.time() + 2
        saver.start()

    def update_history(self, text):
        time.sleep(2)
        if not self.save_at or time.time() < self.save_at:
            # Another thread has superseded this one
            return
        if self.browser not in aqt.DialogManager._dialogs[self.browser.__class__.__name__]:
            # Browser was closed
            return
        self.browser.form.searchEdit.blockSignals(True)
        # Based on browser.py::update_history()
        sh = self.browser.mw.pm.profile.get("searchHistory", [])
        if text in sh:
            sh.remove(text)
        sh.insert(0, text)
        sh = sh[:30]
        # The clear() resets the cursor position so we restore it ourselves
        pos = self.browser.form.searchEdit.lineEdit().cursorPosition()
        self.browser.form.searchEdit.clear()
        self.browser.form.searchEdit.addItems(sh)
        self.browser.form.searchEdit.lineEdit().setCursorPosition(pos)
        self.browser.mw.pm.profile["searchHistory"] = sh
        self.browser.form.searchEdit.blockSignals(False)

    def on_current_index_changed(self, index):
        """Do a search on drop-down selection. -1 is text edit. Skip those as we handle already"""
        if index >= 0:
            self.on_text_edited()

_is = InstantSearch()

# Hooks
gui_hooks.browser_will_show.append(_is.browser_will_show)
