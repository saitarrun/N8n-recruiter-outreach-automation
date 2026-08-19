# 🚀 Production Recruiter Outreach Automation System (n8n)

A complete, production-ready n8n automation suite designed for high-signal, personalized technical recruiter outreach and automated multi-tier follow-ups.

---

## 📌 Features

- **Personalized Email Generation**: Dynamically crafts personalized HTML and plain-text emails based on recruiter data, company focus, and job title without generic fluff.
- **Automated Resume Attachment**: Seamlessly mounts and attaches resume PDFs into outgoing Gmail messages.
- **Idempotency & Duplicate Prevention**: Automatically detects previously contacted recruiters and prevents duplicate initial sends across executions.
- **Gmail Threading**: Follow-up messages (Follow-up 1 & 2) are automatically sent within the **same conversation thread** as the original message.
- **Smart Reply Detection**: Inspects Gmail threads before sending any follow-up, automatically stops sequences when human replies are detected, and ignores automated out-of-office responses.
- **Configurable Rate Limiting & Safety**: Includes a `TEST_MODE` safety switch, max email limits per execution (`MAX_EMAILS_PER_RUN`), configurable delays (`DELAY_BETWEEN_EMAILS_SECONDS`), and company-level daily limits (`MAX_RECRUITERS_PER_COMPANY_PER_DAY`).
- **Comprehensive Logging**: Full audit trail recorded to a dedicated Google Sheet tab (`EmailLogs`).

---

## 🏗 System Architecture

```text
                 RECRUITER OUTREACH WORKFLOW
                 
Google Sheets (Recruiters Tab)
     │
     ▼
Validate & Deduplicate ─────── Invalid / Duplicate ───► Skip / Log
     │
     ▼
Rate Limit & Batching (Max 2/company, Max 15/run)
     │
     ▼
Dynamic Personalization (HTML & Plain Text)
     │
     ▼
Attach Resume PDF (/files/Sai_Tarrun_Pitta_Resume.pdf)
     │
     ▼
Gmail Send (Clean formatting, no branding)
     │
     ▼
Update Google Sheet (Status=Sent, FollowUpDate=Now+5d, ThreadID)
     │
     ▼
Log to EmailLogs & Rate Limit Delay (90s)


                 FOLLOW-UP & REPLY DETECTION WORKFLOW

Daily Schedule (Mon-Fri 9:30 AM)
     │
     ▼
Find Due Follow-Ups (FollowUpDate <= Today & Count < 2)
     │
     ▼
Inspect Gmail Thread
     │
     ├── Recruiter Replied ───► Mark Status=Replied ───► STOP
     │
     └── No Reply Found
              │
              ├── Follow-up 1 (Sent + 5-7 days)
              │
              └── Follow-up 2 (Sent + 14 days, Final)
              │
              ▼
         Send in Existing Thread (GmailThreadID)
              │
              ▼
         Update Google Sheet & Log Action
```

---

## 📊 Google Sheets Schema

### Tab 1: `Recruiters`
| Header | Description |
| :--- | :--- |
| `RecruiterID` | Unique identifier (e.g., `001`) |
| `FirstName` | Recruiter's first name |
| `LastName` | Recruiter's last name |
| `Company` | Target company name |
| `Email` | Recruiter's email address |
| `RecruiterTitle` | Recruiter job title |
| `JobTitle` | Targeted engineering role (optional) |
| `JobLink` | Job application URL (optional) |
| `CompanyFocus` | Custom team/engineering focus for deep personalization |
| `Location` | Office location |
| `Status` | `Pending`, `Ready`, `Sent`, `Follow-up 1`, `Follow-up 2`, `Replied`, `Interview`, `Closed`, `Do Not Contact`, `Failed` |
| `SentDate` | Timestamp of initial outreach |
| `FollowUpDate` | Next scheduled follow-up date (`YYYY-MM-DD`) |
| `FollowUpCount` | Number of follow-ups sent (`0`, `1`, `2`) |
| `LastEmailDate` | Timestamp of latest message |
| `ReplyStatus` | `No Reply`, `Replied`, `Needs Review` |
| `ReplyDate` | Timestamp when recruiter reply was detected |
| `GmailMessageID` | Message ID returned from Gmail API |
| `GmailThreadID` | Thread ID for conversation continuity |
| `Notes` | Additional context or error logs |

### Tab 2: `EmailLogs`
| Header | Description |
| :--- | :--- |
| `Timestamp` | ISO timestamp of event |
| `RecruiterID` | Associated recruiter ID |
| `RecruiterName` | Full recruiter name |
| `Company` | Company name |
| `Email` | Recruiter email |
| `Action` | `Initial Email`, `Follow-up 1`, `Follow-up 2`, `Reply Detected`, `Failed` |
| `Status` | `Sent`, `Replied`, `Failed` |
| `GmailMessageID` | Gmail message identifier |
| `GmailThreadID` | Gmail thread identifier |
| `Error` | Error message (if applicable) |

---

## ⚙️ Setup & Installation

### 1. Run n8n with Docker Compose
```bash
docker compose up -d
```

### 2. Place Resume PDF
Copy your resume PDF to `./files/Sai_Tarrun_Pitta_Resume.pdf`:
```bash
cp /path/to/your/resume.pdf ./files/Sai_Tarrun_Pitta_Resume.pdf
```

### 3. Import Workflows
In n8n (`http://localhost:5678`), import the JSON workflows located in the `workflows/` directory:
1. `workflows/1_recruiter_outreach_workflow.json`
2. `workflows/2_recruiter_followup_workflow.json`
3. `workflows/test_email_workflow.json`

### 4. Connect Credentials
1. Add **Google Sheets OAuth2** credential.
2. Add **Gmail OAuth2** credential.
3. Link your Google Sheet document in the workflow nodes.

---

## 🔒 Safety & Testing Mode

By default, `TEST_MODE = true` in the Global Configuration node. All outreach emails are safely redirected to your personal email (`saitarrunpitta@gmail.com`) with the original recipient annotated in the subject line.

To go live:
1. Change `TEST_MODE` to `false` in both workflows.
2. Activate the schedules in n8n.

---

## 👤 Author
**Sai Tarrun Pitta**
- Portfolio: [saitarrunpitta.vercel.app](https://saitarrunpitta.vercel.app)
- LinkedIn: [linkedin.com/in/saitarrunpitta](https://linkedin.com/in/saitarrunpitta)
- GitHub: [github.com/saitarrun](https://github.com/saitarrun)
