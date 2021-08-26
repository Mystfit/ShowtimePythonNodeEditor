from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Qt
from showtime_editor_conf import register_node
from showtime_editor_node_base import ShowtimeEditorNode, ShowtimeEditorGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils import dumpException

from showtime.showtime import ZstPerformer

PERFORMER_ID = "performer"

class ShowtimeEditorPerformerContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node(PERFORMER_ID)
class ShowtimeEditorNode_Performer(ShowtimeEditorNode):
    icon = "icons/in.png"
    op_title = "Performer"
    content_label_objname = "showtime_editor_node_performer"
    creatable = False

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[])

    def initInnerClasses(self):
        self.content = ShowtimeEditorEntityBaseContent(self)
        self.grNode = ShowtimeEditorGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)
