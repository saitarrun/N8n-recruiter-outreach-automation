const assert = require("assert");

console.log("Running Client-Side JavaScript Logic & Parser Tests...\n");

// 1. Template Rendering & Token Substitution
function renderTemplate(tpl, lead, profile) {
  let text = tpl;
  text = text.replace(/\{RecruiterName\}/g, lead.firstName || 'there');
  text = text.replace(/\{Company\}/g, lead.company || 'your team');
  text = text.replace(/\{Email\}/g, lead.email || '');
  text = text.replace(/\{SenderName\}/g, profile.name || 'Sai Tarrun Pitta');
  text = text.replace(/\{SenderTitle\}/g, profile.title || 'Software Engineer');
  return text;
}

const mockLead = { firstName: "Sarah", company: "Stripe", email: "sarah@stripe.com" };
const mockProfile = { name: "Sai Tarrun Pitta", title: "Software Engineer" };
const mockTpl = "Hi {RecruiterName}, I am {SenderName}, a {SenderTitle} excited about engineering at {Company}. Contact: {Email}";

const rendered = renderTemplate(mockTpl, mockLead, mockProfile);
assert.strictEqual(rendered, "Hi Sarah, I am Sai Tarrun Pitta, a Software Engineer excited about engineering at Stripe. Contact: sarah@stripe.com");
console.log("✓ Test 1 Passed: Dynamic Token Substitution");

// 2. Subject Template Rendering
function renderSubject(subTpl, lead, profile) {
  return subTpl
    .replace(/\{Company\}/g, lead.company || 'your team')
    .replace(/\{SenderName\}/g, profile.name || 'Sai Tarrun Pitta')
    .replace(/\{SenderTitle\}/g, profile.title || 'Software Engineer')
    .trim();
}

const mockSubTpl = "Software Engineering Opportunities at {Company} — {SenderName}";
const renderedSub = renderSubject(mockSubTpl, mockLead, mockProfile);
assert.strictEqual(renderedSub, "Software Engineering Opportunities at Stripe — Sai Tarrun Pitta");
console.log("✓ Test 2 Passed: Subject Template Interpolation");

// 3. Auto-Tokenization of Custom Edits
function autoTokenizeHtml(html, lead) {
  let out = html;
  if (lead.company && lead.company.trim()) {
    const compRegex = new RegExp(lead.company.trim(), 'g');
    out = out.replace(compRegex, '{Company}');
  }
  if (lead.firstName && lead.firstName.trim()) {
    const nameRegex = new RegExp(`\\b${lead.firstName.trim()}\\b`, 'g');
    out = out.replace(nameRegex, '{RecruiterName}');
  }
  return out;
}

const userEdited = "<p>Hi Sarah, I would love to join Stripe as an engineer.</p>";
const tokenized = autoTokenizeHtml(userEdited, mockLead);
assert.strictEqual(tokenized, "<p>Hi {RecruiterName}, I would love to join {Company} as an engineer.</p>");
console.log("✓ Test 3 Passed: User Edits Auto-Tokenization");

// 4. Tab Delimited & Raw Text Bulk Parsing
function parseRawBulkText(rawText) {
  const lines = rawText.split('\n').map(l => l.trim()).filter(Boolean);
  const leads = [];
  for (const line of lines) {
    const parts = line.split(/[,\t|]/).map(p => p.trim());
    if (parts.length >= 3) {
      leads.push({
        firstName: parts[0],
        company: parts[1],
        email: parts[2]
      });
    }
  }
  return leads;
}

const rawInput = `
Sundar	Google	sundar@google.com
Satya	Microsoft	satya@microsoft.com
Tim	Apple	tim@apple.com
`;
const parsedLeads = parseRawBulkText(rawInput);
assert.strictEqual(parsedLeads.length, 3);
assert.strictEqual(parsedLeads[0].firstName, "Sundar");
assert.strictEqual(parsedLeads[1].company, "Microsoft");
assert.strictEqual(parsedLeads[2].email, "tim@apple.com");
console.log("✓ Test 4 Passed: Raw Document & Clipboard Lead Parsing");

// 5. Scheduler Target Leads Scope Slicing
function getScheduledTargetLeads(recruiters, scope) {
  const unsent = recruiters.filter(r => r.status !== 'Sent');
  if (scope === 'all') return unsent;
  const limit = parseInt(scope, 10) || unsent.length;
  return unsent.slice(0, limit);
}

