import atexit, threading, time
import showtime.showtime as ZST

DEFAULT_CLIENT_NAME = "ShowtimeNodeEditor"

class EventLoop(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.setDaemon(True)
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            self.client.poll_once(False)
            time.sleep(0.001)

class ShowtimeEditorClient:
    def __init__(self):
        self.client = None
        self.client_loop = None
        atexit.register(self.stop)

    def create_client(self, name=DEFAULT_CLIENT_NAME):
        self.client = ZST.ShowtimeClient()
        self.client.init(name, True)
        self.client_loop = EventLoop(self.client)
        self.client_loop.start()

    # def start(self):
    #     try:
    #         while 1:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         print("\nExiting...")

    def stop(self):
        self.client_loop.stop()
        self.client.leave()
        self.client.destroy()


def cast_entity_to_natural_type(entity):
    if entity.entity_type() == ZST.ZstEntityType_PERFORMER:
        print("Casting to performer")
        return ZST.cast_to_performer(entity)
    elif entity.entity_type() == ZST.ZstEntityType_COMPONENT:
        print("Casting to component")
        return ZST.cast_to_component(entity)
    elif entity.entity_type() == ZST.ZstEntityType_FACTORY:
        print("Casting to factory")
        return ZST.cast_to_factory(entity)
    elif entity.entity_type() == ZST.ZstEntityType_PLUG:
        print("Casting to plug")
        plug = ZST.cast_to_plug(entity)
        if plug.direction() == ZST.ZstPlugDirection_IN_JACK:
            print("Casting to input plug")
            return ZST.cast_to_input_plug(entity)
        else:
            print("Casting to output plug")
            return ZST.cast_to_output_plug(entity)
    
    return entity