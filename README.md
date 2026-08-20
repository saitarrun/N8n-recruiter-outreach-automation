# Recruiter Outreach Platform & Automation Engine

An autonomous, end-to-end recruitment outreach and cold email platform powered by **n8n** and an **Apple-inspired UI Studio**.

Features live WYSIWYG email composing, real-time personalization, bulk Excel/Word lead parsing, dynamic resume PDF attachments, and automated anti-spam deliverability spacing.

---

## ⚡ 3-Minute Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/saitarrun/n8n-recruiter-outreach-automation.git
cd n8n-recruiter-outreach-automation
```

### 2. Start the Platform
Run the turnkey startup script:
```bash
./start.sh
```
*Or using Docker Compose directly:*
```bash
docker compose up -d
```

### 3. Open the Applications
* **🖥️ Outreach UI Studio**: [http://localhost:3000](http://localhost:3000)
* **⚙️ n8n Automation Engine**: [http://localhost:5678](http://localhost:5678)

---

## 🔑 One-Time API & Gmail Setup

To send emails through your own Gmail account:

### Step 1: Create OAuth Credentials in Google Cloud
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Recruiter Outreach`).
3. Enable the **Gmail API** (and optionally **Google Sheets API** if using Google Sheets tracking).
4. Navigate to **APIs & Services** $\rightarrow$ **OAuth consent screen**:
   * User Type: **External** $\rightarrow$ Add your email address as a Test User.
5. Navigate to **Credentials** $\rightarrow$ **Create Credentials** $\rightarrow$ **OAuth client ID**:
   * Application type: **Web application**
   * Name: `n8n Integration`
   * Authorized Redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
6. Copy your **Client ID** and **Client Secret**.

### Step 2: Connect in n8n
1. Open **[http://localhost:5678](http://localhost:5678)**.
2. Go to **Credentials** $\rightarrow$ **Add Credential** $\rightarrow$ Search for **Gmail OAuth2**.
3. Paste your **Client ID** and **Client Secret**, click **Connect my account**, and approve permissions.
4. Save the credential as `Gmail OAuth2 account`.

---

## 🖥️ UI Studio Features

### 1. Direct WYSIWYG Inline Compose
* Type directly inside the email body or subject line.
* Changing First Name or Company immediately updates both the subject line and every mention in the email body in real time.

### 2. Excel (.xlsx, .csv) & Word (.docx) Bulk Import
* Drag & drop any `.xlsx`, `.xls`, `.csv`, or `.docx` document onto the **Bulk Import** tab.
* Automatic column header recognition (`Name`, `Company`, `Email`, `Focus/Role`).
* 1-click import directly into your **Unsent** leads queue.

### 3. Safe Bulk Dispatching
* **`Send Unsent in Bulk`** exclusively loops through pending leads with a 4-second anti-spam spacing.
* Sent leads automatically receive a `Sent` badge and are protected in **Sent History** so they are never accidentally emailed twice.

### 4. Resume Variant Manager & Quick Look
* Upload and switch between multiple resume variants (e.g. *Backend*, *Software Engineer*, *General*).
* Preview attachments directly in the browser via the built-in **Quick Look** modal.

### 5. Real-Time Engine Health
* Displays a live header status badge (`n8n Active • 2ms`) with automatic latency heartbeat monitoring.

---

## 📁 Repository Structure

```
n8n-recruiter-outreach-automation/
├── ui/
│   ├── index.html         # Apple HIG Outreach Studio UI
│   └── server.py          # Local web server & n8n relay proxy
├── workflows/
│   ├── direct_recruiter_outreach_batch_workflow.json  # Webhook email sender
│   ├── recruiter_outreach_orchestrator.json           # Daily automated runner
│   └── recruiter_reply_followup_tracker.json         # Follow-up tracker
├── files/                 # Persistent resume PDF storage directory
├── sample_recruiter_leads.csv    # Sample test CSV file
├── sample_recruiter_leads.docx   # Sample test Word document
├── docker-compose.yml     # Complete Docker container orchestration
├── start.sh               # Turnkey 1-command startup script
└── README.md
```

---

## 🛡️ License & Attribution
Distributed under the MIT License. Commits and setup scripts are fully open-source and modular for any job seeker or recruitment team.
