from typing import List

from switch_install_prepare.observer import Observer
from switch_install_prepare.switch_install_prepare import SwitchInstallPrepare
from switch_install_prepare.view.game_selection_view_model import GameSelectionViewModel


class GameSelectionPresenter:
    __view_model: GameSelectionViewModel
    __application: SwitchInstallPrepare
    __game_selected_observers: List[Observer]

    def __init__(self,
                 view_model: GameSelectionViewModel,
                 application: SwitchInstallPrepare,
                 initial_game_list: List[str]):
        self.__view_model = view_model
        self.__application = application
        self.__last_game_list = initial_game_list

    def on_view_created(self):
        self.__view_model.game_names = self.__last_game_list
        self.__view_model.notify_observers()

    def on_game_selected(self):
        game_name = self.__view_model.selected_game_name
        self.__application.select_game(game_name)