const mockQueue = [
  { firstName: "A", status: "Pending" },
  { firstName: "B", status: "Sent" },
  { firstName: "C", status: "Pending" },
  { firstName: "D", status: "Pending" },
  { firstName: "E", status: "Pending" }
];
const allUnsent = getScheduledTargetLeads(mockQueue, 'all');
assert.strictEqual(allUnsent.length, 4, "Should return 4 unsent leads");
const limited5 = getScheduledTargetLeads(mockQueue, '2');
assert.strictEqual(limited5.length, 2, "Should limit to 2 unsent leads");
console.log("✓ Test 5 Passed: Scheduler Queue Slicing & Sent-Exclusion");

// 6. Scheduler Recurring Timestamp Calculation
function computeNextRecurringTimestamp(recurringTime, recurringDays, baseNow = new Date('2026-08-24T08:00:00')) {
  const parts = recurringTime.split(':');
  const targetH = parseInt(parts[0], 10);
  const targetM = parseInt(parts[1], 10);

  const next = new Date(baseNow);
  next.setHours(targetH, targetM, 0, 0);

  if (next.getTime() <= baseNow.getTime()) {
    next.setDate(next.getDate() + 1);
  }

  while (recurringDays.length > 0 && !recurringDays.includes(next.getDay())) {
    next.setDate(next.getDate() + 1);
  }

  return next.getTime();
}

const testNow = new Date('2026-08-24T08:00:00'); // Monday morning 8:00 AM
const nextTime = computeNextRecurringTimestamp('09:15', [1, 2, 3, 4, 5], testNow);
const nextDate = new Date(nextTime);
assert.strictEqual(nextDate.getHours(), 9);
assert.strictEqual(nextDate.getMinutes(), 15);
assert.strictEqual(nextDate.getDay(), 1); // Monday
console.log("✓ Test 6 Passed: Scheduler Recurring Time Calculation");

// 7. Scheduler Drip Interval & Jitter Calculation
function computeDripDelaySeconds(intervalMins, humanJitter, mockRandom = 0.5) {
  let baseSec = intervalMins * 60;
  if (humanJitter) {
    const jitter = Math.floor(mockRandom * 60) - 30; // -30 to +30
    baseSec = Math.max(20, baseSec + jitter);
  }
  return baseSec;
}

const strictDelay = computeDripDelaySeconds(3, false);
assert.strictEqual(strictDelay, 180, "Strict 3 mins should be 180s");
const jitterDelay = computeDripDelaySeconds(3, true, 0.75); // 0.75*60 - 30 = +15s -> 195s
assert.strictEqual(jitterDelay, 195, "Jittered 3 mins should be 195s");
console.log("✓ Test 7 Passed: Scheduler Drip Interval & Jitter Logic");

// 8. Bulk Sender State Machine (Pause, Resume, Stop)
let bulkState = { active: false, paused: false, stopped: false };
function testPauseBulk(s) { if (s.active && !s.stopped) s.paused = true; }
function testResumeBulk(s) { if (s.active && !s.stopped) s.paused = false; }
function testStopBulk(s) { if (s.active) { s.stopped = true; s.paused = false; } }

bulkState.active = true;
assert.strictEqual(bulkState.active, true);
testPauseBulk(bulkState);
assert.strictEqual(bulkState.paused, true, "Bulk sender should transition to paused");
testResumeBulk(bulkState);
assert.strictEqual(bulkState.paused, false, "Bulk sender should resume active state");
testStopBulk(bulkState);
assert.strictEqual(bulkState.stopped, true, "Bulk sender should transition to stopped");
console.log("✓ Test 8 Passed: Bulk Sender Pause, Resume, and Stop State Machine");

// 9. Scheduler State Machine (Arm, Pause, Resume, Stop)
let schedConfig = { status: 'idle', mode: 'specific' };
function testPauseScheduler(c) { if (c.status === 'armed' || c.status === 'running') c.status = 'paused'; }
function testResumeScheduler(c) { if (c.status === 'paused') c.status = (c.mode === 'drip') ? 'running' : 'armed'; }
function testStopScheduler(c) { c.status = 'idle'; }

schedConfig.status = 'armed';
testPauseScheduler(schedConfig);
assert.strictEqual(schedConfig.status, 'paused', "Scheduler should transition to paused");
testResumeScheduler(schedConfig);
assert.strictEqual(schedConfig.status, 'armed', "Scheduler should resume to armed");
testStopScheduler(schedConfig);
assert.strictEqual(schedConfig.status, 'idle', "Scheduler should transition to idle");
console.log("✓ Test 9 Passed: Scheduler Arm, Pause, Resume, and Stop State Machine");

// 10. Opportunities & Applied Job Follow-Up Template Presets
const opportunitiesTpl = "Hi {RecruiterName}, exploring opportunities at {Company}. From {SenderName}.";
const appliedTpl = "Hi {RecruiterName}, I recently applied for a Software Engineering role at {Company}. Best, {SenderName}.";

