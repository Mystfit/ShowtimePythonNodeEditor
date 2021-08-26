from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtCore import QDataStream, QIODevice, Qt
from qtpy.QtWidgets import QAction, QGraphicsProxyWidget, QMenu

from showtime_editor_conf import SHOWTIME_EDITOR_NODES, get_class_from_opcode, LISTBOX_MIMETYPE
from nodeeditor.node_editor_widget import NodeEditorWidget
from nodeeditor.node_edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER, EDGE_TYPE_SQUARE
from nodeeditor.node_graphics_view import MODE_EDGE_DRAG
from nodeeditor.utils import dumpException

DEBUG = False
DEBUG_CONTEXT = False


class ShowtimeEditorSubWindow(NodeEditorWidget):
    def __init__(self, client):
        super().__init__()
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.ZST = client
        print(self.ZST)
        print(self.ZST.client)
        print(self.ZST.client_loop.is_running)

        self.setTitle()
        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []
        self._entity_to_node = {}

        self.register_graph_events()

    def register_graph_events(self):
        self.ZST.client.hierarchy_events().performer_arriving.add(self.performer_arriving)
        self.ZST.client.hierarchy_events().performer_leaving.add(self.performer_leaving)
        self.ZST.client.hierarchy_events().entity_arriving.add(self.entity_arriving)
        self.ZST.client.hierarchy_events().entity_leaving.add(self.entity_leaving)
        self.ZST.client.hierarchy_events().entity_updated.add(self.entity_updated)
        self.ZST.client.hierarchy_events().factory_arriving.add(self.factory_arriving)
        self.ZST.client.hierarchy_events().factory_leaving.add(self.factory_leaving)


    # ------------------------------------------------
    # Hierarchy events
    # ------------------------------------------------ 

    def performer_arriving(self, performer):
        print("Editor|> Performer {0} arriving".format(performer.URI().path()))

    def performer_leaving(self, performer_path):
        print("Editor|> Performer {0} leaving".format(performer_path.path()))

    def entity_arriving(self, entity):
        print("Editor|> Entity {0} arriving".format(entity.URI().path()))

    def entity_leaving(self, entity):
        print("Editor|> Entity {0} leaving".format(entity.URI().path()))

    def entity_updated(self, entity_path):
        print("Editor|> Entity {0} leaving".format(entity_path.path()))

    def factory_arriving(self, factory):
        print("Editor|> Factory {0} arriving".format(factory.URI().path()))

    def factory_leaving(self, factory_path):
        print("Editor|> Factory {0} leaving".format(factory_path.path()))

    # ------------------------------------------------


    def getNodeClassFromData(self, data):
        if 'op_code' not in data: return Node
        return get_class_from_opcode(data['op_code'])

    def doEvalOutputs(self):
        pass
        # eval all output nodes
        # for node in self.scene.nodes:
        #     if node.__class__.__name__ == "ShowtimeEditorNode_Output":
        #         node.eval()

    def onHistoryRestored(self):
        pass
        # self.doEvalOutputs()

    def fileLoad(self, filename):
        if super().fileLoad(filename):
            # self.doEvalOutputs()
            return True

        return False

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(SHOWTIME_EDITOR_NODES.keys())
        keys.sort()
        for key in keys:
            node = SHOWTIME_EDITOR_NODES[key]
            if node.creatable:
                self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
                self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        keys = [key for key in SHOWTIME_EDITOR_NODES.keys() if key in self.node_actions]
        keys.sort()
        for key in keys: context_menu.addAction(self.node_actions[key]) 
        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        self.ZST.stop()
        for callback in self._close_event_listeners: callback(self, event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                node = get_class_from_opcode(op_code)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)


            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()


    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAt(event.pos())
            if DEBUG_CONTEXT: print(item)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            #elif item is None:
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e: dumpException(e)

    def handleNodeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        markDirtyAct = context_menu.addAction("Mark Dirty")
        markDirtyDescendantsAct = context_menu.addAction("Mark Descendant Dirty")
        markInvalidAct = context_menu.addAction("Mark Invalid")
        unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        # evalAct = context_menu.addAction("Eval")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if type(item) == QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if DEBUG_CONTEXT: print("got item:", selected)
        if selected and action == markDirtyAct: selected.markDirty()
        if selected and action == markDirtyDescendantsAct: selected.markDescendantsDirty()
        if selected and action == markInvalidAct: selected.markInvalid()
        if selected and action == unmarkInvalidAct: selected.markInvalid(False)
        # if selected and action == evalAct:
        #     val = selected.eval()
        #     if DEBUG_CONTEXT: print("EVALUATED:", val)


    def handleEdgeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        squareAct = context_menu.addAction("Square Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == directAct: selected.edge_type = EDGE_TYPE_DIRECT
        if selected and action == squareAct: selected.edge_type = EDGE_TYPE_SQUARE

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_showtime_editor_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_showtime_editor_node.inputs) > 0: target_socket = new_showtime_editor_node.inputs[0]
        else:
            if len(new_showtime_editor_node.outputs) > 0: target_socket = new_showtime_editor_node.outputs[0]
        return target_socket

    def finish_new_node_state(self, new_showtime_editor_node):
        self.scene.doDeselectItems()
        new_showtime_editor_node.grNode.doSelect(True)
        new_showtime_editor_node.grNode.onSelected()


    def handleNewNodeContextMenu(self, event):

        if DEBUG_CONTEXT: print("CONTEXT: EMPTY SPACE")
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_showtime_editor_node = get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_showtime_editor_node.setPos(scene_pos.x(), scene_pos.y())
            if DEBUG_CONTEXT: print("Selected node:", new_showtime_editor_node)

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                target_socket = self.determine_target_socket_of_node(self.scene.getView().dragging.drag_start_socket.is_output, new_showtime_editor_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.grSocket)
                    self.finish_new_node_state(new_showtime_editor_node)

            else:
                self.scene.history.storeHistory("Created %s" % new_showtime_editor_node.__class__.__name__)
