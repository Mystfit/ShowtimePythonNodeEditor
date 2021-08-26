from qtpy.QtWidgets import QDialog, QListWidget, QErrorMessage, QVBoxLayout, QListWidgetItem, QLineEdit, QPushButton, QAbstractItemView
from qtpy.QtCore import Qt

from showtime_editor_client import ShowtimeEditorClient

class ShowtimeEditorServerBrowser(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.ZST = ShowtimeEditorClient()
        self.ZST.create_client("ZSTServerBrowserClient")

        self.servername = ""
        self.serveraddress = ""
        self.initUI()

    def initUI(self):
        self.setModal(True)

        # Server list
        self.serverlist = QListWidget()
        self.serverlist.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.serverlist.itemClicked.connect(self.serverlist_clicked)
        self.refresh_server_list()

        # Handle new servers arriving whilst the dialog is open
        self.ZST.client.connection_events().server_discovered.add(self.servers_updated)
        self.ZST.client.connection_events().server_lost.add(self.servers_updated)

        # Join button
        self.connectbtn = QPushButton("Connect")
        self.connectbtn.clicked.connect(self.connect_btn_clicked)

        # Manual address entry
        self.serveraddressentry = QLineEdit()

        # Server list window layout
        layout = QVBoxLayout()
        layout.addWidget(self.serverlist)
        layout.addWidget(self.serveraddressentry)
        layout.addWidget(self.connectbtn)
        self.setLayout(layout)

    def serverlist_clicked(self, item):
        pass

    def servers_updated(self, client, serveraddress):
        self.refresh_server_list()

    def refresh_server_list(self):
        self.serverlist.clear()

        discoveredservers = self.ZST.client.get_discovered_servers()
        for server in discoveredservers:
            serveritem = QListWidgetItem()
            serveritem.setText("{0} - {1}".format(server.name, server.address))
            serveritem.setData(Qt.UserRole, server)
            self.serverlist.addItem(serveritem)

    def connect_btn_clicked(self):
        self.servername = ""
        self.serveraddress = ""

        if self.serverlist.selectedItems():
            self.servername = self.serverlist.currentItem().data(Qt.UserRole).name
            self.serveraddress = self.serverlist.currentItem().data(Qt.UserRole).address
        else:
            self.serveraddress = self.serveraddressentry.text()

        self.done(1)
