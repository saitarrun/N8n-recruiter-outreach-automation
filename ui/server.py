import http.server
import socketserver
import os
import re
import json
import time
import sqlite3
import urllib.parse
import urllib.request

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = "/Users/xploit404/n8n-files"
DB_PATH = os.path.join(DIRECTORY, "leads.db")

def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        company TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        focus TEXT,
        resume_file TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        sent_at TEXT,
        created_at TEXT NOT NULL
    )
    ''')
    
    cur.execute("SELECT COUNT(*) FROM leads")
    count = cur.fetchone()[0]
    if count == 0:
        default_leads = [
            ("Stephanie", "TikTok", "stephanie.chao@tiktok.com", "large-scale distributed systems and high-throughput infrastructure", "Sai_Tarrun_Pitta_Backend_Resume.pdf", "Sent", time.strftime('%b %d, %Y %I:%M %p'), time.strftime('%Y-%m-%d %H:%M:%S')),
            ("Vivian", "ByteDance", "vivianjiang@bytedance.com", "scalable microservices and distributed platform engineering", "Sai_Tarrun_Pitta_SoftwareEngineer_Resume.pdf", "Sent", time.strftime('%b %d, %Y %I:%M %p'), time.strftime('%Y-%m-%d %H:%M:%S')),
            ("Emma", "TikTok", "emma.huo@tiktok.com", "cloud infrastructure and scalable backend services", "Sai_Tarrun_Pitta_Backend_Resume.pdf", "Sent", time.strftime('%b %d, %Y %I:%M %p'), time.strftime('%Y-%m-%d %H:%M:%S')),
            ("Isis", "ByteDance", "isis.kcano@bytedance.com", "distributed systems and backend cloud architecture", "Sai_Tarrun_Pitta_General_Resume.pdf", "Sent", time.strftime('%b %d, %Y %I:%M %p'), time.strftime('%Y-%m-%d %H:%M:%S'))
        ]
        cur.executemany('''
        INSERT OR IGNORE INTO leads (first_name, company, email, focus, resume_file, status, sent_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_leads)
        conn.commit()
    conn.close()

