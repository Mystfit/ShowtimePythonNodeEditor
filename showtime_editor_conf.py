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
class EntityTypeNotRegistered(ConfException): pass


def register_node_now(entity_type, class_reference):
    print("Registering entity type {0} to node class {1}".format(entity_type, class_reference))
    if entity_type in SHOWTIME_EDITOR_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" %(
            entity_type, SHOWTIME_EDITOR_NODES[entity_type]
        ))
    SHOWTIME_EDITOR_NODES[entity_type] = class_reference


def register_node(entity_type):
    def decorator(original_class):
        register_node_now(entity_type, original_class)
        return original_class
    return decorator

def get_node_class_from_entity_type(entity_type):
    if entity_type not in SHOWTIME_EDITOR_NODES: raise EntityTypeNotRegistered("EntityType '%d' is not registered" % entity_type)
    return SHOWTIME_EDITOR_NODES[entity_type]

def get_node_class_from_entity(entity):
    if not entity:
        raise EntityTypeNotRegistered("Entity is None")
    return get_node_class_from_entity_type(entity.entity_type())


# import all nodes and register them
from nodes import *