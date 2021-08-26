LISTBOX_MIMETYPE = "application/x-item"

# OP_NODE_INPUT = 1
# OP_NODE_OUTPUT = 2
# OP_NODE_ADD = 3
# OP_NODE_SUB = 4
# OP_NODE_MUL = 5
# OP_NODE_DIV = 6


SHOWTIME_EDITOR_NODES = {
}


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference):
    if op_code in SHOWTIME_EDITOR_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" %(
            op_code, SHOWTIME_EDITOR_NODES[op_code]
        ))
    SHOWTIME_EDITOR_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator

def get_class_from_opcode(op_code):
    if op_code not in SHOWTIME_EDITOR_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return SHOWTIME_EDITOR_NODES[op_code]



# import all nodes and register them
from nodes import *