import os
import http.server
import socketserver

PORT = 8000
DIRECTORY = "./image/scene"


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        if self.path.endswith((".png", ".jpg", ".jpeg", ".gif")):
            file_path = os.path.join(DIRECTORY, self.path.strip("/"))
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.send_header("Content-Length", str(file_size))
        super().end_headers()


def start():
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving in http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    start()
