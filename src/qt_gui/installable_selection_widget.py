from PyQt5 import QtCore
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from switch_install_prepare.observer import Observer
from switch_install_prepare.view.installable_selection_presenter import InstallableSelectionPresenter
from switch_install_prepare.view.installable_selection_view_model import InstallableSelectionViewModel


class __GameSelectionWidgetMeta(type(QListWidget), type(Observer)):
    pass


class InstallableSelectionWidget(QListWidget, Observer, metaclass=__GameSelectionWidgetMeta):

    def __init__(self, view_model: InstallableSelectionViewModel, presenter: InstallableSelectionPresenter):
        super().__init__()
        self.__view_model = view_model
        self.__presenter = presenter

        self.__view_model.add_observer(self)
        self.__presenter.on_view_created()

    def update_contents(self):
        self.clear()
        for installable in self.__view_model.installable_names:
            checkbox = QListWidgetItem(installable)
            flags = checkbox.flags()
            checkbox.setFlags(flags | QtCore.Qt.ItemIsUserCheckable)

            if installable in self.__view_model.checked_installables:
                checkbox.setCheckState(True)
            else:
                checkbox.setCheckState(False)

            self.addItem(checkbox)

        self.itemChanged.connect(self.__check_state_changed)

    def notify(self):
        self.update_contents()

    def __check_state_changed(self):
        for i in range(self.count()):
            checkbox = self.item(i)
            if checkbox.checkState() != 0:
                self.__presenter.on_installable_checked(checkbox.text())
            elif checkbox.checkState() == 0:
                self.__presenter.on_installable_unchecked(checkbox.text())
