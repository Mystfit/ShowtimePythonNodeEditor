from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Qt
from showtime_editor_conf import register_node
from showtime_editor_node_base import ShowtimeEditorNode, ShowtimeEditorGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils import dumpException

from showtime.showtime import ZstEntityType_PERFORMER
from showtime.showtime import ZstPerformer


class ShowtimeEditorPerformerContent(QDMNodeContentWidget):
    def initUI(self):
        pass

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


@register_node(ZstEntityType_PERFORMER)
class ShowtimeEditorNode_Performer(ShowtimeEditorNode):
    icon = "icons/in.png"
    op_title = "Performer"
    content_label_objname = "showtime_editor_node_performer"
    creatable = False

    def __init__(self, scene, performer):
        super().__init__(performer, scene, inputs=[], outputs=[])

    def initInnerClasses(self):
        self.content = ShowtimeEditorPerformerContent(self)
        self.grNode = ShowtimeEditorGraphicsNode(self)
