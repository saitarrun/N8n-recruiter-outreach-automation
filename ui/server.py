import http.server
import socketserver
import os
import re
import json
import time

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
RESUME_DEST = "/Users/xploit404/n8n-files/Sai_Tarrun_Pitta_Resume.pdf"
META_FILE = "/Users/xploit404/n8n-files/resume_meta.json"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Prevent any aggressive browser caching so edits and uploads reflect instantly
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/resume-info":
            if os.path.exists(RESUME_DEST):
                stat = os.stat(RESUME_DEST)
                size_kb = round(stat.st_size / 1024, 1)
                mod_time = time.strftime('%b %d, %Y at %I:%M %p', time.localtime(stat.st_mtime))
                
                original_name = "Sai_Tarrun_Pitta_Resume.pdf"
                if os.path.exists(META_FILE):
                    try:
                        with open(META_FILE, "r") as mf:
                            meta = json.load(mf)
                            original_name = meta.get("originalName", original_name)
                    except Exception:
                        pass
                
                res = {
                    "exists": True,
                    "filename": original_name,
                    "size": f"{size_kb} KB",
                    "lastModified": mod_time
                }
            else:
                res = {"exists": False}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return

        elif self.path.startswith("/api/resume-pdf"):
            if os.path.exists(RESUME_DEST):
                with open(RESUME_DEST, "rb") as f:
                    pdf_data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', 'inline; filename="Sai_Tarrun_Pitta_Resume.pdf"')
                self.send_header('Content-Length', str(len(pdf_data)))
                self.end_headers()
                self.wfile.write(pdf_data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        super().do_GET()

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
            original_filename = self.headers.get('X-File-Name', 'Sai_Tarrun_Pitta_Resume.pdf')
            
            # If raw binary PDF
            if body.startswith(b'%PDF'):
                os.makedirs(os.path.dirname(RESUME_DEST), exist_ok=True)
                with open(RESUME_DEST, "wb") as f:
                    f.write(body)
                
                with open(META_FILE, "w") as mf:
                    json.dump({"originalName": original_filename, "updatedAt": time.time()}, mf)

                file_size_kb = round(len(body) / 1024, 1)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB", "filename": "{original_filename}"}}'.encode('utf-8'))
                return

            # If multipart/form-data
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if boundary_match:
                boundary = boundary_match.group(1).strip().strip('"').encode()
                parts = body.split(b'--' + boundary)
                for part in parts:
                    if b'filename=' in part:
                        fn_match = re.search(r'filename="([^"]+)"', part.decode('utf-8', errors='ignore'))
                        if fn_match:
                            original_filename = fn_match.group(1)

                        header_and_data = part.split(b'\r\n\r\n', 1)
                        if len(header_and_data) == 2:
                            raw_file_data = header_and_data[1]
                            if raw_file_data.endswith(b'\r\n'):
                                raw_file_data = raw_file_data[:-2]
                            if raw_file_data.endswith(b'--'):
                                raw_file_data = raw_file_data[:-2]
                            if raw_file_data.endswith(b'\r\n'):
                                raw_file_data = raw_file_data[:-2]

                            os.makedirs(os.path.dirname(RESUME_DEST), exist_ok=True)
                            with open(RESUME_DEST, "wb") as f:
                                f.write(raw_file_data)

                            with open(META_FILE, "w") as mf:
                                json.dump({"originalName": original_filename, "updatedAt": time.time()}, mf)

                            file_size_kb = round(len(raw_file_data) / 1024, 1)
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB", "filename": "{original_filename}"}}'.encode('utf-8'))
                            print(f"[Upload Server] Successfully wrote {file_size_kb} KB ({original_filename}) to {RESUME_DEST}")
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
        print(f"UI Server running at http://localhost:{PORT}")
        httpd.serve_forever()
