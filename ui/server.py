import http.server
import socketserver
import os
import re
import json
import time
import sqlite3
import urllib.parse
import urllib.request
import base64

PORT = int(os.environ.get("PORT", 3000))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DIRECTORY)
LOCAL_FILES = os.path.join(PROJECT_ROOT, "files")
os.makedirs(LOCAL_FILES, exist_ok=True)

if os.environ.get("FILES_DIR") and os.path.exists(os.environ.get("FILES_DIR")):
    FILES_DIR = os.environ.get("FILES_DIR")
elif os.path.exists("/Users/xploit404/n8n-files"):
    FILES_DIR = "/Users/xploit404/n8n-files"
else:
    FILES_DIR = LOCAL_FILES

DB_PATH = os.path.join(DIRECTORY, "leads.db")

DEFAULT_TEMPLATES_SEED = [
    ("opportunities", "Job Inquiry", "Exploring Software Engineering Opportunities at {Company} — {SenderName}", 
     """Hi {RecruiterName},

I hope you're having a great week.

My name is **{SenderName}**, and I'm a {SenderTitle} with strong experience across **backend engineering, distributed systems, cloud infrastructure, and AI-powered workflows**.

I've been following the innovative engineering work at **{Company}** and wanted to reach out directly to inquire about current or upcoming software engineering opportunities on your team.

Previously, I've designed and scaled production microservices and cloud infrastructure at companies like **Uber, Pacific Life, Cognizant, and California State University, Fullerton**, working with **Python, Java, TypeScript, AWS, PostgreSQL, Redis, Docker, and Kubernetes**.

If there are any active or upcoming roles that align with my background, I would welcome the opportunity to connect for an introductory conversation. If another recruiter or hiring manager is handling relevant engineering teams, I'd greatly appreciate it if you could connect us or share my profile.

I've attached my resume for your reference. Thank you for your time and consideration!

Best regards,

{SignatureBlock}""", 1),

    ("applied", "Follow-Up", "Application Follow-Up: Software Engineer at {Company} — {SenderName}",
     """Hi {RecruiterName},

I hope this email finds you well.

I recently submitted my application for a **Software Engineering** role at **{Company}** and wanted to follow up with you directly to express my strong interest in the team.

As a {SenderTitle} with experience at **Uber, Pacific Life, Cognizant, and California State University, Fullerton**, I have built high-throughput backend services, distributed systems, and AI-powered pipelines using **Python, Java, TypeScript, AWS, PostgreSQL, Redis, Docker, and Kubernetes**.

Given my track record in architecting resilient microservices and shipping production-grade software, I am confident I can make an immediate positive impact at **{Company}**.

I've attached my resume here for your convenience alongside my formal application. I would love the chance to connect with you or the hiring team to discuss how my skill set aligns with your engineering goals.

Thank you so much for your time and consideration!

Best regards,

{SignatureBlock}""", 0),

    ("comprehensive", "Full Stack", "Software Engineering Opportunities at {Company} — {SenderName}",
     """Hi {RecruiterName},

I hope you're doing well.

My name is **{SenderName}**, and I'm a {SenderTitle} with experience across **backend engineering, full-stack development, distributed systems, cloud infrastructure, and AI-powered applications**.

I've previously worked with **Uber, Pacific Life, Cognizant, and California State University, Fullerton**, contributing to production systems across scalable backend services, full-stack applications, distributed systems, cloud infrastructure, AI/LLM workflows, RAG systems, and agent-based applications.

My technical background includes **Python, Java, TypeScript, JavaScript, React, FastAPI, Spring Boot, AWS, PostgreSQL, Redis, Docker, Kubernetes, LangChain, RAG, LLMs, AI Agents, APIs, microservices, and distributed systems**.

I'm currently exploring **Software Engineering opportunities at {Company}**.

If there are any current or upcoming positions that align with my background, I would greatly appreciate it if you could review my profile and consider me for the interview process.

I've attached my resume for reference. Thank you for your time and consideration.

Best regards,

{SignatureBlock}""", 0),

    ("concise", "Short", "Software Engineering Opportunities at {Company} — {SenderName}",
     """Hi {RecruiterName},

I hope you're having a great week.

I'm **{SenderName}**, a {SenderTitle} specializing in scalable backend services, distributed systems, and AI/LLM applications.

I've previously built high-performance microservices and cloud infrastructure at companies like **Uber, Pacific Life, and Cognizant** with a core stack in **Python, Java, TypeScript, AWS, Docker, Kubernetes, and PostgreSQL**.

I'm currently exploring **Software Engineering roles at {Company}** and would love to connect to discuss how my engineering background aligns with your team's upcoming hiring priorities.

I've attached my resume for reference. If there is a better person to speak with regarding engineering roles at {Company}, please let me know!

Best regards,

{SignatureBlock}""", 0),

    ("backend", "Backend", "{SenderTitle} (Backend & Distributed Systems) — {Company} | {SenderName}",
     """Hi {RecruiterName},

I hope this finds you well.

My name is **{SenderName}**, and I'm a {SenderTitle} focused on **high-throughput distributed systems, scalable backend infrastructure, and cloud data platforms**.

Across my work with **Uber, Pacific Life, and Cognizant**, I've designed resilient microservices, optimized SQL/NoSQL data pipelines, and architected cloud-native systems using **Python, Java, Spring Boot, FastAPI, AWS, Redis, Docker, and Kubernetes**.

I've been following the engineering innovations at **{Company}** and am very interested in contributing to your distributed systems and infrastructure teams.

I've attached my resume and would welcome the opportunity to connect for an interview or introduction to the relevant engineering manager.

Thank you for your time and consideration.

Best regards,

{SignatureBlock}""", 0)
]

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

    cur.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        is_default INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    cur.execute("SELECT COUNT(*) FROM templates")
    tpl_count = cur.fetchone()[0]
    if tpl_count == 0:
        cur.executemany('''
        INSERT OR IGNORE INTO templates (id, name, subject, body, is_default)
        VALUES (?, ?, ?, ?, ?)
        ''', DEFAULT_TEMPLATES_SEED)
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
                        "resumeFile": r[5] or "PittaSaiTarrun_SoftwareEngineer_Resume.pdf",
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
            seen = set()
            for d in [LOCAL_FILES, FILES_DIR, "/Users/xploit404/n8n-files"]:
                if os.path.exists(d):
                    for f in sorted(os.listdir(d)):
                        if f.lower().endswith('.pdf') and f not in seen:
                            seen.add(f)
                            fp = os.path.join(d, f)
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

        # 4. Get all templates from SQLite
        elif parsed.path == "/api/templates":
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT id, name, subject, body, is_default, updated_at FROM templates ORDER BY is_default DESC, id ASC")
                rows = cur.fetchall()
                conn.close()

                templates = []
                for r in rows:
                    templates.append({
                        "id": r[0],
                        "name": r[1],
                        "subject": r[2],
                        "body": r[3],
                        "isDefault": bool(r[4]),
                        "updatedAt": r[5]
                    })

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"templates": templates}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        # 4. View specific resume PDF
        elif parsed.path == "/api/resume-pdf":
            params = urllib.parse.parse_qs(parsed.query)
            target_file = params.get('file', ['PittaSaiTarrun_SoftwareEngineer_Resume.pdf'])[0]
            safe_filename = os.path.basename(target_file)
            
            found_fp = None
            for d in [LOCAL_FILES, FILES_DIR, "/Users/xploit404/n8n-files"]:
                fp = os.path.join(d, safe_filename)
                if os.path.exists(fp):
                    found_fp = fp
                    break

            if found_fp and os.path.exists(found_fp):
                with open(found_fp, "rb") as f:
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
                    res_file = lead.get('resumeFile') or 'PittaSaiTarrun_SoftwareEngineer_Resume.pdf'
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
                                resume_file=excluded.resume_file,
                                status=excluded.status,
                                sent_at=CASE WHEN excluded.status='Pending' THEN '' ELSE leads.sent_at END
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

        # 2. Delete Lead or Clear Unsent Leads from SQLite (supports single, batch ids, batch emails, and clearUnsent)
        elif parsed.path == "/api/delete-lead":
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            lead_id = body.get('id')
            email = body.get('email')
            lead_ids = body.get('ids', [])
            emails = body.get('emails', [])
            clear_unsent = body.get('clearUnsent', False)

            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                if clear_unsent:
                    cur.execute("DELETE FROM leads WHERE status != 'Sent'")
                elif lead_ids:
                    placeholders = ','.join('?' for _ in lead_ids)
                    cur.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", tuple(lead_ids))
                elif emails:
                    placeholders = ','.join('?' for _ in emails)
                    cur.execute(f"DELETE FROM leads WHERE email IN ({placeholders})", tuple(emails))
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

        # 3. Save or Update Template in SQLite
        elif parsed.path == "/api/templates":
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            tpl_id = body.get('id', '').strip()
            name = body.get('name', '').strip()
            subject = body.get('subject', '').strip()
            tpl_body = body.get('body', '').strip()
            is_default = 1 if body.get('isDefault') else 0

            if not tpl_id:
                tpl_id = name.lower().replace(' ', '_')[:32] or f"tpl_{int(time.time())}"

            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                now_str = time.strftime('%Y-%m-%d %H:%M:%S')
                cur.execute('''
                INSERT INTO templates (id, name, subject, body, is_default, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    subject=excluded.subject,
                    body=excluded.body,
                    is_default=excluded.is_default,
                    updated_at=excluded.updated_at
                ''', (tpl_id, name, subject, tpl_body, is_default, now_str))
                conn.commit()
                conn.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "id": tpl_id}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
                return

        # 4. Delete Template from SQLite
        elif parsed.path == "/api/delete-template":
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            tpl_id = body.get('id')

            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                if tpl_id:
                    cur.execute("DELETE FROM templates WHERE id=?", (tpl_id,))
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

        # 5. Reset Templates in SQLite to System Defaults
        elif parsed.path == "/api/reset-templates":
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM templates")
                cur.executemany('''
                INSERT INTO templates (id, name, subject, body, is_default)
                VALUES (?, ?, ?, ?, ?)
                ''', DEFAULT_TEMPLATES_SEED)
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

        # 6. Mark Lead as Sent in SQLite
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
                for target_dir in [LOCAL_FILES, FILES_DIR, "/Users/xploit404/n8n-files"]:
                    if os.path.exists(target_dir):
                        with open(os.path.join(target_dir, safe_filename), "wb") as f:
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

                            for target_dir in [LOCAL_FILES, FILES_DIR, "/Users/xploit404/n8n-files"]:
                                if os.path.exists(target_dir):
                                    with open(os.path.join(target_dir, safe_filename), "wb") as f:
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
                
                deleted = False
                for target_dir in [LOCAL_FILES, FILES_DIR, "/Users/xploit404/n8n-files"]:
                    fp = os.path.join(target_dir, safe_filename)
                    if os.path.exists(fp):
                        try:
                            os.remove(fp)
                            deleted = True
                        except Exception as e:
                            print(f"[Delete err] {e}")

                if deleted:
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

                # Locate and attach resume binary in base64
                if res_file:
                    safe_res_name = os.path.basename(res_file)
                    possible_paths = [
                        os.path.join(FILES_DIR, safe_res_name),
                        os.path.join(LOCAL_FILES, safe_res_name),
                        os.path.join("/Users/xploit404/n8n-files", safe_res_name)
                    ]
                    for p in possible_paths:
                        if os.path.exists(p):
                            try:
                                with open(p, "rb") as rf:
                                    req_data['resumeBase64'] = base64.b64encode(rf.read()).decode('utf-8')
                                req_data['resumeFileName'] = safe_res_name
                                break
                            except Exception as read_err:
                                print(f"[Resume Read Err] {read_err}")

                # If requested file wasn't found, attach first available PDF from library
                if not req_data.get('resumeBase64'):
                    for d in [FILES_DIR, LOCAL_FILES, "/Users/xploit404/n8n-files"]:
                        if os.path.exists(d):
                            pdfs = [f for f in sorted(os.listdir(d)) if f.lower().endswith('.pdf')]
                            if pdfs:
                                fallback_path = os.path.join(d, pdfs[0])
                                try:
                                    with open(fallback_path, "rb") as rf:
                                        req_data['resumeBase64'] = base64.b64encode(rf.read()).decode('utf-8')
                                    req_data['resumeFileName'] = pdfs[0]
                                    break
                                except Exception as fallback_err:
                                    print(f"[Resume Fallback Err] {fallback_err}")

                forward_bytes = json.dumps(req_data).encode('utf-8')

                req = urllib.request.Request(
                    "http://127.0.0.1:5678/webhook/send-recruiter-outreach",
                    data=forward_bytes,
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
                            actual_res_file = req_data.get('resumeFileName') or res_file or 'PittaSaiTarrun_SoftwareEngineer_Resume.pdf'
                            cur.execute('''
                            INSERT INTO leads (first_name, company, email, focus, resume_file, status, sent_at, created_at)
                            VALUES (?, ?, ?, ?, ?, 'Sent', ?, ?)
                            ON CONFLICT(email) DO UPDATE SET
                                resume_file=?,
                                status='Sent',
                                sent_at=?
                            ''', (fn, comp, em, focus, actual_res_file, sent_time_str, now_str, actual_res_file, sent_time_str))
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
    try:
        from http.server import ThreadingHTTPServer
        server_class = ThreadingHTTPServer
    except ImportError:
        class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            daemon_threads = True
        server_class = ThreadedTCPServer

    server_class.allow_reuse_address = True
    with server_class(("", PORT), CustomHandler) as httpd:
        print(f"Multi-Threaded UI Server with Persistent SQLite Database running at http://localhost:{PORT}")
        httpd.serve_forever()