init_sqlite_db()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-File-Name')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # 1. Real-time n8n health check
        if parsed.path == "/api/health":
            t0 = time.time()
            try:
                req = urllib.request.Request("http://127.0.0.1:5678/healthz")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    latency_ms = round((time.time() - t0) * 1000)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok", "latency": latency_ms, "engine": "n8n"}).encode('utf-8'))
                    return
            except Exception as e:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "offline", "error": str(e)}).encode('utf-8'))
                return

        # 2. Get all persistent leads from SQLite
        elif parsed.path == "/api/leads":
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT id, first_name, company, email, focus, resume_file, status, sent_at, created_at FROM leads ORDER BY CASE WHEN status='Pending' THEN 0 ELSE 1 END, id DESC")
                rows = cur.fetchall()
                conn.close()

                leads = []
                for r in rows:
                    leads.append({
                        "id": r[0],
                        "firstName": r[1],
                        "company": r[2],
                        "email": r[3],
                        "focus": r[4] or "",
                        "resumeFile": r[5] or "Sai_Tarrun_Pitta_Backend_Resume.pdf",
                        "status": r[6],
                        "sentAt": r[7] or "",
                        "createdAt": r[8]
                    })

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"leads": leads}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        # 3. List all resumes
        elif parsed.path == "/api/resumes":
            resumes = []
            if os.path.exists(FILES_DIR):
                for f in sorted(os.listdir(FILES_DIR)):
                    if f.lower().endswith('.pdf'):
                        fp = os.path.join(FILES_DIR, f)
                        stat = os.stat(fp)
                        size_kb = round(stat.st_size / 1024, 1)
                        mod_time = time.strftime('%b %d, %Y at %I:%M %p', time.localtime(stat.st_mtime))
                        resumes.append({
                            "filename": f,
                            "path": f"/files/{f}",
                            "size": f"{size_kb} KB",
                            "lastModified": mod_time
                        })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"resumes": resumes}).encode('utf-8'))
            return

        # 4. View specific resume PDF
        elif parsed.path == "/api/resume-pdf":
            params = urllib.parse.parse_qs(parsed.query)
            target_file = params.get('file', ['Sai_Tarrun_Pitta_Resume.pdf'])[0]
            safe_filename = os.path.basename(target_file)
            fp = os.path.join(FILES_DIR, safe_filename)

            if os.path.exists(fp):
                with open(fp, "rb") as f:
                    pdf_data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'inline; filename="{safe_filename}"')
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
        parsed = urllib.parse.urlparse(self.path)
        
        # 1. Save or Add Leads to SQLite (ID-based, validated)
        if parsed.path == "/api/leads":
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            lead_list = body.get('leads', [body])

            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                now_str = time.strftime('%Y-%m-%d %H:%M:%S')

                for lead in lead_list:
                    lead_id = lead.get('id')
                    fn = lead.get('firstName', '').strip()
                    comp = lead.get('company', '').strip()
                    em = lead.get('email', '').strip()
                    focus = lead.get('focus', '')
                    res_file = lead.get('resumeFile', 'Sai_Tarrun_Pitta_Backend_Resume.pdf')
                    status = lead.get('status', 'Pending')
                    sent_at = lead.get('sentAt', '')

                    # Only process valid email addresses
                    if em and '@' in em and '.' in em:
                        if lead_id:
                            cur.execute('''
                            UPDATE leads SET first_name=?, company=?, email=?, focus=?, resume_file=?, status=?, sent_at=?
                            WHERE id=?
                            ''', (fn, comp, em, focus, res_file, status, sent_at, lead_id))
                        else:
                            cur.execute('''
                            INSERT INTO leads (first_name, company, email, focus, resume_file, status, sent_at, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(email) DO UPDATE SET
                                first_name=excluded.first_name,
                                company=excluded.company,
                                focus=excluded.focus,
                                resume_file=excluded.resume_file
                            ''', (fn, comp, em, focus, res_file, status, sent_at, now_str))

                conn.commit()
                conn.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        # 2. Delete Lead or Clear Unsent Leads from SQLite
        elif parsed.path == "/api/delete-lead":
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            lead_id = body.get('id')
            email = body.get('email')
            clear_unsent = body.get('clearUnsent', False)

            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                if clear_unsent:
                    cur.execute("DELETE FROM leads WHERE status != 'Sent'")
                elif lead_id:
                    cur.execute("DELETE FROM leads WHERE id=?", (lead_id,))
                elif email:
                    cur.execute("DELETE FROM leads WHERE email=?", (email,))
                conn.commit()
                conn.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        # 3. Mark Lead as Sent in SQLite
        elif parsed.path == "/api/mark-sent":
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            email = body.get('email')
            sent_time_str = time.strftime('%b %d, %Y %I:%M %p')

            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("UPDATE leads SET status='Sent', sent_at=? WHERE email=?", (sent_time_str, email))
                conn.commit()
                conn.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "sentAt": sent_time_str}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        # 3. Upload Resume
        elif parsed.path == "/api/upload-resume":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"success": false, "error": "Empty upload"}')
                return

            body = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            original_filename = self.headers.get('X-File-Name', 'Sai_Tarrun_Pitta_Resume.pdf')
            safe_filename = os.path.basename(original_filename)
            if not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'

            dest_path = os.path.join(FILES_DIR, safe_filename)
            os.makedirs(FILES_DIR, exist_ok=True)

            if body.startswith(b'%PDF'):
                with open(dest_path, "wb") as f:
                    f.write(body)

                file_size_kb = round(len(body) / 1024, 1)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB", "filename": "{safe_filename}"}}'.encode('utf-8'))
                print(f"[Multi-Resume] Saved {safe_filename} ({file_size_kb} KB)")
                return

            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if boundary_match:
                boundary = boundary_match.group(1).strip().strip('"').encode()
                parts = body.split(b'--' + boundary)
                for part in parts:
                    if b'filename=' in part:
                        fn_match = re.search(r'filename="([^"]+)"', part.decode('utf-8', errors='ignore'))
                        if fn_match:
                            safe_filename = os.path.basename(fn_match.group(1))

                        header_and_data = part.split(b'\r\n\r\n', 1)
                        if len(header_and_data) == 2:
                            raw_file_data = header_and_data[1]
                            if raw_file_data.endswith(b'\r\n'): raw_file_data = raw_file_data[:-2]
                            if raw_file_data.endswith(b'--'): raw_file_data = raw_file_data[:-2]
                            if raw_file_data.endswith(b'\r\n'): raw_file_data = raw_file_data[:-2]

                            dest_path = os.path.join(FILES_DIR, safe_filename)
                            with open(dest_path, "wb") as f:
                                f.write(raw_file_data)

                            file_size_kb = round(len(raw_file_data) / 1024, 1)
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(f'{{"success": true, "size": "{file_size_kb} KB", "filename": "{safe_filename}"}}'.encode('utf-8'))
                            print(f"[Multi-Resume] Saved {safe_filename} ({file_size_kb} KB)")
                            return

            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": false, "error": "Failed to parse PDF upload"}')
            return

        # 4. Delete Resume
        elif parsed.path == "/api/delete-resume":
            content_length = int(self.headers.get('Content-Length', 0))
            body_str = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body_str)
                filename = data.get('filename')
                if not filename:
                    raise ValueError("Filename missing")
                
                safe_filename = os.path.basename(filename)
                fp = os.path.join(FILES_DIR, safe_filename)
                
                if os.path.exists(fp):
                    os.remove(fp)
                    print(f"[Multi-Resume] Deleted {safe_filename}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(f'{{"success": true, "deleted": "{safe_filename}"}}'.encode('utf-8'))
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"success": false, "error": "File not found"}')
                    return
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"success": false, "error": "{str(e)}"}}'.encode('utf-8'))
                return

        # 5. Proxy Send Outreach to n8n and Auto-Record Sent in SQLite
        elif parsed.path == "/api/send-outreach":
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length)
            
            try:
                req_data = json.loads(body_bytes.decode('utf-8'))
                em = req_data.get('email')
                fn = req_data.get('firstName', '')
                comp = req_data.get('company', '')
                focus = req_data.get('focus', '')
                res_file = req_data.get('resumeFile', 'Sai_Tarrun_Pitta_Backend_Resume.pdf')

                req = urllib.request.Request(
                    "http://127.0.0.1:5678/webhook/send-recruiter-outreach",
                    data=body_bytes,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    resp_data = resp.read()
                    
                    # Update SQLite database
                    if em:
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            cur = conn.cursor()
                            sent_time_str = time.strftime('%b %d, %Y %I:%M %p')
                            now_str = time.strftime('%Y-%m-%d %H:%M:%S')
                            cur.execute('''
                            INSERT INTO leads (first_name, company, email, focus, resume_file, status, sent_at, created_at)
                            VALUES (?, ?, ?, ?, ?, 'Sent', ?, ?)
                            ON CONFLICT(email) DO UPDATE SET
                                status='Sent',
                                sent_at=?
                            ''', (fn, comp, em, focus, res_file, sent_time_str, now_str, sent_time_str))
                            conn.commit()
                            conn.close()
                        except Exception as db_err:
                            print(f"[DB Error] {db_err}")

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(resp_data)
                    return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"UI Server with Persistent SQLite Database running at http://localhost:{PORT}")
        httpd.serve_forever()
