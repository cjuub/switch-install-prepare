#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path

from switch_install_prepare.switch_install_prepare import SwitchInstallPrepare, ServerInfo
from qt_gui.qt_gui import QtGui


def main():
    parser = ArgumentParser()
    parser.add_argument('game',
                        help='The name of the game prepare for installation',
                        type=str)
    parser.add_argument('--config',
                        help='Path to config file',
                        type=Path,
                        default=Path(__file__).parents[1] / 'switch_prepare_install.ini')
    args = parser.parse_args()

    server_info = ServerInfo.from_config(args.config)

    # get all games
    application = SwitchInstallPrepare(server_info)
    game_list = application.get_game_list(server_info)

    # get information about game files
    # game_info = application.get_game_info(args.game, server_info)

    gui = QtGui(application, game_list)
    # gui.on_game_list_changed(game_list)
    # gui.on_selected_game_changed(game_info)
    gui.execute()

    # copy
    # unpack
    # convert to nsp
    # remove files


if __name__ == '__main__':
    main()
