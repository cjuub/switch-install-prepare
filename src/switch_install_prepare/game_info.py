from typing import List


class GameInfo:
    __slots__ = ['name', 'game', 'updates', 'dlc']
    name: str
    game: List
    updates: List
    dlc: List

    def __repr__(self) -> str:
        return 'Game: ' + self.name + '\n' + \
               '\tGame Files:\n\t\t' + '\n\t\t'.join(self.game) + '\n' + \
               '\tUpdates:\n\t\t' + '\n\t\t'.join(self.updates) + '\n' + \
               '\tDLC:\n\t\t' + '\n\t\t'.join(self.dlc)