const renderedOpp = renderTemplate(opportunitiesTpl, mockLead, mockProfile);
assert.strictEqual(renderedOpp, "Hi Sarah, exploring opportunities at Stripe. From Sai Tarrun Pitta.");

const renderedApp = renderTemplate(appliedTpl, mockLead, mockProfile);
assert.strictEqual(renderedApp, "Hi Sarah, I recently applied for a Software Engineering role at Stripe. Best, Sai Tarrun Pitta.");

const oppSub = renderSubject("Exploring Software Engineering Opportunities at {Company} — {SenderName}", mockLead, mockProfile);
assert.strictEqual(oppSub, "Exploring Software Engineering Opportunities at Stripe — Sai Tarrun Pitta");

const appSub = renderSubject("Application Follow-Up: Software Engineer at {Company} — {SenderName}", mockLead, mockProfile);
assert.strictEqual(appSub, "Application Follow-Up: Software Engineer at Stripe — Sai Tarrun Pitta");

console.log("✓ Test 10 Passed: Opportunities Inquiry & Application Follow-Up Template Presets");

// 11. Active Resume Resolution & Fallback Logic
const mockLibrary = [
  { filename: "PittaSaiTarrun_SoftwareEngineer_Resume.pdf", size: "74.0 KB" },
  { filename: "Sai_Tarrun_Pitta_Frontend_Resume.pdf", size: "68.2 KB" }
];

function testGetActiveResumeFile(lead, activeSelected, lib) {
  if (lead && lead.resumeFile && lib.some(r => r.filename === lead.resumeFile)) {
    return lead.resumeFile;
  }
  if (activeSelected && lib.some(r => r.filename === activeSelected)) {
    return activeSelected;
  }
  if (lib.length > 0) {
    return lib[0].filename;
  }
  return "PittaSaiTarrun_SoftwareEngineer_Resume.pdf";
}

const leadWithValidResume = { resumeFile: "Sai_Tarrun_Pitta_Frontend_Resume.pdf" };
assert.strictEqual(testGetActiveResumeFile(leadWithValidResume, "PittaSaiTarrun_SoftwareEngineer_Resume.pdf", mockLibrary), "Sai_Tarrun_Pitta_Frontend_Resume.pdf");

const leadWithStaleResume = { resumeFile: "NonExistent_Old_Resume.pdf" };
assert.strictEqual(testGetActiveResumeFile(leadWithStaleResume, "PittaSaiTarrun_SoftwareEngineer_Resume.pdf", mockLibrary), "PittaSaiTarrun_SoftwareEngineer_Resume.pdf");

const leadWithoutResume = {};
assert.strictEqual(testGetActiveResumeFile(leadWithoutResume, null, mockLibrary), "PittaSaiTarrun_SoftwareEngineer_Resume.pdf");
console.log("✓ Test 11 Passed: Active Resume Resolution, Fallback & Library Validation");

// 12. Multi-Select Queue Selection and Bulk Delete State Logic
let mockMultiQueue = [
  { email: "a@wnco.com", status: "Pending" },
  { email: "b@koyeb.com", status: "Pending" },
  { email: "c@clerk.dev", status: "Sent" }
];

let selectedEmails = new Set();
function toggleLead(em, checked) { if (checked) selectedEmails.add(em); else selectedEmails.delete(em); }
function toggleAllVisible(leads, checked) {
  leads.forEach(l => { if (checked) selectedEmails.add(l.email); else selectedEmails.delete(l.email); });
}

// Filter unsent
const unsentOnly = mockMultiQueue.filter(r => r.status !== 'Sent');
assert.strictEqual(unsentOnly.length, 2);

toggleAllVisible(unsentOnly, true);
assert.strictEqual(selectedEmails.size, 2);
assert.strictEqual(selectedEmails.has("a@wnco.com"), true);
assert.strictEqual(selectedEmails.has("b@koyeb.com"), true);
assert.strictEqual(selectedEmails.has("c@clerk.dev"), false);

// Deselect one
toggleLead("a@wnco.com", false);
assert.strictEqual(selectedEmails.size, 1);

// Bulk delete action removes selected items
mockMultiQueue = mockMultiQueue.filter(r => !selectedEmails.has(r.email));
selectedEmails.clear();
assert.strictEqual(mockMultiQueue.length, 2);
assert.strictEqual(mockMultiQueue.some(r => r.email === "b@koyeb.com"), false);
console.log("✓ Test 12 Passed: Multi-Select Queue Selection and Bulk Delete State Logic");

console.log("\n🎉 ALL 12 JAVASCRIPT CLIENT-SIDE, RESUME & MULTI-SELECT TESTS PASSED!");
