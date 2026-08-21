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

console.log("\n🎉 ALL 4 JAVASCRIPT CLIENT-SIDE LOGIC TESTS PASSED!");
