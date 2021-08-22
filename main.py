# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import showtime.showtime as ZST
import threading
import time
import atexit

import os, sys
from qtpy.QtWidgets import QApplication

import calc_window
from calc_window import CalculatorWindow

DEFAULT_CLIENT_NAME = "ShowtimeNodeEditor"

class EventLoop(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.setDaemon(True)
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            self.client.poll_once()
            time.sleep(0.001)

class ShowtimeNodeEditor:
    def __init__(self):
        self.client = None
        self.client_loop = None

    def create_client(self):
        self.client = ZST.ShowtimeClient()
        self.client.init(DEFAULT_CLIENT_NAME, True)
        self.client_loop = EventLoop(self.client)
        self.client_loop.start()

    def start(self):
        try:
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")

    def stop(self):
        self.client_loop.stop()
        self.client.leave()
        self.client.destroy()

if __name__ == '__main__':
    node_editor = ShowtimeNodeEditor()
    node_editor.create_client()
    node_editor.client.auto_join_by_name("LiveBridgeServer")
    atexit.register(node_editor.stop)

    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = CalculatorWindow()
    wnd.show()

    sys.exit(app.exec_())

