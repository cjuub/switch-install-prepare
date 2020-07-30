import glob
import os
import shutil
import subprocess
import tempfile

from pathlib import Path
from typing import List

from switch_install_prepare.game_info import GameInfo
from switch_install_prepare.observer import Observer


class ServerInfo:
    __slots__ = ['user', 'host', 'remote_games_path', 'ssh_port', 'path_4nxci', 'prod_keys']
    user: str
    host: str
    remote_games_path: str
    ssh_port: int
    path_4nxci: Path
    prod_keys: Path

    @staticmethod
    def from_values(user: str,
                    host: str,
                    remote_games_path: str,
                    path_4nxci: Path,
                    prod_keys: Path,
                    ssh_port: int = 22) -> 'ServerInfo':
        server_info = __class__()
        server_info.user = user
        server_info.host = host
        server_info.remote_games_path = remote_games_path
        server_info.ssh_port = ssh_port
        server_info.path_4nxci = path_4nxci
        server_info.prod_keys = prod_keys
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
                    elif '4nxci_path:' in line:
                        path_4nxci = Path(line.split(': ')[1].strip())
                    elif 'prod_keys:' in line:
                        prod_keys = Path(line.split(': ')[1].strip())

        return ServerInfo.from_values(user, host, remote_games_path, path_4nxci, prod_keys, ssh_port)

    def create_scp_command(self, remote_path: str, local_path: Path) -> List[str]:
        return ['scp', '-r', '-P', str(self.ssh_port), self.user + '@' + self.host + ':' +
                remote_path, str(local_path.absolute())]

    def create_ssh_command(self, command: List[str]) -> List[str]:
        return ['ssh', '-p', str(self.ssh_port), self.user + '@' + self.host] + command


class SwitchInstallPrepare:
    def __init__(self, server_info: ServerInfo):
        self.__server_info = server_info
        self.__game_changed_observers = []
        self.__selected_game_info = None
        self.__selected_files = set()

    def add_game_changed_observer(self, observer: Observer):
        self.__game_changed_observers.append(observer)

    def select_game(self, game_name: str):
        self.__selected_game_info = self.get_game_info(game_name, self.__server_info)
        
        for observer in self.__game_changed_observers:
            observer.notify()

    def get_selected_game_info(self) -> GameInfo:
        return self.__selected_game_info

    def get_game_list(self, server_info: ServerInfo):
        return self.execute_remote_command(server_info, ['ls', server_info.remote_games_path]).strip().split('\n')

    def get_game_info(self, name: str, server_info: ServerInfo) -> GameInfo:
        files = self.execute_remote_command(server_info, ['ls', server_info.remote_games_path + name])
        game_info = GameInfo()
        game_info.name = name
        game_info.game = []
        game_info.updates = []
        game_info.dlc = []
        for file in files.split('\n'):
            if 'dlc' in file.lower():
                game_info.dlc.append(file)
            elif 'update' in file.lower() or '[upd]' in file.lower():
                game_info.updates.append(file)
            else:
                game_info.game.append(file)

        return game_info

    def add_installable(self, installable: str):
        game_info = self.get_selected_game_info()
        self.__selected_files.add((installable, game_info))

    def remove_installable(self, installable: str):
        game_info = self.get_selected_game_info()
        self.__selected_files.remove((installable, game_info))

    def _collect_game_files(self, root_directory: Path, output_directory: Path):
        for filename in glob.iglob(str(root_directory) + '**/**', recursive=True):
            print(filename)
            if filename.endswith('.nsp') or filename.endswith('.xci'):
                shutil.move(filename, str(output_directory))
            elif filename.endswith('.rar'):
                self.execute_command(['unrar', 'x', '-o+', filename, str(output_directory)])

        for filename in glob.iglob(str(output_directory) + '**/*.xci', recursive=True):
            self.execute_command([str(self.__server_info.path_4nxci),
                                  '-k', str(self.__server_info.prod_keys),
                                  '-o', str(output_directory),
                                  filename])
            os.remove(filename)

    def _download_file(self, server_info: ServerInfo, game_info: GameInfo, file: str):
        working_directory = Path(os.getcwd()) / 'nsps'
        os.makedirs(working_directory, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=working_directory) as local_path:
            local_path = Path(local_path)
            remote_path = '"' + server_info.remote_games_path + game_info.name + '/' + file + '"'
            self.execute_command(server_info.create_scp_command(remote_path, local_path))

            self._collect_game_files(local_path, working_directory)

    def download_selected_files(self):
        for file, game_info in self.__selected_files:
            self._download_file(self.__server_info, game_info, file)

    def execute_remote_command(self, server_info: ServerInfo, command: List[str]) -> str:
        return self.execute_command(server_info.create_ssh_command(command))

    def execute_command(self, command: List[str]):
        print('Executing: ' + ' '.join(command))
        res = subprocess.check_output(command)
        print('done')
        return res.decode('utf-8').strip()
