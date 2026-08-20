import http.server
import socketserver
import os
import re

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
RESUME_DEST = "/Users/xploit404/n8n-files/Sai_Tarrun_Pitta_Resume.pdf"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == "/api/upload-resume":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"success": false, "error": "Empty upload"}')
                return

            body = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            
            # If raw binary PDF
            if body.startswith(b'%PDF'):
                os.makedirs(os.path.dirname(RESUME_DEST), exist_ok=True)
                with open(RESUME_DEST, "wb") as f:
                    f.write(body)
                file_size_kb = round(len(body) / 1024, 1)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB"}}'.encode('utf-8'))
                return

            # If multipart/form-data
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if boundary_match:
                boundary = boundary_match.group(1).strip().strip('"').encode()
                parts = body.split(b'--' + boundary)
                for part in parts:
                    if b'filename=' in part:
                        header_and_data = part.split(b'\r\n\r\n', 1)
                        if len(header_and_data) == 2:
                            raw_file_data = header_and_data[1]
                            # Trim trailing \r\n
                            if raw_file_data.endswith(b'\r\n'):
                                raw_file_data = raw_file_data[:-2]
                            if raw_file_data.endswith(b'--'):
                                raw_file_data = raw_file_data[:-2]
                            if raw_file_data.endswith(b'\r\n'):
                                raw_file_data = raw_file_data[:-2]

                            os.makedirs(os.path.dirname(RESUME_DEST), exist_ok=True)
                            with open(RESUME_DEST, "wb") as f:
                                f.write(raw_file_data)

                            file_size_kb = round(len(raw_file_data) / 1024, 1)
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB"}}'.encode('utf-8'))
                            print(f"[Upload Server] Successfully wrote {file_size_kb} KB to {RESUME_DEST}")
                            return

            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": false, "error": "Failed to parse PDF upload"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"UI Server with robust file upload running at http://localhost:{PORT}")
        httpd.serve_forever()
