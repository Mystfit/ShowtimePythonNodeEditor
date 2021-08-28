from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Qt
from showtime_editor_conf import register_node
from showtime_editor_node_base import ShowtimeEditorNode, ShowtimeEditorGraphicsNode
from showtime_editor_socket import ShowtimePlugSocket
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils import dumpException

from showtime.showtime import ZstEntityType_COMPONENT
from showtime.showtime import ZstComponent


class ShowtimeEditorComponentContent(QDMNodeContentWidget):
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


@register_node(ZstEntityType_COMPONENT)
class ShowtimeEditorNode_Component(ShowtimeEditorNode):
    Socket_class = ShowtimePlugSocket

    icon = "icons/add.png"
    op_title = "Component"
    content_label_objname = "showtime_editor_node_component"
    creatable = False

    def __init__(self, scene, component):
        super().__init__(component, scene, inputs=[], outputs=[])

        # Register events
        # component.entity_events().child_entity_added.add(self.child_entity_added)
        # component.entity_events().child_entity_removed.add(self.child_entity_removed)

    def child_entity_added(self, entity):
        if entity:
            print(entity.URI().path())

    def child_entity_removed(self, entity_path):
        if entity_path:
            print(entity_path.path())

    def initInnerClasses(self):
        self.content = ShowtimeEditorComponentContent(self)
        self.grNode = ShowtimeEditorGraphicsNode(self)
