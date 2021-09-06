from qtpy.QtWidgets import QLineEdit, QPushButton
from qtpy.QtCore import Qt
from showtime_editor_conf import register_node
from showtime_editor_node_base import ShowtimeEditorGraphicsNode, ShowtimeEditorContent
from showtime_editor_socket import ShowtimeOutputPlugSocket
from nodes.component import ShowtimeEditorNode_Component
from nodeeditor.utils import dumpException

from showtime.showtime import ZstEntityType_COMPONENT, ZstValueType_IntList
from showtime.showtime import ZstComponent, ZstOutputPlug

class ShowtimeEditorButtonContent(ShowtimeEditorContent):
    def initUI(self):
        ShowtimeEditorContent.initUI(self)
        self.button = QPushButton("Bang")
        self.layout.addWidget(self.button, 1, 1)

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


class ShowtimeButton(ZstComponent):
	BUTTON_TYPE = "button"

	def __init__(self, name):
		ZstComponent.__init__(self, ShowtimeButton.BUTTON_TYPE, name)
		self.output_plug = ZstOutputPlug("pressed", ZstValueType_IntList)

	def on_registered(self):
		self.add_child(self.output_plug)


@register_node(ShowtimeButton.__qualname__)
class ShowtimeEditorNode_Button(ShowtimeEditorNode_Component): 
    icon = "icons/output.png"
    op_title = "Button"
    op_code = ShowtimeButton.__qualname__
    content_label_objname = "showtime_editor_node_button"
    creatable = True

    def __init__(self, scene, entity=None, parent_node=None):
        self.button = entity if entity else ShowtimeButton("button")
        super().__init__(scene, self.button, parent_node)
        parent_node.entity.entity_events().child_entity_added.add(lambda entity: self.create_socket())
        parent_node.entity.add_child(self.button)

    def create_socket(self):
        print("Creating button socket")
        self.socket = ShowtimeOutputPlugSocket(self.scene, self.button.output_plug, self)

    def initInnerClasses(self):
        self.content = ShowtimeEditorButtonContent(self)
        self.content.button.clicked.connect(self.send_pressed)
        self.grNode = ShowtimeEditorGraphicsNode(self)

    def send_pressed(self, state):
    	self.button.output_plug.append_int(int(self.content.button.isChecked()))
    	self.button.output_plug.fire()
