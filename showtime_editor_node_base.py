from qtpy.QtGui import QImage
from qtpy.QtCore import QRectF
from qtpy.QtWidgets import QLabel, QSizePolicy, QGridLayout, QPushButton

from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.utils import dumpException
from nodeeditor.node_editor_widget import NodeEditorWidget


class ShowtimeEditorGraphicsNode(QDMGraphicsNode):
    maximised_width = 600
    maximised_height = 500
    minimised_width = 160
    minimised_height = 74

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
        self.layout.addWidget(self.subgraph, 1, 1)


class ShowtimeEditorNode(Node):
    icon = ""
    # op_code = 0
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

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def evalOperation(self, input1, input2):
        pass
        # return 123

    def evalImplementation(self):
        pass
        # i1 = self.getInput(0)
        # i2 = self.getInput(1)

        # if i1 is None or i2 is None:
        #     self.markInvalid()
        #     self.markDescendantsDirty()
        #     self.grNode.setToolTip("Connect all inputs")
        #     return None

        # else:
        #     val = self.evalOperation(i1.eval(), i2.eval())
        #     self.value = val
        #     self.markDirty(False)
        #     self.markInvalid(False)
        #     self.grNode.setToolTip("")

        #     self.markDescendantsDirty()
        #     self.evalChildren()

        #     return val

    def eval(self):
        pass
        # if not self.isDirty() and not self.isInvalid():
        #     print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
        #     return self.value

        # try:

        #     val = self.evalImplementation()
        #     return val
        # except ValueError as e:
        #     self.markInvalid()
        #     self.grNode.setToolTip(str(e))
        #     self.markDescendantsDirty()
        # except Exception as e:
        #     self.markInvalid()
        #     self.grNode.setToolTip(str(e))
        #     dumpException(e)

    def toggle_maximised(self):
        if self.ismaximised:
            self.minimize()
        else:
            self.maximise()

    def maximise(self):
        self.ismaximised = True
        self.grNode.width = ShowtimeEditorGraphicsNode.maximised_width
        self.grNode.height = ShowtimeEditorGraphicsNode.maximised_height
        self.content.resize(self.grNode.width, self.grNode.height-50)
        self.content.subgraph.setVisible(self.ismaximised)

    def minimize(self):
        self.ismaximised = False
        self.grNode.width = ShowtimeEditorGraphicsNode.minimised_width
        self.grNode.height = ShowtimeEditorGraphicsNode.minimised_height
        self.content.resize(self.grNode.width, self.grNode.height-50)
        self.content.subgraph.setVisible(self.ismaximised)

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

