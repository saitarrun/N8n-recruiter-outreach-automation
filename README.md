<div align="center">

<img src="./assets/banner.svg" alt="Recruiter Outreach Automation" width="100%"/>

<br/>
<br/>

[![n8n](https://img.shields.io/badge/n8n-Workflow_Automation-FF6D5A?style=flat-square&logo=n8n&logoColor=white)](https://n8n.io)
[![Gmail API](https://img.shields.io/badge/Gmail-OAuth_2.0-EA4335?style=flat-square&logo=gmail&logoColor=white)](https://developers.google.com/gmail/api)
[![Google Sheets](https://img.shields.io/badge/Google_Sheets-Database-0F9D58?style=flat-square&logo=googlesheets&logoColor=white)](https://developers.google.com/sheets/api)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-38BDF8.svg?style=flat-square)](https://opensource.org/licenses/MIT)

<p align="center">
  <b>A production-ready, intelligent n8n automation suite for high-signal, personalized recruiter outreach, dynamic resume attachment, and smart multi-tier Gmail reply tracking.</b>
</p>

</div>

---

## ⚡ Overview

This suite automates technical recruiter outreach with built-in safety controls, smart reply tracking, and full conversation threading.

- **🎯 Context-Aware Personalization**: Dynamic subject lines and custom focus sentences tailored to each company and role.
- **📄 Resume Attachment**: Automatically reads and attaches your PDF resume from a mounted volume.
- **🔄 Gmail Threading**: Follow-up emails are sent inside the **same conversation thread** as the original message.
- **🛑 Smart Reply Detection**: Inspects Gmail threads before sending follow-ups; halts sequences on human reply and skips out-of-office autoreplies.
- **🔒 Built-in Guardrails**: Includes `TEST_MODE`, company rate limits (max 2/company/day), per-run caps (max 15/run), and 90s delays between sends.

---

## 🏗 Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 1. RECRUITER OUTREACH                       │
│                                                             │
│  [Google Sheets] ──► [Validate & Dedup] ──► [Personalize]   │
│                             │                       │       │
│                        (Skip/Log)             [Attach PDF]  │
│                                                     │       │
│  [Log to Sheet] ◄── [Update Status] ◄── [Gmail API Send]    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 2. FOLLOW-UP & REPLY TRACKING               │
│                                                             │
│  [Daily Schedule] ──► [Find Due Follow-Ups]                 │
│                               │                             │
│                      [Inspect Gmail Thread]                 │
│                               │                             │
│         ┌─────────────────────┴─────────────────────┐       │
│         ▼                                           ▼       │
│  [Reply Detected]                            [No Reply]     │
│         │                                           │       │
│  [Mark 'Replied' & Stop]                [Send in Same Thread]
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Google Sheet Schema

Create a Google Spreadsheet with two tabs:

### 1. `Recruiters` (Outreach Queue)
`RecruiterID` • `FirstName` • `LastName` • `Company` • `Email` • `RecruiterTitle` • `JobTitle` • `JobLink` • `CompanyFocus` • `Location` • `Status` • `SentDate` • `FollowUpDate` • `FollowUpCount` • `LastEmailDate` • `ReplyStatus` • `ReplyDate` • `GmailMessageID` • `GmailThreadID` • `Notes`

> **Statuses**: `Pending`, `Ready`, `Sent`, `Follow-up 1`, `Follow-up 2`, `Replied`, `Interview`, `Closed`, `Do Not Contact`, `Failed`

### 2. `EmailLogs` (Audit Trail)
`Timestamp` • `RecruiterID` • `RecruiterName` • `Company` • `Email` • `Action` • `Status` • `GmailMessageID` • `GmailThreadID` • `Error`

---

## 🚀 Quick Start

### 1. Launch n8n
```bash
docker compose up -d
```
Access the editor at **`http://localhost:5678`**.

### 2. Add Resume
Place your resume PDF at `./files/Sai_Tarrun_Pitta_Resume.pdf`.

### 3. Import & Connect
1. Import `workflows/1_recruiter_outreach_workflow.json` and `workflows/2_recruiter_followup_workflow.json`.
2. Connect **Google Sheets OAuth2** and **Gmail OAuth2** credentials.
3. Link your Google Sheet document ID in the nodes.

---

## 🛡 Safe Testing Mode

Both workflows default to `TEST_MODE = true` in the **Global Configuration** node. Outreach emails are routed to your test email with the recruiter address annotated in the subject.

To go live:
1. Set `TEST_MODE = false` in the configuration nodes.
2. Toggle the workflows to **Active**.

---

## 👤 Author

**Sai Tarrun Pitta**
- **Portfolio**: [saitarrunpitta.vercel.app](https://saitarrunpitta.vercel.app)
- **LinkedIn**: [linkedin.com/in/saitarrunpitta](https://linkedin.com/in/saitarrunpitta)
- **GitHub**: [@saitarrun](https://github.com/saitarrun)

---

## 📄 License

Distributed under the MIT License.
