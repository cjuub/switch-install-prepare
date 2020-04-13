import subprocess

from pathlib import Path

from switch_install_prepare.game_info import GameInfo
from switch_install_prepare.observer import Observer


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


class SwitchInstallPrepare:
    def __init__(self, server_info: ServerInfo):
        self.__server_info = server_info
        self.__game_changed_observers = []
        self.__selected_game_info = None

    def add_game_changed_observer(self, observer: Observer):
        self.__game_changed_observers.append(observer)

    def select_game(self, game_name: str):
        self.__selected_game_info = self.get_game_info(game_name, self.__server_info)
        
        for observer in self.__game_changed_observers:
            observer.notify()

    def get_selected_game_info(self) -> GameInfo:
        return self.__selected_game_info

    def get_game_list(self, server_info: ServerInfo):
        return self.execute_remote_command(server_info, 'ls ' + server_info.remote_games_path).strip().split('\n')

    def get_game_info(self, name: str, server_info: ServerInfo) -> GameInfo:
        files = self.execute_remote_command(server_info, 'ls ' + server_info.remote_games_path + name)
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

    def execute_remote_command(self, server_info: ServerInfo, command: str) -> str:
        return self.execute_command(server_info.create_ssh_command(command))

    def execute_command(self, command: str):
        subprocess_cmd = command.split(' ')
        print('Executing: ' + command)
        res = subprocess.check_output(subprocess_cmd)
        return res.decode('utf-8').strip()

