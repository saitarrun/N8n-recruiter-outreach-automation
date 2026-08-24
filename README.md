<div align="center">

# 🚀 Recruiter Outreach Platform & Automation Engine

An autonomous, full-stack cold email outreach and recruiter relationship automation platform powered by **n8n**, an **Apple HIG UI Studio**, an **Automated Outreach Scheduler**, and a **Persistent Local SQLite Database**.

[![GitHub Release](https://img.shields.io/badge/Release-v2.0-blue.svg?style=flat-square)](#)
[![macOS 1-Click](https://img.shields.io/badge/macOS-Apple%20Silicon%20Native-black.svg?logo=apple&style=flat-square)](#)
[![Windows 1-Click](https://img.shields.io/badge/Windows-1--Click%20Ready-0078D6.svg?logo=windows&style=flat-square)](#)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white&style=flat-square)](#)
[![Automated Tests](https://img.shields.io/badge/Tests-18%2F18%20Passing-10b981.svg?style=flat-square)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

<br/>

![UI Studio Demo](assets/ui_studio_demo.png)

</div>

---

## ⚡ 1-Command Turnkey Installation (macOS, Windows, Linux)

Run the entire platform locally (n8n Engine + UI Studio + SQLite Storage + Desktop Launcher) in under 60 seconds with **zero configuration**:

### 1. Clone the Repository
```bash
git clone https://github.com/saitarrun/n8n-recruiter-outreach-automation.git
cd n8n-recruiter-outreach-automation
```

### 2. Launch on Your Operating System

* **🍎 macOS**:
  ```bash
  ./start.sh
  ```
  *(Or double-click **`start.command`** — automatically creates the native **`Recruiter Outreach.app`** on your Desktop with high-res Apple icon!)*

* **🪟 Windows**:
  Double-click **`start.bat`** *(automatically creates a **`Recruiter Outreach`** shortcut on your Windows Desktop with the `.ico` icon!)*

* **🐳 Docker Compose** (Any OS):
  ```bash
  docker compose up -d
  ```

### 3. Open the Apps
* **🖥️ Outreach UI Studio**: [http://localhost:3000](http://localhost:3000)
* **⚙️ n8n Automation Engine**: [http://localhost:5678](http://localhost:5678)

---

## 📸 Visual Usage Workflow & Features

### 1. Interactive WYSIWYG Outreach Studio
Compose and customize cold outreach in real time. Modifying the recruiter's **First Name**, **Company**, or **Email** dynamically updates the salutation, subject line, custom focus paragraphs, and header metadata instantly.

![UI Studio](assets/ui_studio_demo.png)

---

### 2. ⏱️ Automated Outreach Scheduler Studio
Schedule and throttle outreach campaigns with zero database modifications:
* **Delayed Batch Launch**: Schedule a batch of unsent leads to launch at an exact date & time with live digital countdown.
* **Smart Drip Sender**: Dispatches 1 email every $N$ minutes with organic **Human Jitter ($\pm 30\text{s}$)** to protect your Gmail reputation.
* **Daily Business Hours Autopilot**: Automatically triggers outreach on weekdays during peak reply windows (e.g., Mon–Fri at 9:15 AM).
* **Live Execution Monitor**: Monospaced terminal log and upcoming scheduled queue preview.

---

### 3. 📑 Bulk Lead Ingestion (Excel, CSV, & Word Documents)
Drag and drop any `.xlsx`, `.xls`, `.csv`, `.docx`, or `.txt` document onto the **Bulk Import** tab. The platform automatically detects column headers (`Name`, `Company`, `Email`, `Focus/Role`), renders an in-browser staged preview, and imports all leads into the persistent SQLite database.

![Bulk Document Import](assets/bulk_import_demo.png)

---

### 4. 📄 Multi-Resume PDF Library & Apple Quick Look
Upload and manage multiple resume variants (e.g., *Backend*, *Full-Stack*, *AI/ML*). Preview them in-app using Apple Quick Look and dynamically attach specific resume versions to individual recruiters or batches.

---

### 5. ⚙️ n8n Autonomous Workflow Engine
The backend workflow handles Base64 binary resume attachment resolution, dynamic email payload construction, and Gmail API dispatch with exponential backoff and rate limiting.

![n8n Workflow](assets/n8n_workflow_demo.png)

---

## 🔑 One-Time Gmail OAuth Setup (2 Minutes)

To send emails through your personal Gmail account:

### Step 1: Create OAuth Credentials in Google Cloud Console
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Recruiter Outreach`).
3. Enable the **Gmail API**.
4. Go to **APIs & Services** $\rightarrow$ **OAuth consent screen**:
   * Set User Type to **External** $\rightarrow$ Add your email address under Test Users.
5. Go to **Credentials** $\rightarrow$ **Create Credentials** $\rightarrow$ **OAuth client ID**:
   * Application type: **Web application**
   * Name: `n8n Gmail Integration`
   * Authorized Redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
6. Copy your **Client ID** and **Client Secret**.

### Step 2: Connect in n8n
1. Open **[http://localhost:5678](http://localhost:5678)**.
2. Navigate to **Credentials** $\rightarrow$ **Add Credential** $\rightarrow$ Search for **Gmail OAuth2**.
3. Paste your **Client ID** and **Client Secret**, click **Connect my account**, and approve permissions.
4. Save the credential as `Gmail OAuth2 account`.

---

## 🛠️ CLI & Platform Management Commands

| Action | macOS / Linux | Windows |
| :--- | :--- | :--- |
| **Start Platform** | `./start.sh` or `start.command` | `start.bat` |
| **Stop Services** | `./stop.sh` | `stop.bat` |
| **Restart Platform** | `./restart.sh` | `restart.bat` |
| **Check System Status** | `./status.sh` | `status.bat` |
| **Run Automated Tests** | `./tests/run_tests.sh` | `python tests\test_platform.py` |
| **Install macOS Auto-Start** | `./scripts/install-autostart.sh` | — |

---

## 🧪 Automated Test Suite (18 Tests)

The repository includes a complete automated test suite covering backend endpoints, n8n webhook registration, SQLite persistence, and client logic:

```bash
./tests/run_tests.sh
```

```
==========================================================
   🧪 Recruiter Outreach Platform — Automated Test Suite  
==========================================================
1. Running Backend & Integration Test Suite (Python)...
   ✓ Node runtime v22 LTS verification
   ✓ Apple Silicon ARM64 native Python
   ✓ n8n SQLite database & workflow active verification
   ✓ Gmail OAuth2 credentials check
   ✓ Webhook route registration in database
   ✓ /api/health endpoint status & latency
   ✓ Leads CRUD & SQLite persistence lifecycle
   ✓ Binary PDF Upload, Quick Look stream, & Deletion
   ✓ End-to-end outreach email dispatch with attachment
   ✓ Desktop App bundle & permissions integrity
   ✓ Shell scripts executable permissions

2. Running Client-Side Parser & Logic Test Suite (Node.js)...
   ✓ Dynamic Token Substitution ({RecruiterName}, {Company})
   ✓ Subject Template Interpolation
   ✓ User Edits Auto-Tokenization
   ✓ Raw Document & Clipboard Lead Parsing
   ✓ Scheduler Queue Slicing & Sent-Exclusion
   ✓ Scheduler Recurring Time Calculation
   ✓ Scheduler Drip Interval & Jitter Logic

==========================================================
   🎉 ALL 18 PLATFORM & SCHEDULER TESTS PASSED!           
==========================================================
```

---

## 📁 Repository Structure

```
n8n-recruiter-outreach-automation/
├── ui/
│   ├── index.html         # Apple HIG Outreach Studio UI + Scheduler
│   ├── server.py          # Python server, SQLite database, & n8n proxy
│   └── leads.db           # Persistent local SQLite database
├── workflows/
│   ├── direct_recruiter_outreach_batch_workflow.json  # Direct email sender
│   ├── recruiter_outreach_orchestrator.json           # Automated daily runner
│   └── recruiter_reply_followup_tracker.json         # Follow-up tracker
├── assets/
│   ├── AppIcon.icns       # Native macOS application icon
│   ├── app_icon.ico       # Native Windows desktop icon
│   ├── app_icon_1024.png  # High-resolution master icon
│   └── ui_studio_demo.png # UI preview assets
├── scripts/
│   ├── create-desktop-app.sh      # macOS .app bundle generator
│   ├── create-windows-shortcut.bat # Windows desktop shortcut generator
│   ├── install-autostart.sh       # macOS LaunchAgent auto-start installer
│   └── uninstall-autostart.sh     # macOS LaunchAgent uninstaller
├── tests/
│   ├── run_tests.sh       # 1-Command test runner
│   ├── test_platform.py   # Python backend & integration test suite
│   └── test_client_logic.js # JavaScript parser & scheduler test suite
├── files/                 # Resume PDF storage directory
├── start.sh / start.bat   # 1-Click startup scripts (Mac / Windows)
├── stop.sh / stop.bat     # 1-Click shutdown scripts
├── restart.sh / restart.bat # 1-Click restart scripts
├── status.sh / status.bat # 1-Click diagnostic status dashboards
├── docker-compose.yml     # Container orchestration
└── README.md
```

---

## 📄 License
Distributed under the **MIT License**. Free and open for developers, job seekers, and recruiters to customize.
