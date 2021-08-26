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
            self.client.poll_once()
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
