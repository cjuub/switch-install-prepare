from typing import List, Any

from switch_install_prepare.observer import Observer


class ViewModel:
    __observers: List[Observer]

    def __init__(self):
        self.__observers = []

    def add_observer(self, observer: Any):
        self.__observers.append(observer)

    def notify_observers(self):
        for observer in self.__observers:
            observer.notify()
