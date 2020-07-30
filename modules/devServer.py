import socketserver
import http.server

from functools import partial

from . import Module


class DevelopmentServer(Module):
    def __init__(self, host, port):
        self.host, self.port = host, port

    def server_thread(self, direc):
        handler = partial(
            http.server.SimpleHTTPRequestHandler, directory=direc
        )

        with socketserver.TCPServer((self.host, self.port), handler) as http_daemon:
            self.log(
                f"Local development server running on {self.host}:{self.port}")
            self.error(" !  This server is not suitable for production!")
            http_daemon.serve_forever()

    def run(self, render):
        import threading
        threading.Thread(target=self.server_thread, args=(
            render.dest, ), daemon=True).start()
