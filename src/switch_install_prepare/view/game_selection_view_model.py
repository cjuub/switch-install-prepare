from typing import List

from switch_install_prepare.view.view_model import ViewModel


class GameSelectionViewModel(ViewModel):
    __slots__ = ['selected_game_name', 'game_names']
    selected_game_name: str
    game_names: List[str]
