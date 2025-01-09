# https://github.com/hssm/browser-instant-search
# Version 1.0

from aqt import gui_hooks
from aqt.theme import theme_manager


class InstantSearch:
    def __init__(self):
        self.last_search = ''

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
                normed = self.browser.col.build_search_string(text)
                self.last_search = normed
                self.browser.table.search(normed)
                self.browser.form.searchEdit.setStyleSheet("")
            except Exception as err:
                # This is breaking the browser UI ??? This has to be a qt bug.
                # if theme_manager.night_mode:
                #     self.browser.form.searchEdit.setStyleSheet("QComboBox {background-color: #4a3a36;}")
                # else:
                #     self.browser.form.searchEdit.setStyleSheet("QComboBox {background-color: #ffc9b9;}")
                pass

    def on_current_index_changed(self, index):
        """Do a search on drop-down selection. -1 is text edit. Skip those as we handle already"""
        if index >= 0:
            self.on_text_edited()


_is = InstantSearch()

# Hooks
gui_hooks.browser_will_show.append(_is.browser_will_show)
