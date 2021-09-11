from qtpy.QtGui import QImage, QPixmap
from qtpy.QtCore import QRectF, QDataStream, QIODevice, Qt
from qtpy.QtWidgets import QLabel, QSizePolicy, QGridLayout, QPushButton, QGraphicsItem

from showtime_editor_conf import SHOWTIME_EDITOR_NODES, get_node_class_from_entity, get_node_class_from_entity_type, LISTBOX_MIMETYPE
from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_TOP, RIGHT_TOP
from nodeeditor.utils import dumpException
from nodeeditor.node_editor_widget import NodeEditorWidget


DEBUG = True
DEBUG_CONTEXT = True


class ShowtimeEditorGraphicsNode(QDMGraphicsNode):
    maximised_width = 1280
    maximised_height = 900
    minimised_width = 160
    minimised_height = 74
    maximised_padding = 25

    def initUI(self):
        super().initUI()
        self.setAcceptDrops(True)

    def initSizes(self):
        super().initSizes()
        self.width = ShowtimeEditorGraphicsNode.minimised_width
        self.height = ShowtimeEditorGraphicsNode.minimised_height

        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class ShowtimeEditorContent(QDMNodeContentWidget):
    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Create subgraph canvas to hold child nodes
        self.subgraph = NodeEditorWidget(self)
        self.subgraph.setVisible(False)
        self.subgraph.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        # self.subgraph.setAcceptDrops(True)
        self.subgraph.scene.getView().setAcceptDrops(True)

        self.layout.addWidget(self.subgraph, 1, 1)


class ShowtimeEditorNode(Node):
    icon = ""
    op_code = ""
    op_title = "Undefined"
    content_label = ""
    content_label_objname = "showtime_editor_node_bg"
    creatable = False

    GraphicsNode_class = ShowtimeEditorGraphicsNode
    NodeContent_class = ShowtimeEditorContent

    def __init__(self, entity, scene, parent_node=None, inputs=[], outputs=[]):
        super().__init__(scene, entity.URI().last().path(), inputs, outputs)

        # self.value = None
        self.entity = entity
        self.parent_node = parent_node

        # it's really important to mark all nodes Dirty by default
        self.markDirty()

        self.ismaximised = False

        # Pass events to subgraph
        self.content.subgraph.scene.addDropListener(self.onDrop)
        self.content.subgraph.scene.addDragEnterListener(self.onDragEnter)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def toggle_maximised(self):
        if self.ismaximised:
            self.minimize()
        else:
            self.maximise()

    def maximise(self):
        self.ismaximised = True
        self.grNode.setAcceptHoverEvents(False)

        # Set size values
        title_offset = self.grNode.title_height + self.grNode.title_vertical_padding
        self.grNode.width = (self.parent_node.content.width() if self.parent_node else self.scene.getView().viewport().width()) - ShowtimeEditorGraphicsNode.maximised_padding
        self.grNode.height = (self.parent_node.content.height() if self.parent_node else self.scene.getView().viewport().height()) - ShowtimeEditorGraphicsNode.maximised_padding
        self.content.resize(self.grNode.width, self.grNode.height - title_offset)
        
        # Show child graph
        self.content.subgraph.setVisible(self.ismaximised)

        # Remember last node position
        self.minimized_pos = self.pos
        self.setPos(ShowtimeEditorGraphicsNode.maximised_padding * 0.5, ShowtimeEditorGraphicsNode.maximised_padding * 0.5)

        # Draw maximised node on top
        self.grNode.setZValue(len(self.content.subgraph.scene.nodes) + 10)

    def minimize(self):
        self.ismaximised = False
        self.grNode.setAcceptHoverEvents(True)

        # Restore sizes
        self.grNode.width = ShowtimeEditorGraphicsNode.minimised_width
        self.grNode.height = ShowtimeEditorGraphicsNode.minimised_height
        self.content.resize(self.grNode.width, self.grNode.height)

        # Hide child graph
        self.content.subgraph.setVisible(self.ismaximised)

        # Restore node position
        self.setPos(self.minimized_pos.x(), self.minimized_pos.y())

        # Restore node stacking order
        self.grNode.setZValue(0)

    def onDoubleClicked(self, event):
        """Event handling double click on Graphics Node in `Scene`"""
        self.toggle_maximised()

    def onInputChanged(self, socket=None):
        pass
        # print("%s::__onInputChanged" % self.__class__.__name__)
        # self.markDirty()
        # self.eval()

    def serialize(self):
        res = super().serialize()
        res['URI'] = self.entity.URI().path()
        # res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialized ShowtimeEditorNode '%s'" % self.__class__.__name__, "res:", res)
        return res

    def onEdgeConnectionChanged(self, new_edge):
        # We will receive two events so limit ourself to output->input connections only
        output_plug = new_edge.start_socket.plug
        input_plug = new_edge.end_socket.plug
        # print("Connecting cable between {0} {1}".format(output_plug.URI().path(), input_plug.URI().path()))

        if output_plug.URI().contains(self.entity.URI()):
            # Our entity contains the output plug
            cable = output_plug.connect_cable_async(input_plug)
            cable.synchronisable_events().synchronisable_activated.add(lambda synchronisable: print("Cable activated"))

    def onDragEnter(self, event):
        print("Subgraph received drag event")

    def onDrop(self, event):
        print("Redirected drop event to node {0}".format(self))
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readQString()
            text = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%s] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                # (entity, scene, parent_node=None)
                node = get_node_class_from_entity_type(op_code)(self.content.subgraph.scene, None, self)
                node.setPos(mouse_position.x(), mouse_position.y())
                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()
