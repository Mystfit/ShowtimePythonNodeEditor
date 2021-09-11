from nodeeditor.node_socket import Socket
from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_socket import Socket, LEFT_TOP, RIGHT_TOP
from showtime_editor_conf import register_node


"""Class representing a socket that routes nodes between different node levels"""
class ShowtimeMetaSocket(Socket):
    Socket_GR_Class = QDMGraphicsSocket
    creatable = False

    """Class representing Socket."""
    def __init__(self, scene, entity, parent_node, position, socket_type, is_input):
        # Count on our node side
        plug_index = 0

        # Limit number of connections depending on max cables that can be connected
        multi_edges = True

        # Position is based on input/output direction
        position = LEFT_TOP if is_input else RIGHT_TOP

        # Add to parent
        if is_input:
            parent_node.inputs.append(self)
        else:
            parent_node.outputs.append(self)

        super().__init__(parent_node, plug_index, position, 0, True, 0, is_input)
