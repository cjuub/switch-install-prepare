from PyQt5 import QtCore

from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from switch_install_prepare.observer import Observer
from switch_install_prepare.view.game_selection_presenter import GameSelectionPresenter
from switch_install_prepare.view.game_selection_view_model import GameSelectionViewModel


class __GameSelectionWidgetMeta(type(QListWidget), type(Observer)):
    pass


class GameSelectionWidget(QListWidget, Observer, metaclass=__GameSelectionWidgetMeta):

    def __init__(self, view_model: GameSelectionViewModel, presenter: GameSelectionPresenter):
        super().__init__()
        self.__view_model = view_model
        self.__presenter = presenter

        self.clearSelection()
        self.itemSelectionChanged.connect(self.on_game_selected)

        self.__view_model.add_observer(self)
        self.__presenter.on_view_created()

    def on_game_selected(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return

        self.__view_model.selected_game_name = selected_items[0].text()
        self.__presenter.on_game_selected()

    def notify(self):
        self.clear()
        for game_name in self.__view_model.game_names:
            list_item = QListWidgetItem(game_name)
            flags = list_item.flags()
            list_item.setFlags(flags | QtCore.Qt.ItemIsSelectable)
            self.addItem(list_item)
