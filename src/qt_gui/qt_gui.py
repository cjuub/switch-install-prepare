import PyQt5

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from typing import List

from qt_gui.game_selection_widget import GameSelectionWidget
from qt_gui.installable_selection_widget import InstallableSelectionWidget

from switch_install_prepare.game_info import GameInfo
from switch_install_prepare.installable_data import InstallableData
from switch_install_prepare.switch_install_prepare import SwitchInstallPrepare
from switch_install_prepare.view.game_selection_presenter import GameSelectionPresenter
from switch_install_prepare.view.game_selection_view_model import GameSelectionViewModel
from switch_install_prepare.view.installable_selection_presenter import InstallableSelectionPresenter
from switch_install_prepare.view.installable_selection_view_model import InstallableSelectionViewModel


class QtGui:
    def __init__(self, application: SwitchInstallPrepare, initial_game_list: List[str]):

        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        self.__app = QApplication([])
        self.__window = QWidget()
        self.__window.setMinimumWidth(1366)

        print(self.__app.screens()[0].physicalDotsPerInch())

        layout = QHBoxLayout()
        done_button = QPushButton()
        done_button.setText('Done')
        done_button.clicked.connect(lambda: print('asdf'))
        layout.addWidget(done_button)

        self.game_selection_view_model = GameSelectionViewModel()
        self.game_selection_presenter = GameSelectionPresenter(self.game_selection_view_model, application, initial_game_list)
        self.game_selection_widget = GameSelectionWidget(self.game_selection_view_model, self.game_selection_presenter)
        self.game_selection_presenter.on_view_created()
        layout.addWidget(self.game_selection_widget)

        game_installable_selection_view_model = InstallableSelectionViewModel()
        game_installable_selection_presenter = \
            InstallableSelectionPresenter(game_installable_selection_view_model,
                                          application,
                                          InstallableSelectionPresenter.Type.GAME)
        self.game_installable_selection_widget = \
            InstallableSelectionWidget(game_installable_selection_view_model, game_installable_selection_presenter)

        update_installable_selection_view_model = InstallableSelectionViewModel()
        update_installable_selection_presenter = \
            InstallableSelectionPresenter(update_installable_selection_view_model,
                                          application,
                                          InstallableSelectionPresenter.Type.UPDATE)
        self.update_installable_selection_widget = \
            InstallableSelectionWidget(update_installable_selection_view_model, update_installable_selection_presenter)

        dlc_installable_selection_view_model = InstallableSelectionViewModel()
        dlc_installable_selection_presenter = \
            InstallableSelectionPresenter(dlc_installable_selection_view_model,
                                          application,
                                          InstallableSelectionPresenter.Type.DLC)
        self.dlc_installable_selection_widget = \
            InstallableSelectionWidget(dlc_installable_selection_view_model, dlc_installable_selection_presenter)

        file_types_layout = QVBoxLayout()
        file_types_layout.addWidget(self.game_installable_selection_widget)
        file_types_layout.addWidget(self.update_installable_selection_widget)
        file_types_layout.addWidget(self.dlc_installable_selection_widget)
        layout.addLayout(file_types_layout)

        application.add_game_changed_observer(game_installable_selection_presenter)
        application.add_game_changed_observer(update_installable_selection_presenter)
        application.add_game_changed_observer(dlc_installable_selection_presenter)

        self.__window.setLayout(layout)
        self.__window.show()

    def execute(self):
        self.__app.exec_()

    def on_game_list_changed(self, game_list: List[str]) -> None:
        self.game_selection_widget.update_contents(game_list)

    def on_selected_game_changed(self, game_info: GameInfo):
        game_installable_data = InstallableData()
        game_installable_data.names = game_info.game
        self.game_installable_selection_widget.update_contents(game_installable_data)

        update_installable_data = InstallableData()
        update_installable_data.names = game_info.updates
        self.update_installable_selection_widget.update_contents(update_installable_data)

        dlc_installable_data = InstallableData()
        dlc_installable_data.names = game_info.dlc
        self.dlc_installable_selection_widget.update_contents(dlc_installable_data)
