#!/usr/bin/env python3

import subprocess

from argparse import ArgumentParser
from typing import Dict
from pathlib import Path


class ServerInfo:
    __slots__ = ['user', 'host', 'remote_games_path', 'ssh_port']
    user: str
    host: str
    remote_games_path: str
    ssh_port: int

    @staticmethod
    def from_values(user: str, host: str, remote_games_path: str, ssh_port: int = 22) -> 'ServerInfo':
        server_info = __class__()
        server_info.user = user
        server_info.host = host
        server_info.remote_games_path = remote_games_path
        server_info.ssh_port = ssh_port
        return server_info

    @staticmethod
    def from_config(config: Path) -> 'ServerInfo':
        with config.open('r') as fp:
            current_section = None
            for line in fp:
                if '[Server]' in line:
                    current_section = '[Server]'
                    continue

                if current_section == '[Server]':
                    if 'user:' in line:
                        user = line.split(': ')[1].strip()
                    elif 'host:' in line:
                        host = line.split(': ')[1].strip()
                    elif 'remote_games_dir:' in line:
                        remote_games_path = line.split(': ')[1].strip()
                    elif 'ssh_port:' in line:
                        ssh_port = int(line.split(': ')[1])

        return ServerInfo.from_values(user, host, remote_games_path, ssh_port)

    def create_scp_command(self, remote_path, local_path: Path) -> str:
        return 'scp -r -P ' + str(self.ssh_port) + ' ' + self.user + '@' + self.host + ':' + \
               remote_path + ' ' + str(local_path.absolute())

    def create_ssh_command(self, command: str) -> str:
        return 'ssh -p ' + str(self.ssh_port) + ' ' + self.user + '@' + self.host + ' ' + command


class GameInfo:
    __slots__ = ['name', 'game', 'updates', 'dlc']
    name: str
    game: Dict
    updates: Dict
    dlc: Dict

    def __repr__(self) -> str:
        return 'Game: ' + self.name + '\n' + \
               '\tGame Files:\n\t\t' + '\n\t\t'.join(self.game) + '\n' + \
               '\tUpdates:\n\t\t' + '\n\t\t'.join(self.updates) + '\n' + \
               '\tDLC:\n\t\t' + '\n\t\t'.join(self.dlc)


def get_game_info(name: str, server_info: ServerInfo) -> GameInfo:
    files = execute_remote_command(server_info, 'ls ' + server_info.remote_games_path + name)

    game_info = GameInfo()
    game_info.name = name
    game_info.game = []
    game_info.updates = []
    game_info.dlc = []
    for file in files.split('\n'):
        if 'dlc' in file.lower():
            game_info.dlc.append(file)
        elif 'update' in file.lower():
            game_info.updates.append(file)
        else:
            game_info.game.append(file)

    return game_info


def execute_remote_command(server_info: ServerInfo, command: str) -> str:
    return execute_command(server_info.create_ssh_command(command))


def execute_command(command: str):
    subprocess_cmd = command.split(' ')
    print('Executing: ' + command)
    res = subprocess.check_output(subprocess_cmd)
    return res.decode('utf-8').strip()


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

    # get information about game files
    game_info = get_game_info(args.game, server_info)
    print(game_info)

    # copy
    # unpack
    # convert to nsp
    # remove files


if __name__ == '__main__':
    main()
