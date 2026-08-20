import http.server
import socketserver
import os
import cgi

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
RESUME_DEST = "/Users/xploit404/n8n-files/Sai_Tarrun_Pitta_Resume.pdf"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == "/api/upload-resume":
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                fields = cgi.parse_multipart(self.rfile, pdict)
                file_content = fields.get('resumeFile')
                if file_content and len(file_content) > 0:
                    data = file_content[0]
                    os.makedirs(os.path.dirname(RESUME_DEST), exist_ok=True)
                    with open(RESUME_DEST, "wb") as f:
                        f.write(data)
                    
                    file_size_kb = round(len(data) / 1024, 1)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB"}}'.encode('utf-8'))
                    return
            
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": false, "error": "Invalid upload"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"UI Server with file upload running at http://localhost:{PORT}")
        httpd.serve_forever()
