import enum

from switch_install_prepare.observer import Observer
from switch_install_prepare.switch_install_prepare import SwitchInstallPrepare
from switch_install_prepare.view.installable_selection_view_model import InstallableSelectionViewModel


class InstallableSelectionPresenter(Observer):
    class Type(enum.IntEnum):
        GAME = 0,
        UPDATE = 1,
        DLC = 2

    __view_model: InstallableSelectionViewModel
    __application: SwitchInstallPrepare
    __type: Type

    def __init__(self, view_model: InstallableSelectionViewModel, application: SwitchInstallPrepare, type: Type):
        self.__view_model = view_model
        self.__application = application
        self.__type = type

    def on_view_created(self):
        self.__view_model.checked_installables = []
        self.__view_model.installable_names = []

    def on_game_selected(self):
        game_info = self.__application.get_selected_game_info()
        if self.__type == InstallableSelectionPresenter.Type.GAME:
            self.__view_model.installable_names = game_info.game
        elif self.__type == InstallableSelectionPresenter.Type.UPDATE:
            self.__view_model.installable_names = game_info.updates
        elif self.__type == InstallableSelectionPresenter.Type.DLC:
            self.__view_model.installable_names = game_info.dlc
        else:
            assert False

        self.__view_model.notify_observers()

    def notify(self):
        self.on_game_selected()
