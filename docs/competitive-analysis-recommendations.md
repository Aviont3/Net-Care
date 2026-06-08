# Net-Care Improvement Recommendations: Prioritized Synthesis

## 1. Quick Wins (< 1 Week Each, High Impact)

### 1.1 Push Notifications for Daily Reports

**Description:** Implement push notifications that alert parents when their child's AI-generated daily report is ready. Leverage the existing daily report system by adding a notification layer that triggers at pickup time with a personalized message (e.g., "Emma's daily report is ready — see what she did today!").

**Effort Estimate:** 2–3 days (Firebase Cloud Messaging or APNs integration + notification triggers on report generation)

**Impact Rating:** 5/5

**Competitive Advantage:** One push notification per day improves retention by 147%; around 1 in 3 app users only open the app after receiving a push notification ([Pugpig Docs](https://docs.pugpig.com/en_US/improving-engagement-with-your-app/how-to-maximise-engagement-with-push-notifications-and-in-app-messaging)). This transforms Net-Care's existing AI reports from a passive feature parents may forget to check into an active engagement driver.

---

### 1.2 Photo Attachment to Activity Logs

**Description:** Allow staff to attach a single photo when logging activities (meals, play, milestones). Photos are stored and displayed inline within the parent portal's daily report. No gallery, no albums — just a camera button on the existing activity logging form.

**Effort Estimate:** 3–5 days (camera capture, image upload/storage, display in parent portal)

**Impact Rating:** 5/5

**Competitive Advantage:** 42% of parents want milestone updates with photos multiple times per week ([LineLeader Blog](https://blog.lineleader.com/digital-communication-in-childcare-the-role-of-software-in-boosting-parent-satisfaction)). Photos are the #1 engagement driver across all childcare apps. This single addition transforms Net-Care's text-based reports into emotionally resonant updates that parents look forward to.

---

### 1.3 QR Code Parent Check-In

**Description:** Generate unique QR codes per family. Parents scan at the existing kiosk or use their phone camera to trigger check-in/out, replacing manual kiosk entry. Builds on the existing attendance system with a contactless front-end.

**Effort Estimate:** 3–4 days (QR generation per family, scanner integration at kiosk, mobile camera check-in option)

**Impact Rating:** 4/5

**Competitive Advantage:** Post-COVID, contactless check-in became industry standard. Brightwheel, Procare, and MyKidReports all offer QR-based check-in ([Gitnux — Childcare Attendance Software](https://gitnux.org/best/childcare-attendance-software/)). This modernizes Net-Care's existing kiosk without a full rebuild.

---

### 1.4 Bottom-Navigation UI Refactor (Staff App)

**Description:** Move the primary staff actions (Log Activity, Take Photo, Check-In, Messages) from top navigation/menus to a persistent bottom action bar. Ensure all primary tap targets are 44pt+ and in the thumb-friendly zone.

**Effort Estimate:** 3–5 days (UI restructure, no backend changes)

**Impact Rating:** 4/5

**Competitive Advantage:** 75% of mobile interactions happen with one hand ([Glance Design](https://thisisglance.com/learning-centre/how-do-i-design-for-one-handed-phone-use)). Childcare staff are holding children while logging — this isn't a nice-to-have, it's a workflow requirement. Brightwheel's success is explicitly attributed to their consumer-grade, speed-first design ([Rootstrap Case Study](https://www.rootstrap.com/case-studies/brightwheel)).

---

### 1.5 Quick-Log Preset Buttons

**Description:** Replace free-text activity entry with one-tap preset buttons for the most common activities: "Diaper (wet/dry)", "Bottle (2/4/6/8 oz)", "Nap Start/End", "Snack", "Outdoor Play". Staff tap once instead of filling forms.

**Effort Estimate:** 2–3 days (UI component + mapping to existing activity log model)

**Impact Rating:** 4/5

**Competitive Advantage:** Brightwheel saves staff "up to 20 hours per month" through streamlined workflows ([Brightwheel vs Procare Comparison](https://mybrightwheel.com/compare-brightwheel-vs-procare/)). LineLeader's daily reports let "teachers tap quick prompts instead of typing paragraphs" ([LineLeader: Automated Childcare Daily Reports](https://lineleader.com/feature/daily-reports)). This directly addresses the one-handed, 3-second-attention constraint of classroom staff.

---

## 2. Strategic Differentiators (1–4 Weeks)

### 2.1 AI-Powered Narrative Daily Reports (Enhanced)

**Description:** Upgrade Net-Care's existing template-based AI reports to generate rich, personalized narratives using LLM technology. Weave together the day's activity data, photos, behavioral observations, and milestones into parent-friendly prose. Example: "Sophia had a wonderful morning — she built her tallest block tower yet (7 blocks!) during free play, then was the first to sit for story time. She ate all her lunch and napped peacefully for 1.5 hours."

**Effort Estimate:** 2–3 weeks (LLM integration, prompt engineering, safety guardrails, parent preference settings)

**Impact Rating:** 5/5

**Competitive Advantage:** No major competitor offers true AI-narrative reports — Brightwheel, Procare, and HiMama all use template-based manual reporting ([AI & Innovation Trends Analysis](https://www.tryplayground.com/blog/best-ai-child-care-daycare-preschool)). Net-Care already has this as a basic feature; deepening it with GPT-4-class narratives creates a category-defining differentiator that justifies premium positioning against Brightwheel's purely template approach.

---

### 2.2 Bidirectional Parent-Staff Messaging

**Description:** Add real-time in-app messaging between parents and staff/admins. Include read receipts, admin oversight capabilities (directors can view all conversations), and message templates for common situations (absence notification, late pickup, etc.).

**Effort Estimate:** 2–3 weeks (WebSocket/real-time infrastructure, message UI for both staff and parent apps, notification integration, admin oversight panel)

**Impact Rating:** 5/5

**Competitive Advantage:** Real-time messaging is listed as essential by every buyer's guide and present in all top platforms ([Brightwheel — 9 Essential Features](https://mybrightwheel.com/blog/9-essential-features-of-child-care-manager-software)). Net-Care's current parent portal is read-only — adding messaging transforms it from a reporting tool into a communication platform. Parents who feel connected during early enrollment months are 40% more likely to stay long-term ([LineLeader Blog](https://blog.lineleader.com/digital-communication-in-childcare-the-role-of-software-in-boosting-parent-satisfaction)).

---

### 2.3 AI Communication Coach for Staff

**Description:** An AI assistant that helps staff draft sensitive parent messages. When a staff member needs to communicate about a biting incident, developmental concern, or behavioral pattern, the AI suggests tone-appropriate language, timing recommendations, and follow-up actions. Pre-loaded with childcare communication best practices.

**Effort Estimate:** 2–3 weeks (LLM integration, prompt library, message drafting UI, director approval workflow for sensitive topics)

**Impact Rating:** 4/5

**Competitive Advantage:** No competitor offers AI-assisted communication coaching. Playground's "Camber" AI handles routine inquiries but doesn't coach staff on sensitive conversations ([Playground: Best AI for Child Care 2026](https://www.tryplayground.com/blog/best-ai-child-care-daycare-preschool)). This addresses a real pain point — staff often struggle with how to phrase difficult messages and either avoid them (eroding trust) or communicate poorly (causing conflict).

---

### 2.4 Smart Ratio Compliance Alerts

**Description:** Real-time child-to-staff ratio monitoring that combines attendance data with staff clock-in data. Push alerts to directors when ratios approach or breach state-mandated limits. Include predictive warnings (e.g., "If Teacher B clocks out at 3 PM as scheduled, Room 2 will be over ratio by 1 child").

**Effort Estimate:** 2–3 weeks (ratio rule engine per state, real-time calculation from attendance + staff data, alert system, director dashboard widget)

**Impact Rating:** 4/5

**Competitive Advantage:** This extends Net-Care's existing DCFS compliance strength into real-time operational intelligence. While Brightwheel and Procare track ratios, none offer predictive ratio alerts that warn *before* violations occur ([Forbes: Tech Shifts Reshaping Childcare Franchises](https://www.forbes.com/councils/forbesbusinesscouncil/2026/05/19/tech-shifts-reshaping-childcare-franchises/)). Lightbridge Academy uses similar predictive scheduling AI as a franchise-level competitive advantage.

---

### 2.5 Weekly AI Developmental Insights

**Description:** Automatically analyze a child's activity, behavior, and milestone data over the week and generate a developmental insight summary. Flag emerging patterns (language development acceleration, socialization improvements, potential concerns). Frame as "conversation starters for parents" rather than assessments.

**Effort Estimate:** 3–4 weeks (longitudinal data aggregation, LLM-based pattern synthesis, developmental framework mapping, parent-facing report UI)

**Impact Rating:** 4/5

**Competitive Advantage:** No competitor offers AI-driven longitudinal developmental tracking ([AI & Innovation Trends Analysis — Blue Ocean section](https://www.tryplayground.com/blog/ai-use-child-care-2026)). Lillio/HiMama offers manual developmental portfolios and Brightwheel offers framework alignment, but none synthesize daily observations into actionable developmental narratives over time. This positions Net-Care as the "intelligent developmental partner" rather than just a logging tool.

---

## 3. Table-Stakes Gaps (Must-Have to Compete)

### 3.1 Billing & Automated Payments

**Description:** Full billing module: automated tuition invoicing based on enrollment schedules, multiple payment methods (ACH, credit card, autopay), payment reminders via push notification, late fee automation, subsidy tracking, and parent-facing payment portal. Include year-end tax statement generation (1099/tax receipts).

**Effort Estimate:** 6–8 weeks (payment processor integration e.g., Stripe, billing engine, invoice templates, autopay scheduling, parent payment UI, financial reporting)

**Impact Rating:** 5/5

**Competitive Advantage:** Without billing, Net-Care cannot compete as a standalone platform — centers must use separate tools, defeating the all-in-one value proposition. Every major competitor offers integrated billing ([WorldMetrics — Child Care Billing Software](https://worldmetrics.org/best/child-care-billing-software/)). Billing is also the stickiest feature: once parents are set up on autopay, switching costs become high. MyKidReports claims centers "cut late payments by 87% in the first 60 days" with integrated billing ([MyKidReports](https://mykidreports.com/why-mykidreports)).

---

### 3.2 Enrollment & Waitlist Management

**Description:** End-to-end enrollment pipeline: lead capture form (embeddable on center websites), inquiry tracking, tour scheduling, waitlist management with position visibility for parents, digital enrollment forms with document upload (photo capture from phone), and automated conversion to active child records upon acceptance.

**Effort Estimate:** 4–6 weeks (CRM pipeline, form builder, waitlist logic, document storage, parent-facing enrollment portal, admin pipeline dashboard)

**Impact Rating:** 5/5

**Competitive Advantage:** Enrollment management ties the entire system together — from first inquiry to active enrollment to billing. Without it, Net-Care only covers the middle of the center's workflow ([WorldMetrics — Best Day Care Software](https://worldmetrics.org/best/day-care-software)). Brightwheel positions this as their #1 essential feature, and their CRM "captures leads from your website, automates follow-up emails, and centralizes family data" ([Brightwheel — Childcare CRM](https://mybrightwheel.com/blog/childcare-crm)).

---

### 3.3 Staff Scheduling & Time Tracking

**Description:** Staff schedule builder with shift templates, time clock (clock-in/out via app), overtime tracking, ratio compliance integration, and schedule change notifications. Include a simple calendar view for staff to see their upcoming shifts and request time off.

**Effort Estimate:** 3–4 weeks (scheduling UI, time clock, shift templates, ratio integration, notification system, basic reporting)

**Impact Rating:** 4/5

**Competitive Advantage:** Procare's buyer's guide lists "basic staff scheduling tools" as essential even for the smallest centers ([Procare — Childcare Management Software for Small Businesses](https://www.procaresoftware.com/blog/childcare-management-software-for-small-businesses-what-daycare-owners-actually-use-in-2026/)). The primary value is ensuring ratio compliance at all times and providing accurate payroll data. Without this, directors manage staff on paper or in separate tools, creating reconciliation headaches and compliance risk.

---

## 4. Innovation Opportunities (AI-Powered Features Competitors Don't Have)

### 4.1 Predictive Illness & Outbreak Detection

**Description:** Pattern recognition across attendance and health log data to detect potential illness outbreaks early. When multiple children in the same classroom show similar symptoms (logged in health records) or unusual absence patterns emerge, the system alerts directors with recommended actions (notify parents, deep clean, monitor specific children).

**Effort Estimate:** 3–4 weeks (historical pattern analysis, anomaly detection model, alert rules, director notification UI, parent communication templates)

**Impact Rating:** 4/5

**Competitive Advantage:** No competitor offers predictive health analytics. Current platforms only log illness reactively. This turns Net-Care's existing health/medication tracking into a proactive safety tool — a compelling selling point for health-conscious post-COVID parents and licensing bodies.

---

### 4.2 AI Regulatory Compliance Assistant

**Description:** An LLM-powered chatbot trained on state-specific licensing regulations (starting with DCFS/Illinois, expandable). Staff and directors can ask plain-language questions ("Do I need a separate nap space for infants?", "How many fire drills per month?") and get instant, cited answers. The system also auto-generates compliance documentation from daily operational data and pre-fills state reporting forms.

**Effort Estimate:** 4–6 weeks (regulatory knowledge base construction, RAG system, compliance document generation, state report templates, chatbot UI)

**Impact Rating:** 5/5

**Competitive Advantage:** Net-Care already has DCFS-specific compliance monitoring — this extends it into an intelligent assistant. No competitor offers conversational regulatory guidance. Playground's "Camber" AI handles enrollment questions but doesn't address regulatory compliance ([Playground Platform](https://www.tryplayground.com)). For multi-state operators, this becomes a major differentiator as they face a patchwork of requirements.

---

### 4.3 AI-Generated Enrollment Nurture Sequences

**Description:** When families join the waitlist or inquire about enrollment, the system generates personalized email/notification sequences based on the family's stated priorities (e.g., outdoor play focus, multilingual program interest, sibling already enrolled). LLM crafts messages that feel personal rather than templated, with dynamic timing based on engagement signals.

**Effort Estimate:** 3–4 weeks (lead profiling, LLM sequence generation, engagement tracking, send-time optimization, A/B testing framework)

**Impact Rating:** 4/5

**Competitive Advantage:** Brightwheel's CRM automates follow-up but uses standard templates. LineLeader offers basic automation sequences. No competitor uses LLMs to generate deeply personalized, context-aware nurture content that adapts based on each family's specific questions and interests ([Forbes: Tech Shifts Reshaping Childcare Franchises](https://www.forbes.com/councils/forbesbusinesscouncil/2026/05/19/tech-shifts-reshaping-childcare-franchises/)). This directly improves lead-to-enrollment conversion without adding headcount.

---

### 4.4 Staff Training & Behavioral Coaching Copilot

**Description:** An always-available AI assistant for childcare workers that provides just-in-time guidance for behavioral situations ("A 3-year-old won't share and is hitting — what do I do?"), age-appropriate de-escalation strategies, and observation note suggestions aligned with developmental frameworks. Includes a "prepare for parent conference" mode that summarizes a child's recent data into talking points.

**Effort Estimate:** 4–5 weeks (behavioral guidance knowledge base, age-appropriate strategy library, conference prep generation, contextual suggestion UI, staff app integration)

**Impact Rating:** 4/5

**Competitive Advantage:** The 2026 Playground survey shows behavioral advice (28%) is the second-most-wanted AI use case among childcare workers ([Playground 2026 Survey](https://www.tryplayground.com/blog/ai-use-child-care-2026)). Only 12% of teams have formal AI training, meaning embedded, purpose-built tools win over standalone AI. No competitor offers a contextual coaching copilot that knows the specific child's history and temperament.

---

### 4.5 Sentiment-Aware Parent Relationship Monitor

**Description:** NLP analysis of parent message tone, response patterns, and engagement signals (app opens declining, messages becoming shorter/more curt, delayed payments) to surface early warning indicators of family dissatisfaction. Alerts directors before frustration becomes churn, with suggested re-engagement actions.

**Effort Estimate:** 3–4 weeks (sentiment analysis pipeline, engagement scoring model, churn risk indicators, director alert dashboard, suggested action templates)

**Impact Rating:** 3/5

**Competitive Advantage:** Parents who trust their provider are 65% more likely to remain loyal ([LineLeader Platform](https://lineleader.com/benefit/engage-families)). No competitor monitors parent sentiment proactively — all current systems are reactive (parents complain, then centers respond). This positions Net-Care as the platform that helps centers retain families before problems escalate.

---

## 5. UX Improvements

### 5.1 Progressive Enrollment Onboarding Flow

**Description:** Replace any bulk enrollment form with a step-by-step, mobile-optimized flow: one question per screen, clear progress indicators, document upload via phone camera, skip logic for irrelevant sections, and an estimated completion time shown upfront. Get parents to their first "aha moment" (seeing their child's daily report) within minutes of completing enrollment.

**Effort Estimate:** 1–2 weeks

**Impact Rating:** 4/5

**Competitive Advantage:** Government UX research shows chunked applications with progress indicators dramatically reduce abandonment ([HHS.gov Childcare Application Guidelines](https://childcareta.acf.hhs.gov/guidelines-designing-successful-online-application)). Brightwheel invests in "1:1 human support" during onboarding because their self-service flow still has friction. A seamlessly designed progressive flow reduces the need for hand-holding support.

---

### 5.2 Parent App "Today" Dashboard

**Description:** Make the parent app's home screen a "Today" view showing: current check-in status, most recent activity/photo, next scheduled event, and any unread messages. Eliminate the need to navigate to see what's happening right now. Auto-refresh in real time.

**Effort Estimate:** 1 week

**Impact Rating:** 4/5

**Competitive Advantage:** The information architecture should put "today's updates front and center upon app open" — this is what drives daily engagement ([LineLeader Blog](https://blog.lineleader.com/digital-communication-in-childcare-the-role-of-software-in-boosting-parent-satisfaction)). Most competing apps require 1–2 taps to reach today's updates. A zero-tap "Today" dashboard creates an Instagram-like immediacy.

---

### 5.3 Multilingual Interface & Plain Language

**Description:** Add language selection (Spanish, Mandarin, Arabic as priority based on US demographics) with full interface localization. Simultaneously audit all interface copy for plain language: active voice, sentences under 15 words, conversational tone, icon+text labels, and helper text on every form field.

**Effort Estimate:** 2–3 weeks (i18n framework, translation for top 3 languages, copy audit, icon system)

**Impact Rating:** 4/5

**Competitive Advantage:** Government guidelines mandate multilingual childcare applications ([HHS.gov](https://childcareta.acf.hhs.gov/guidelines-designing-successful-online-application)). Combining multilingual support with audio-visual material enhances comprehension by up to 50% for non-native speakers ([Moldstud](https://moldstud.com/articles/p-designing-mobile-apps-for-multilingual-education-challenges-and-solutions)). Most competitors offer English-only or limited Spanish support. Full multilingual + plain language positions Net-Care for diverse urban markets.

---

### 5.4 Notification Personalization & Smart Timing

**Description:** Allow parents to set notification preferences (frequency, types, quiet hours). Implement smart timing that delivers the mid-day photo update during lunch break and the daily report summary 15 minutes before typical pickup time. Segment notifications by classroom/age group to ensure relevance.

**Effort Estimate:** 1–2 weeks

**Impact Rating:** 3/5

**Competitive Advantage:** Personalized, timely notifications increase app opens while preventing opt-out from notification fatigue ([ZigPoll](https://www.zigpoll.com/content/how-can-i-efficiently-implement-targeted-push-notifications-in-my-javabased-daycare-app-to-improve-parent-engagement-without-overwhelming-them)). The daily engagement pattern (morning schedule → mid-day photo → pickup summary → weekly milestone) is a proven retention framework that most competitors implement inconsistently.

---

### 5.5 Offline Mode for Staff

**Description:** Enable basic activity logging (meals, naps, diapers, incidents) when staff are offline or in poor connectivity areas (basements, outdoor playgrounds). Queue entries locally and sync when connectivity resumes. Show a clear "offline" indicator and confirmation that entries will sync.

**Effort Estimate:** 1–2 weeks

**Impact Rating:** 3/5

**Competitive Advantage:** Users file 6x more complaints about "broken basics" than requests for new features ([PRNewswire / unitQ Report](https://www.prnewswire.com/news-releases/unitq-report-app-users-file-6x-more-complaints-about-broken-basics-than-requests-for-new-features-302697098.html)). Connectivity issues in childcare environments (thick walls, basements, outdoor areas) are common. Offline reliability prevents the frustration of lost entries and positions Net-Care as the most dependable option.

---

### 5.6 Batch Activity Logging

**Description:** Allow staff to log the same activity for multiple children simultaneously (e.g., "All 8 children in Ladybug Room had lunch at 11:30" or "Group nap time started for selected children"). Select children from a visual roster, choose the activity, and log in one tap.

**Effort Estimate:** 3–5 days

**Impact Rating:** 4/5

**Competitive Advantage:** Batch operations are a critical one-handed design pattern for classroom environments where activities happen simultaneously for groups. This directly reduces logging time from minutes to seconds for routine group activities, supporting the "save staff 20 hours/month" value proposition that Brightwheel leads with ([Brightwheel vs Procare Comparison](https://mybrightwheel.com/compare-brightwheel-vs-procare/)).

---

## Summary

### Implementation Priority Matrix

| Priority | Recommendation | Effort | Impact | Category |
|----------|---------------|--------|--------|----------|
| 1 | Push Notifications | 2–3 days | 5/5 | Quick Win |
| 2 | Photo Attachment | 3–5 days | 5/5 | Quick Win |
| 3 | Quick-Log Presets | 2–3 days | 4/5 | Quick Win |
| 4 | Bottom-Nav Refactor | 3–5 days | 4/5 | Quick Win |
| 5 | QR Code Check-In | 3–4 days | 4/5 | Quick Win |
| 6 | Billing & Payments | 6–8 weeks | 5/5 | Table Stakes |
| 7 | Parent Messaging | 2–3 weeks | 5/5 | Differentiator |
| 8 | AI Narrative Reports (Enhanced) | 2–3 weeks | 5/5 | Differentiator |
| 9 | Enrollment & Waitlist | 4–6 weeks | 5/5 | Table Stakes |
| 10 | AI Compliance Assistant | 4–6 weeks | 5/5 | Innovation |
| 11 | Smart Ratio Alerts | 2–3 weeks | 4/5 | Differentiator |
| 12 | Staff Scheduling | 3–4 weeks | 4/5 | Table Stakes |
| 13 | Weekly Dev Insights | 3–4 weeks | 4/5 | Differentiator |
| 14 | Predictive Illness Detection | 3–4 weeks | 4/5 | Innovation |
| 15 | AI Nurture Sequences | 3–4 weeks | 4/5 | Innovation |
| 16 | Staff Coaching Copilot | 4–5 weeks | 4/5 | Innovation |
| 17 | Progressive Onboarding | 1–2 weeks | 4/5 | UX |
| 18 | Parent "Today" Dashboard | 1 week | 4/5 | UX |
| 19 | Multilingual + Plain Language | 2–3 weeks | 4/5 | UX |
| 20 | Batch Activity Logging | 3–5 days | 4/5 | UX |
| 21 | Notification Personalization | 1–2 weeks | 3/5 | UX |
| 22 | Offline Mode | 1–2 weeks | 3/5 | UX |
| 23 | Sentiment Monitor | 3–4 weeks | 3/5 | Innovation |

### Key Takeaways

1. **Quick wins first, table stakes in parallel.** The five quick wins (push notifications, photos, presets, bottom-nav, QR check-in) can ship in 2 weeks and immediately transform user experience. Meanwhile, the billing and enrollment modules should begin development as the critical path to market viability.

2. **AI is Net-Care's moat — deepen it aggressively.** Net-Care's existing AI daily reports are already ahead of every major competitor. Enhancing them with LLM-powered narratives and expanding into developmental insights, compliance assistance, and staff coaching creates a multi-layered AI advantage that Brightwheel and Procare cannot quickly replicate.

3. **Billing is existential.** Without integrated billing, Net-Care cannot position as a standalone platform — it remains a supplementary classroom tool. Billing is the stickiest feature in childcare software (parents on autopay don't switch), and its absence is the single largest competitive disqualification.

4. **Design for the hardest user, win everyone.** Staff holding children with one free hand, immigrant parents with limited English, directors with 30 seconds between crises — designing for these constraints produces a universally excellent experience. The competitor that feels like a consumer app wins.

5. **Privacy-first AI wins trust.** With 61% of childcare workers citing security as their top AI concern and COPPA's January 2025 updates expanding penalties to $53,088 per incident ([FTC COPPA Update](https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-changes-childrens-privacy-rule-limiting-companies-ability-monetize-kids-data)), Net-Care's AI features must be transparent, consent-driven, and data-minimized. Building this trust becomes its own competitive advantage.

6. **The 3-month path to competitive parity:** Quick Wins (Weeks 1–2) → Messaging + Enhanced AI Reports (Weeks 3–5) → Billing MVP (Weeks 6–10) → Enrollment Pipeline (Weeks 10–14). This sequence ensures each phase delivers standalone value while building toward a complete platform that can go head-to-head with Brightwheel.
