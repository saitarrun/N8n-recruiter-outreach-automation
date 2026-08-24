import unittest
import urllib.request
import urllib.parse
import json
import os
import sqlite3
import subprocess
import time

BASE_UI_URL = "http://localhost:3000"
BASE_N8N_URL = "http://localhost:5678"
PROJECT_ROOT = "/Users/xploit404/Projects/n8n-recruiter-outreach-automation"

class TestRecruiterOutreachPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure servers are online before running tests"""
        # Quick health ping
        try:
            req = urllib.request.Request(f"{BASE_UI_URL}/api/health")
            with urllib.request.urlopen(req, timeout=3) as resp:
                cls.ui_online = (resp.getcode() == 200)
        except Exception:
            cls.ui_online = False

    # ==========================================================
    # 1. Environment & Architecture Tests
    # ==========================================================
    def test_01_node_version(self):
        """Test that Node runtime is v22 LTS"""
        res = subprocess.run(["node", "-v"], capture_output=True, text=True, env=dict(os.environ, PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:" + os.environ.get("PATH", "")))
        self.assertEqual(res.returncode, 0)
        self.assertTrue(res.stdout.strip().startswith("v22"), f"Expected Node v22, got {res.stdout.strip()}")

    def test_02_python_arm64_native(self):
        """Test that Python runtime is native Apple Silicon ARM64"""
        py_bin = "/opt/homebrew/bin/python3" if os.path.exists("/opt/homebrew/bin/python3") else "python3"
        res = subprocess.run(["file", py_bin], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("arm64", res.stdout, "Python should be native arm64")

    # ==========================================================
    # 2. n8n Database & Credentials Verification
    # ==========================================================
    def test_03_n8n_database_exists(self):
        """Test n8n SQLite database and workflow table exist"""
        db_path = os.path.expanduser("~/.n8n/database.sqlite")
        self.assertTrue(os.path.exists(db_path), "n8n database.sqlite must exist")
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, name, active FROM workflow_entity WHERE id='T5xzFPEkCQ3vjclr'")
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row, "Direct Recruiter Outreach Sender workflow must exist")
        self.assertEqual(row[2], 1, "Workflow must be marked Active (1)")

    def test_04_n8n_gmail_oauth_credential(self):
        """Test Gmail OAuth2 credential exists in n8n database"""
        db_path = os.path.expanduser("~/.n8n/database.sqlite")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, name, type FROM credentials_entity WHERE type='gmailOAuth2'")
        rows = cur.fetchall()
        conn.close()

        self.assertGreaterEqual(len(rows), 1, "Gmail OAuth2 credentials must be registered in n8n")
        self.assertEqual(rows[0][1], "Gmail OAuth2 account")

    def test_05_n8n_webhook_registered(self):
        """Test send-recruiter-outreach webhook is registered in SQLite"""
        db_path = os.path.expanduser("~/.n8n/database.sqlite")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT workflowId, webhookPath, method FROM webhook_entity WHERE webhookPath='send-recruiter-outreach'")
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row, "Webhook 'send-recruiter-outreach' must be registered in webhook_entity")
        self.assertEqual(row[2], "POST")

    # ==========================================================
    # 3. Outreach Studio API Tests
    # ==========================================================
    def test_06_ui_health_endpoint(self):
        """Test /api/health endpoint returns 200 OK and connected status"""
        req = urllib.request.Request(f"{BASE_UI_URL}/api/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode())
            self.assertEqual(data.get("status"), "ok")
            self.assertEqual(data.get("engine"), "n8n")

    def test_07_leads_crud_lifecycle(self):
        """Test Lead Insertion, Querying, Mark Sent, and Deletion"""
        test_email = f"audit.lead.{int(time.time())}@example.com"
        test_lead = {
            "firstName": "TestRecruiter",
            "company": "AuditCorp",
            "email": test_email,
            "focus": "FullStack",
            "status": "Pending"
        }

        # 1. Insert lead
        req = urllib.request.Request(f"{BASE_UI_URL}/api/leads", method="POST")
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(test_lead).encode()
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode())
            self.assertTrue(res_data.get("success"))

        # 2. Query leads to verify persistence
        req = urllib.request.Request(f"{BASE_UI_URL}/api/leads")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode())
            leads_list = data.get("leads", data) if isinstance(data, dict) else data
            found = next((l for l in leads_list if l.get("email") == test_email), None)
            self.assertIsNotNone(found, "Inserted lead must be retrieved from database")
            self.assertEqual(found["company"], "AuditCorp")
            self.assertEqual(found["status"], "Pending")

        # 3. Mark as Sent
        req = urllib.request.Request(f"{BASE_UI_URL}/api/mark-sent", method="POST")
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps({"email": test_email}).encode()
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode())
            self.assertTrue(res_data.get("success"))

        # 4. Delete lead
        req = urllib.request.Request(f"{BASE_UI_URL}/api/delete-lead", method="POST")
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps({"email": test_email}).encode()
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode())
            self.assertTrue(res_data.get("success"))

    def test_08_resume_upload_view_and_delete_lifecycle(self):
        """Test uploading a binary PDF, streaming it back, and deleting it"""
        test_filename = f"UnitTest_Resume_{int(time.time())}.pdf"
        dummy_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"

        # 1. Upload
        req = urllib.request.Request(f"{BASE_UI_URL}/api/upload-resume", method="POST", data=dummy_pdf_bytes)
        req.add_header("Content-Type", "application/pdf")
        req.add_header("X-File-Name", test_filename)
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode())
            self.assertTrue(res_data.get("success"))

        # 2. View PDF
        req = urllib.request.Request(f"{BASE_UI_URL}/api/resume-pdf?file={test_filename}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            self.assertEqual(resp.headers.get("Content-Type"), "application/pdf")
            self.assertEqual(resp.read(), dummy_pdf_bytes)

        # 3. Delete
        req = urllib.request.Request(f"{BASE_UI_URL}/api/delete-resume", method="POST")
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps({"filename": test_filename}).encode()
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode())
            self.assertTrue(res_data.get("success"))

    # ==========================================================
    # 4. End-to-End Outreach Email Dispatch Test
    # ==========================================================
    def test_09_end_to_end_outreach_send(self):
        """Test complete outreach email pipeline with binary PDF attachment"""
        payload = {
            "firstName": "TestRunner",
            "company": "AutomatedTestCo",
            "email": "saitarrunpitta@gmail.com",
            "customSubject": f"Automated Suite Test {int(time.time())} — Sai Tarrun Pitta",
            "customHtml": "<!DOCTYPE html><html><body><p>Automated Unit Test Verification</p></body></html>",
            "resumeFile": "PittaSaiTarrun_SoftwareEngineer_Resume.pdf"
        }

        req = urllib.request.Request(f"{BASE_UI_URL}/api/send-outreach", method="POST")
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(payload).encode()

        with urllib.request.urlopen(req, timeout=15) as resp:
            self.assertEqual(resp.getcode(), 200)
            res_data = json.loads(resp.read().decode())
            self.assertTrue("id" in res_data or "threadId" in res_data or res_data.get("success") is not False)

    # ==========================================================
    # 5. Desktop Application Bundle & Launcher Integrity
    # ==========================================================
    def test_10_desktop_app_bundle_integrity(self):
        """Test that Desktop App bundle and executable launcher exist and have executable permissions"""
        desktop_app = os.path.expanduser("~/Desktop/Recruiter Outreach.app")
        launcher_bin = os.path.join(desktop_app, "Contents", "MacOS", "applet")
        if not os.path.exists(launcher_bin):
            launcher_bin = os.path.join(desktop_app, "Contents", "MacOS", "app_launcher")
        plist = os.path.join(desktop_app, "Contents", "Info.plist")

        self.assertTrue(os.path.exists(desktop_app), "Desktop application must exist")
        self.assertTrue(os.path.exists(launcher_bin), "App executable binary must exist")
        self.assertTrue(os.path.exists(plist), "Info.plist must exist")
        self.assertTrue(os.access(launcher_bin, os.X_OK), "app executable must be executable (chmod +x)")

    def test_11_shell_scripts_executable(self):
        """Test all repository lifecycle shell scripts are executable"""
        scripts = ["start.sh", "stop.sh", "restart.sh", "status.sh", "start.command", "update.sh"]
        for s in scripts:
            sp = os.path.join(PROJECT_ROOT, s)
            self.assertTrue(os.path.exists(sp), f"{s} must exist")
            self.assertTrue(os.access(sp, os.X_OK), f"{s} must be executable")

if __name__ == "__main__":
    unittest.main(verbosity=2)
