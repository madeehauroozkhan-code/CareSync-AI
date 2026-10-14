<div align="center">
  <h1>🩺 CareSync AI</h1>
  <strong>An AI-powered Healthcare Coordination Platform for Rural India</strong>
</div>
<br />

> Patient is just one input. The real users are: Citizens, Hospitals, Ambulances, NGOs, Government, and PHCs. CareSync AI doesn't just help one patient — it coordinates the entire healthcare response around them.

---

## 📋 Table of Contents

- [🚀 Live Demo](#live-demo)
- [Problem Statement](#problem-statement)
- [What Makes This Different](#what-makes-this-different)
- [The 10 Agents](#the-10-agents)

---

<a id="live-demo"></a>
## 🚀 Live Demo

The entire CareSync AI platform is currently deployed and running live on the cloud:

- **Patient Interface (Frontend):** https://ai-sahayak-frontend.onrender.com/
- **Hospital/Admin Dashboard:** https://ai-sahayak-dashboard.onrender.com/
- **Backend API (FastAPI):** https://ai-sahayak-jxxw.onrender.com
- [Core Intelligence — The Hospital Scoring Model](#core-intelligence)
- [Full System Flow](#full-system-flow)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Author & Maintainer](#author)
- [Contributing](#contributing)
- [Future Scope](#future-scope)

---

<a id="problem-statement"></a>
## 🧩 Problem Statement

In India, and across most developing regions, a large share of the population — especially in rural and semi-urban areas — does not have timely access to healthcare and emergency medical services. The core issues are:

- **Distance and delay** — the nearest hospital is often unclear, and its real-time capacity is unknown.
- **No triage at first contact** — people can't tell if a symptom is minor or an emergency.
- **Resource mismatch during disasters** — some hospitals overload while others sit idle, because there's no real-time coordination between facilities, ambulances, and volunteers.
- **Language and literacy barriers** — most digital health tools are English/text-based.
- **No feedback loop** — once referred, nobody tracks whether the patient actually got treated.
- **Reactive public health monitoring** — outbreaks are usually noticed only after hospitals are already overwhelmed.

---

<a id="what-makes-this-different"></a>
## 🎯 What Makes This Different

A simple "symptom checker → hospital finder → notify family" pipeline has already been built many times. That combination alone is not a strong differentiator. The real innovation is:

> **The AI doesn't just help the patient. It actively coordinates hospitals, ambulances, volunteers, and government response around the patient.**

Concretely, this means:
- Instead of "nearest hospital," the system computes a **weighted score** across distance, bed capacity, specialization match, wait time, and ICU availability — and explains *why* it picked what it picked.
- Instead of reacting to a disaster after it happens, the Emergency Response Agent **predicts** which hospital is about to overload and redistributes patients *before* that happens.
- Instead of just detecting an outbreak, the Public Health Intelligence Agent **predicts the next hotspot** and recommends concrete actions (extra medicine stock, vaccination camps, mobile clinics).
- A dedicated agent activates **community resources** (NGOs, blood donors, local drivers/boat owners) during large-scale events — not just hospitals.
- The patient journey doesn't end at referral — a **Follow-up Agent** checks in after 24 hours to close the loop.

---

<a id="the-10-agents"></a>
## 🤖 The 10 Agents

| # | Agent | Capability & Function | What It Actually Does |
|---|---|---|---|
| 1 | **Citizen Intake Agent** | Natural Language & Voice Processing | Understands symptoms via voice/text in any language; converts free-form conversation into structured data |
| 2 | **Clinical Triage Agent** | Urgency Classification | Classifies urgency as **Critical / Urgent / Routine**, attaches a **confidence score**, and explains reasoning |
| 3 | **Care Coordination Agent** | Intelligent Hospital Routing | Chooses the best hospital using the weighted scoring model (see below) — not just the nearest one |
| 4 | **Emergency Response Agent** | Regional Load Balancing | Watches incoming case volume per region in real time and handles proactive redirection |
| 5 | **Public Health Intelligence Agent** | Outbreak Prediction | Continuously scans anonymized case data for symptom clusters to predict outbreaks |
| 6 | **Community Response Agent** | Resource Orchestration | Notifies nearby NGO volunteers, blood donors, and local drivers/boat owners during mass casualties |
| 7 | **Follow-up & Recovery Agent** | Patient Lifecycle Tracking | 24 hours after referral, checks in with the patient to close the full patient lifecycle |
| 8 | **Knowledge / RAG Agent** | Medical Context Retrieval | Searches medical PDFs via Qdrant Vector DB to provide immediate first-aid context for symptoms |
| 9 | **Explainability Agent** | Transparent AI Reasoning | Generates transparent explanations for AI decisions to build trust with doctors and patients |
| 10 | **Ambulance Dispatch Agent** | Autonomous Dispatch | Autonomously calculates distance and dispatches the nearest emergency vehicle for critical cases |

> **Why 10 agents instead of one LLM?** Each agent has a single responsibility and its own logic/prompt. This makes the system modular, lets us combine deterministic logic with LLM reasoning only where needed, and mirrors how a real healthcare coordination team is organized.

---

<a id="core-intelligence"></a>
## 🧠 Core Intelligence — The Hospital Scoring Model

This is the single most important piece of logic in the whole project — it's what proves "actual reasoning" instead of a simple lookup, and it's the part most likely to impress judges.

Instead of picking the nearest hospital, the **Care Coordination Agent** computes a score (0–100) for every candidate hospital:

```
Hospital Score =
      (Distance Weight        × Proximity Score)
    + (Bed Availability Weight × Capacity Score)
    + (Specialization Weight   × Specialist Match Score)
    + (Wait Time Weight        × Historical Wait Score)
    + (ICU Weight              × ICU Availability Score)   [only weighted in for Critical cases]
```

**Example scenario:**
- Hospital A → nearest, but 95% full, no cardiologist → **low score**
- Hospital B → 10 minutes further, has beds, no specialist → **medium score**
- Hospital C → a bit further still, but has a cardiologist and ICU beds free → **highest score for a chest-pain case**

The system picks **Hospital C**, and explains why:
```
Hospital C selected because:
✔ Cardiologist available (patient reported chest pain)
✔ ICU beds available (3)
✔ ETA ~14 min
✘ Hospital A is overloaded (95% capacity)
✘ Hospital B lacks a cardiac specialist
```

**Every weight is a configurable, documented constant** (e.g. distance 25%, capacity 25%, specialization 25%, wait time 15%, ICU 10%). In production these weights could be tuned or learned from historical outcome data, but for the platform they are transparent, adjustable numbers, not a hidden black box.

---

<a id="full-system-flow"></a>
## 🔄 Full System Flow

### Scenario A — Routine Case
```
Citizen: "Mujhe halka bukhaar hai, do din se"
   ↓
Citizen Intake Agent → structured symptom data
   ↓
Clinical Triage Agent → "Routine" (confidence: 88%, reason: mild fever, no red-flag symptoms)
   ↓
Safe home-care guidance shown (rest, hydration, "see a doctor if fever persists beyond 3 days")
   (No medicine names or dosages are ever suggested)
```

### Scenario B — Emergency Case
```
Citizen: "Chest me tez dard hai, saans lene me dikkat"
   ↓
Citizen Intake Agent → structured data
   ↓
Clinical Triage Agent → "Critical" (confidence: 95%, reason: chest pain + breathing difficulty)
   ↓
Care Coordination Agent → scores all nearby hospitals → selects best match with explanation
   ↓
Simulated ambulance dispatch → ETA shown
   ↓
Hospital dashboard → receives notification, reserves a slot
   ↓
Follow-up & Recovery Agent → schedules a 24-hour check-in
```

### Scenario C — Disaster / Mass-Casualty Surge
```
Flood event → 50 patients reporting symptoms in one region within minutes
   ↓
Emergency Response Agent → detects Hospital A is trending toward overload
   ↓
Proactively redirects new incoming cases to Hospital B and Hospital C
   (before Hospital A actually hits capacity — predictive, not reactive)
   ↓
Community Response Agent → notifies nearby NGO volunteers, blood donors,
   local drivers/boat owners, and the district officer liaison
   ↓
Dashboard shows live redistribution + activated volunteers on the map
```

### Scenario D — Public Health Prediction (runs continuously in background)
```
Public Health Intelligence Agent monitors all anonymized case data
   ↓
Detects: 45 of 52 recent cases in Village X report "high fever + body pain"
   ↓
Flags: "🟠 Possible dengue cluster in Village X"
   ↓
Predicts: neighboring Village Y is at elevated risk (based on proximity + trend)
   ↓
Recommends: increase platelet/testing stock, deploy mobile clinic, alert nearby PHCs
   ↓
Government Dashboard shows a Village Health Risk heatmap (Safe / Medium / High / Critical)
```

---

<a id="tech-stack"></a>
## 🛠️ Tech Stack

| Layer | Tool / Technology | Purpose |
|---|---|---|
| Frontend (Web) | React.js + Tailwind CSS | Citizen-facing chat interface |
| Admin Dashboard | React + Recharts + Leaflet.js / Google Maps | Map, charts, outbreak alerts, redistribution view |
| Low-connectivity access | WhatsApp Business API / Twilio SMS API | Reach users without a smartphone app or good internet |
| Backend / API | Python (FastAPI) | Core application server, agent orchestration |
| Agent Orchestration | LangGraph / CrewAI | Defines agents and how they hand off tasks to each other |
| LLM / Reasoning Engine | Gemini API or OpenAI API | Powers reasoning for Intake, Triage, and Public Health agents |
| Speech-to-Text | Google Speech-to-Text / Whisper API | Converts voice input to text |
| Text-to-Speech | Google Cloud TTS | Converts responses back to voice |
| Translation | Google Translate API / AI4Bharat IndicTrans2 | Hindi and regional language support |
| Database (structured) | PostgreSQL (Supabase) | Patient cases, facility data |
| Real-time data | Firebase Realtime Database | Simulated live hospital bed/occupancy status |
| Maps | Google Maps Platform API | Distance, ETA calculation |
| Notifications | Twilio (WhatsApp/SMS) | Family and volunteer notifications |
| Hosting | Vercel (frontend) + Render/Railway (backend) | Demo deployment |
| Version Control | Git + GitHub | Team collaboration |

---

<a id="project-structure"></a>
## 📁 Project Structure

```
CareSync-AI/
│
├── README.md
├── .gitignore
├── .env.example
│
├── frontend/                          # Landing page + AI Chat UI
│   └── src/
│       ├── components/ChatWindow.jsx, VoiceInput.jsx, StatusTracker.jsx
│       ├── pages/ChatPage.jsx
│       └── services/api.js
│
├── dashboard/                         # Admin Command Center
│   └── src/
│       └── components/MapView.jsx, CaseList.jsx, OutbreakAlert.jsx
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt
│   │
│   ├── agents/
│   │   ├── intake/                    # Voice & text intake
│   │   ├── triage/                    # Urgency classification
│   │   ├── care_coordination/         # Hospital scoring & routing model
│   │   ├── emergency_response/        # Regional load balancing
│   │   ├── public_health_intelligence/# Outbreak prediction
│   │   ├── community_response/        # Volunteer & NGO notification
│   │   └── followup_recovery/         # Patient lifecycle follow-up
│   │
│   ├── services/
│   │   ├── scoring_service.py         # the hospital scoring formula
│   │   ├── llm_service.py
│   │   ├── maps_service.py
│   │   ├── sms_service.py
│   │   └── firebase_service.py
│   │
│   ├── database/models.py, db_connection.py
│   └── config/settings.py
│
└── backend/tests/
    ├── test_triage_agent.py
    └── test_scoring_service.py
```

---

<a id="author"></a>
## 👤 Author & Maintainer

<table>
  <tr>
    <td align="center"><a href="https://github.com/madeehauroozkhan-code"><img src="https://github.com/madeehauroozkhan-code.png" width="100px;" alt=""/><br /><sub><b>Madeeha Urooz Khan</b></sub></a><br />Developer & Maintainer</td>
  </tr>
</table>

---

<a id="contributing"></a>
## 🤝 Contributing

Contributions are welcome — bug fixes, feature enhancements, or documentation improvements!

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please give appropriate credit to the original authors if you use or modify this project.

---

<a id="future-scope"></a>
## 🔮 Future Scope

- Real government health database integration (ABHA/Ayushman Bharat) for verified facility data.
- Offline SMS/IVR fallback with a sync-when-connected queue.
- Live traffic-aware ambulance routing.
- Drug/blood-supply shortage prediction as an extension of the Public Health Intelligence Agent.
- Multi-language admin dashboard for government officials.
- Extension of the same agent framework to other public services (education, agriculture advisory).

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<div align="center">
  <img src="https://img.shields.io/badge/BUILT_WITH-%E2%9D%A4-red?style=for-the-badge" alt="Built With Love" />
</div>

<div align="center">
  <b>⭐ Star this repo if you found it useful!</b>
</div>
