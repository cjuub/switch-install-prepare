from typing import List

from switch_install_prepare.view.view_model import ViewModel


class InstallableSelectionViewModel(ViewModel):
    __slots__ = ['checked_installables', 'installable_names']
    checked_installables: List[str]
    installable_names: List[str]
