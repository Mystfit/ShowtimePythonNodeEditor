from nodeeditor.node_socket import Socket
from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_socket import Socket, LEFT_BOTTOM, LEFT_CENTER, LEFT_TOP, RIGHT_BOTTOM, RIGHT_CENTER, RIGHT_TOP
from showtime_editor_conf import register_node
from qtpy.QtWidgets import QGraphicsTextItem
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont, QColor

import showtime.showtime as ZST
from showtime.showtime import ZstPlug, ZstInputPlug, ZstOutputPlug

class ShowtimeEditorGraphicsSocket(QDMGraphicsSocket):
    def __init__(self, socket:'Socket'):
        super().__init__(socket)
        self.initUI()

    def initUI(self):
        self.socket_label = QGraphicsTextItem(self)
        self.socket_label.setDefaultTextColor(Qt.white)
        self.socket_label.setFont(QFont("Ubuntu", 10))
        # self.socket_label.setTextWidth(self.socket_label.boundingRect().width())

    def update_socket_label(self):
        self.socket_label.setPos(-self.socket_label.boundingRect().width() if self.socket_type == 2 else 0, 0)


class ShowtimePlugSocket(Socket):
    Socket_GR_Class = ShowtimeEditorGraphicsSocket
    creatable = False

    """Class representing Socket."""
    def __init__(self, scene, entity, parent_node, position, socket_type, is_input):
        """
        :param node: reference to the :class:`~nodeeditor.node_node.Node` containing this `Socket`
        :type node: :class:`~nodeeditor.node_node.Node`
        :param index: Current index of this socket in the position
        :type index: ``int``
        :param position: Socket position. See :ref:`socket-position-constants`
        :param socket_type: Constant defining type(color) of this socket
        :param multi_edges: Can this socket have multiple `Edges` connected?
        :type multi_edges: ``bool``
        :param count_on_this_node_side: number of total sockets on this position
        :type count_on_this_node_side: ``int``
        :param is_input: Is this an input `Socket`?
        :type is_input: ``bool``

        :Instance Attributes:

            - **node** - reference to the :class:`~nodeeditor.node_node.Node` containing this `Socket`
            - **edges** - list of `Edges` connected to this `Socket`
            - **grSocket** - reference to the :class:`~nodeeditor.node_graphics_socket.QDMGraphicsSocket`
            - **position** - Socket position. See :ref:`socket-position-constants`
            - **index** - Current index of this socket in the position
            - **socket_type** - Constant defining type(color) of this socket
            - **count_on_this_node_side** - number of sockets on this position
            - **is_multi_edges** - ``True`` if `Socket` can contain multiple `Edges`
            - **is_input** - ``True`` if this socket serves for Input
            - **is_output** - ``True`` if this socket serves for Output
        """
        # Cast and store plug
        plug = ZST.cast_to_plug(entity)
        if not plug:
            raise Exception("Socket was not given a plug entity to wrap, was given {0}".format(entity))
        self.plug = ZST.cast_to_input_plug(entity) if plug.direction() == ZST.ZstPlugDirection_IN_JACK else ZST.cast_to_output_plug(entity)

        # Count on our node side
        plug_index = self.get_plug_index()

        # Limit number of connections depending on max cables that can be connected
        multi_edges = True if self.plug.max_connected_cables() > 1 or self.plug.max_connected_cables() < 0 else False

        # Super socket class
        super().__init__(parent_node, plug_index, position, socket_type, multi_edges, 0, is_input)

        # Set the socket label
        self.grSocket.socket_label.setPlainText(self.plug.URI().last().path())
        self.grSocket.update_socket_label()

        # Resize parent node to fit all children
        parent_node.resize()

    def get_plug_index(self):
        input_index = -1
        output_index = -1
        plug_index = -1
        parent_entities = self.plug.parent().get_child_entities()
        for entity in parent_entities:
            neighbour_plug = ZST.cast_to_plug(entity)
            if neighbour_plug:
                # Count how many input and output plugs we have
                if neighbour_plug.direction() == ZST.ZstPlugDirection_IN_JACK:
                    input_index += 1
                else:
                    output_index += 1

                # Match our plug to get its index
                if neighbour_plug.URI().path() == self.plug.URI().path():
                    plug_index = input_index if self.plug.direction() == ZST.ZstPlugDirection_IN_JACK else output_index

        print("Total inputs {0}, outputs {1}, Index for plug {2} is {3}".format(input_index, output_index, self.plug.URI().path(), plug_index))
        return plug_index


@register_node(ZstInputPlug.__qualname__)
class ShowtimeInputPlugSocket(ShowtimePlugSocket):
    creatable = False

    def __init__(self, scene, entity, parent_node):
        # Put plug on left or right depending on direction
        position = LEFT_TOP
        socket_type = 1
        is_input = True
        
        ShowtimePlugSocket.__init__(self, scene, entity, parent_node, position, socket_type, is_input)
        parent_node.inputs.append(self)
        


@register_node(ZstOutputPlug.__qualname__)
class ShowtimeOutputPlugSocket(ShowtimePlugSocket):
    creatable = False

    def __init__(self, scene, entity, parent_node):
        # Put plug on left or right depending on direction
        position = RIGHT_TOP
        socket_type = 2
        is_input = False

        ShowtimePlugSocket.__init__(self, scene, entity, parent_node, position, socket_type, is_input)
        parent_node.outputs.append(self)
