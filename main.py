import threading
import time

import os, sys
from qtpy.QtWidgets import QApplication

from showtime_editor_client import ShowtimeEditorClient

import showtime_editor_window
from showtime_editor_window import ShowtimeEditorWindow


if __name__ == '__main__':
    node_editor = ShowtimeEditorClient()
    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = ShowtimeEditorWindow()
    wnd.show()

    sys.exit(app.exec_())

