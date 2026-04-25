# FedShield — Product Requirements Document (PRD)
### Version 2.0 — Final | Agentic IDE Edition (Copilot / Cursor / Windsurf / Antigravity)
### Author: Team BugBytes | Date: April 2026

---

> **Purpose of This Document**
> This PRD is the single source of truth for building FedShield end-to-end. It is written to be consumed directly by agentic coding assistants (GitHub Copilot Agent, Cursor, Windsurf, Antigravity). Every section is intentionally precise so that an AI agent can scaffold, implement, and wire up the full system without ambiguity.

---

## TABLE OF CONTENTS

1. [Product Vision & Core Concept](#1-product-vision--core-concept)
2. [Problem Statement](#2-problem-statement)
3. [Solution Architecture Overview](#3-solution-architecture-overview)
4. [Repository Structure](#4-repository-structure)
5. [Design System & UI Specification](#5-design-system--ui-specification)
6. [Frontend — Pages & Components](#6-frontend--pages--components)
7. [Three.js & GSAP Animation Specification](#7-threejs--gsap-animation-specification)
8. [Backend Services Specification](#8-backend-services-specification)
9. [Database Schema](#9-database-schema)
10. [ML Pipeline Specification](#10-ml-pipeline-specification)
11. [MLSecOps Specification](#11-mlsecops-specification)
12. [Blockchain / Smart Contract Specification](#12-blockchain--smart-contract-specification)
13. [API Contracts (All Endpoints)](#13-api-contracts-all-endpoints)
14. [Real-Time System (WebSocket + Redis)](#14-real-time-system-websocket--redis)
15. [CI/CD & Security Pipeline](#15-cicd--security-pipeline)
16. [Infrastructure (IaC)](#16-infrastructure-iac)
17. [Bank SDK Specification](#17-bank-sdk-specification)
18. [Functional Requirements](#18-functional-requirements)
19. [Non-Functional Requirements](#19-non-functional-requirements)
20. [Feature Roadmap (All Scope)](#20-feature-roadmap-all-scope)
21. [Success Metrics](#21-success-metrics)
22. [Risks & Mitigation](#22-risks--mitigation)
23. [Demo Script (5-Minute)](#23-demo-script-5-minute)
24. [Winning Sentence](#24-winning-sentence)

---

## 1. Product Vision & Core Concept

### One-Line Definition
FedShield is the **first open-source federated fraud intelligence network** — banks train ML models locally on private transaction data, share only encrypted weight updates, and a Byzantine-robust aggregation server produces a shared global model anchored immutably on-chain.

### Core Insight
```
Fraud is networked.        →  Fraudsters move across banks.
Detection is isolated.     →  Each bank sees only its own patterns.
FedShield breaks that gap. →  Shared intelligence, zero shared data.
```

### The Three Unsolved Problems FedShield Solves Simultaneously
| Problem | Solution |
|---------|----------|
| Legal barrier (GDPR, DPDP, PCI-DSS) | Federated Learning — raw data never leaves the bank |
| Trust barrier (competitive intelligence) | Only weight deltas are shared — no business logic exposed |
| Poisoning problem (malicious participants) | FLTrust + on-chain audit — attacks are detected and prosecutable |

---

## 2. Problem Statement

### 2.1 The Fraud Landscape
- Global card fraud loss: $32 billion/year (Nilson Report 2025)
- 78% of fraud is cross-institution — a fraudster flagged at HDFC reappears at a small NBFC the next day
- Detection gap between large banks (AUC ~0.96) and small fintechs (AUC ~0.71) is 0.25 AUC — that gap costs small fintechs 3–8% of transaction volume to fraud

### 2.2 Why Current Solutions Fail
```
Current Vendor Model (Feedzai, Sift, DataVisor):
  Bank sends raw transactions → Vendor builds model → Vendor owns all banks' data forever
  
Problems:
  1. Legal: GDPR Art. 28, India DPDP Act 2023, RBI/2021-22/112 prohibit this
  2. Trust: Bank A's fraud signals become Bank B's intelligence (via the vendor)
  3. Monopoly: Vendor becomes an irreplaceable data custodian

Isolated Bank Model:
  Each bank builds its own model on its own data
  
Problems:
  1. Small banks have insufficient fraud cases to train on
  2. Cross-bank fraud rings are completely invisible
  3. The weakest bank is the fraudster's entry point
```

### 2.3 Regulatory Context
| Regulation | Constraint | FedShield Compliance |
|------------|------------|----------------------|
| GDPR Article 5 | Data minimization — collect only what's necessary | Only weight deltas transmitted |
| India DPDP Act 2023 | Financial data is "sensitive personal data" — cannot leave bank | Federated architecture — data stays local |
| PCI-DSS v4.0 | Cardholder data must not be shared externally | No cardholder data in any transmission |
| RBI/2021-22/112 | Data localization for payment systems | Aggregation server deployable on Indian infra |

---

## 3. Solution Architecture Overview

### 3.1 System Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                    BANK NODE (N banks)                        │
│                                                              │
│  Raw Transactions → Feature Pipeline (local)                 │
│       ↓                                                      │
│  LightGBM Local Trainer → train on local data only           │
│       ↓                                                      │
│  Extract weight delta (Δw) — NOT raw data                    │
│       ↓                                                      │
│  Differential Privacy noise injection (ε-DP, Gaussian)       │
│       ↓                                                      │
│  Sign Δw with bank's RSA-4096 private key                    │
│       ↓                                                      │
│  Upload encrypted Δw to IPFS → submit CID + hash             │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│           FEDSHIELD AGGREGATION SERVER (FastAPI)              │
│                                                              │
│  Receive CIDs from N banks                                   │
│  Verify RSA signatures → reject invalid                       │
│  Pull Δw from IPFS → verify SHA-256 hashes                   │
│  GradientAnomalyDetector (3-layer) → flag suspicious         │
│  FLTrust Byzantine-robust scoring → compute trust weights     │
│  FedAvg weighted aggregation → global model                  │
│  SHA-256 global model → write hash to Polygon                 │
│  Store global model on IPFS → distribute CID to all banks    │
└──────────────────────────────────────────────────────────────┘
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
┌──────────────────────┐  ┌───────────────────────────┐
│  FASTIFY SCORING API  │  │   POLYGON BLOCKCHAIN       │
│  (<10ms p99 latency)  │  │                           │
│                      │  │  Round N: hash 0xABC       │
│  POST /v1/score/txn  │  │  Poisoning event: 0xDEF    │
│  WS  /v1/alerts      │  │  Bank suspended: 0xGHI     │
│  POST /v1/score/batch│  │  (immutable, permanent)    │
└──────────────────────┘  └───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                   REACT 19 DASHBOARD                          │
│                                                              │
│  Three.js 3D Network Globe   │  Live Fraud Alert Feed        │
│  GSAP Animated Metrics       │  Federation Round Status      │
│  Bank Contribution Heatmap   │  Compliance Report Generator  │
│  Poisoning Event Timeline    │  Model Performance Charts     │
│  SHAP Explainability Panel   │  Multi-Bank Simulation View   │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow Clarity
```
What IS transmitted:
  ✅ Encrypted model weight deltas (Δw) → IPFS
  ✅ IPFS CID (content identifier string) → aggregation server
  ✅ SHA-256 hash of Δw → server (for verification)
  ✅ RSA signature → server (for authentication)
  ✅ Scalar metrics (local AUC, sample count) → server

What is NEVER transmitted:
  ❌ Transaction records
  ❌ Account IDs
  ❌ Customer identity
  ❌ Raw feature vectors
  ❌ Fraud labels
```

---

## 4. Repository Structure

```
fedshield/
├── apps/
│   ├── web/                          # React 19 + Vite + Three.js + GSAP dashboard
│   │   ├── src/
│   │   │   ├── components/           # Reusable UI components
│   │   │   │   ├── three/            # All Three.js scenes
│   │   │   │   ├── charts/           # Recharts + D3 data visualizations
│   │   │   │   ├── ui/               # Design system primitives
│   │   │   │   └── layout/           # Shell, sidebar, topbar
│   │   │   ├── pages/                # Route-level page components
│   │   │   ├── hooks/                # Custom React hooks (WebSocket, SWR, etc.)
│   │   │   ├── store/                # Zustand global state
│   │   │   ├── lib/                  # API clients, utility functions
│   │   │   └── animations/           # GSAP timeline definitions
│   │   ├── public/
│   │   └── vite.config.ts
│   │
│   ├── api-gateway/                  # Fastify real-time scoring API (Node.js)
│   │   ├── src/
│   │   │   ├── routes/               # score.js, alerts.js, health.js
│   │   │   ├── plugins/              # Redis, DB, auth, rate-limit
│   │   │   ├── middleware/           # JWT validation, bank auth
│   │   │   └── inference/            # WASM/ONNX model runner
│   │   └── package.json
│   │
│   ├── federation-server/            # FastAPI Python aggregation server
│   │   ├── main.py
│   │   ├── aggregation/              # FedAvg, FLTrust
│   │   ├── poisoning/                # Gradient anomaly detection
│   │   ├── ipfs/                     # IPFS client
│   │   ├── blockchain/               # Polygon web3 client
│   │   └── schemas.py
│   │
│   ├── admin-service/                # Django REST bank management
│   │   ├── banks/                    # Bank CRUD, onboarding
│   │   ├── compliance/               # Report generation
│   │   └── rounds/                   # Federation round management
│   │
│   └── contracts/                    # Solidity smart contracts
│       ├── FedShieldRegistry.sol
│       ├── test/
│       └── hardhat.config.js
│
├── packages/
│   ├── bank-sdk-python/              # pip install fedshield-sdk
│   │   ├── fedshield/
│   │   │   ├── client.py             # FedShieldClient
│   │   │   ├── trainer.py            # LocalTrainer
│   │   │   ├── features.py           # FeatureExtractor
│   │   │   └── privacy.py            # DifferentialPrivacy
│   │   └── setup.py
│   │
│   ├── bank-sdk-node/                # npm install fedshield-sdk
│   └── shared-types/                 # Zod + Pydantic schemas
│
├── ml/
│   ├── local_trainer/                # Bank-side LightGBM training
│   ├── aggregation/                  # FedAvg + FLTrust implementation
│   ├── feature_pipeline/             # Feature engineering (24 features)
│   ├── models/                       # Model architecture definitions
│   ├── explainability/               # SHAP integration
│   └── experiments/                  # MLflow experiment tracking
│
├── mlsecops/
│   ├── poisoning_detector/           # 3-layer gradient anomaly detection
│   ├── drift_monitor/                # Evidently drift configs
│   ├── adversarial_tests/            # Robustness test suite
│   └── simulation/                   # Multi-bank attack simulation
│
├── infra/
│   ├── terraform/                    # AWS / GCP / Azure IaC
│   ├── helm/                         # K8s Helm charts per service
│   └── argocd/                       # GitOps manifests
│
├── simulation/                       # Multi-bank local simulation (student feature)
│   ├── synthetic_data/               # Fraud dataset generators
│   ├── bank_simulator.py             # Spins up N simulated banks
│   └── attack_simulator.py           # Gradient poisoning attack simulation
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       └── deploy.yml
│
├── docker-compose.dev.yml
├── docker-compose.test.yml
├── docker-compose.simulation.yml     # Full multi-bank local simulation
└── README.md
```

---

## 5. Design System & UI Specification

> **Agent Instruction:** Build the entire frontend using this design system. Every component must follow these exact tokens. The UI is light theme, clean, professional — think Vercel dashboard × Linear × Stripe.

### 5.1 Color Palette

```css
:root {
  /* Primary Brand */
  --color-primary-50:   #EFF6FF;
  --color-primary-100:  #DBEAFE;
  --color-primary-200:  #BFDBFE;
  --color-primary-500:  #3B82F6;
  --color-primary-600:  #2563EB;
  --color-primary-700:  #1D4ED8;
  --color-primary-900:  #1E3A5F;

  /* Neutrals (Light Theme Base) */
  --color-bg-base:      #FFFFFF;
  --color-bg-subtle:    #F8FAFC;
  --color-bg-muted:     #F1F5F9;
  --color-bg-emphasis:  #E2E8F0;

  /* Text */
  --color-text-primary:  #0F172A;
  --color-text-secondary: #475569;
  --color-text-muted:    #94A3B8;
  --color-text-inverse:  #FFFFFF;

  /* Semantic Colors */
  --color-success:      #10B981;
  --color-success-bg:   #D1FAE5;
  --color-warning:      #F59E0B;
  --color-warning-bg:   #FEF3C7;
  --color-danger:       #EF4444;
  --color-danger-bg:    #FEE2E2;
  --color-info:         #06B6D4;
  --color-info-bg:      #CFFAFE;

  /* Risk Tier Colors */
  --color-risk-low:      #10B981;
  --color-risk-medium:   #F59E0B;
  --color-risk-high:     #F97316;
  --color-risk-critical: #EF4444;

  /* Border */
  --color-border:        #E2E8F0;
  --color-border-subtle: #F1F5F9;

  /* Glassmorphism */
  --glass-bg:            rgba(255, 255, 255, 0.7);
  --glass-border:        rgba(255, 255, 255, 0.9);
  --glass-shadow:        0 4px 24px rgba(0, 0, 0, 0.06);

  /* Three.js Canvas BG */
  --canvas-bg:           #F0F4FF;
}
```

### 5.2 Typography

```css
/* Font Stack */
--font-sans: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Scale */
--text-xs:   0.75rem;    /* 12px — labels, badges */
--text-sm:   0.875rem;   /* 14px — body secondary */
--text-base: 1rem;       /* 16px — body primary */
--text-lg:   1.125rem;   /* 18px — lead text */
--text-xl:   1.25rem;    /* 20px — section headers */
--text-2xl:  1.5rem;     /* 24px — page titles */
--text-3xl:  1.875rem;   /* 30px — hero metrics */
--text-4xl:  2.25rem;    /* 36px — hero numbers */
--text-6xl:  3.75rem;    /* 60px — landing hero */

/* Weight */
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
--font-extrabold: 800;

/* Line Height */
--leading-tight:  1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

### 5.3 Spacing & Layout

```css
/* Spacing Scale (4px base) */
--space-1:  0.25rem;   /* 4px */
--space-2:  0.5rem;    /* 8px */
--space-3:  0.75rem;   /* 12px */
--space-4:  1rem;      /* 16px */
--space-5:  1.25rem;   /* 20px */
--space-6:  1.5rem;    /* 24px */
--space-8:  2rem;      /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */
--space-16: 4rem;      /* 64px */
--space-20: 5rem;      /* 80px */

/* Border Radius */
--radius-sm:  0.375rem;   /* 6px */
--radius-md:  0.5rem;     /* 8px */
--radius-lg:  0.75rem;    /* 12px */
--radius-xl:  1rem;       /* 16px */
--radius-2xl: 1.5rem;     /* 24px */
--radius-full: 9999px;

/* Shadows */
--shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
--shadow-md:  0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
--shadow-lg:  0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.04);
--shadow-xl:  0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04);
--shadow-glow-blue: 0 0 20px rgba(59, 130, 246, 0.3);
--shadow-glow-green: 0 0 20px rgba(16, 185, 129, 0.3);
--shadow-glow-red: 0 0 20px rgba(239, 68, 68, 0.3);

/* Layout */
--sidebar-width: 256px;
--topbar-height: 64px;
--content-max-width: 1400px;
```

### 5.4 Component Design Tokens

```
Card:
  background: var(--color-bg-base)
  border: 1px solid var(--color-border)
  border-radius: var(--radius-xl)
  padding: var(--space-6)
  box-shadow: var(--shadow-md)
  transition: box-shadow 200ms ease, transform 200ms ease
  hover: box-shadow var(--shadow-lg), transform translateY(-1px)

Stat Card:
  Same as Card + top-left colored accent bar (4px wide, full height)
  Accent color maps to semantic color based on metric type

Badge:
  padding: 2px 8px
  border-radius: var(--radius-full)
  font-size: var(--text-xs)
  font-weight: var(--font-semibold)
  text-transform: uppercase
  letter-spacing: 0.05em

Button Primary:
  background: var(--color-primary-600)
  color: white
  border-radius: var(--radius-md)
  padding: 10px 20px
  font-weight: var(--font-semibold)
  transition: all 150ms ease
  hover: background var(--color-primary-700), box-shadow var(--shadow-glow-blue)

Button Secondary:
  background: var(--color-bg-muted)
  color: var(--color-text-primary)
  border: 1px solid var(--color-border)
  hover: background var(--color-bg-emphasis)
```

### 5.5 Animation Principles

```
Entrance:   fade-in + translateY(12px → 0) over 400ms, easing: cubic-bezier(0.16, 1, 0.3, 1)
Hover:      scale(1.02) + shadow upgrade over 200ms ease
Number Count: GSAP CountTo — always counts up from 0 on mount
Stagger:    Children stagger entrance by 60ms per item
Three.js:   Continuous slow rotation (0.001 rad/frame), accelerates on hover
```

---

## 6. Frontend — Pages & Components

### 6.1 Application Shell

```
Layout:
  <AppShell>
    <Sidebar />        ← fixed left, 256px wide
    <MainContent>
      <Topbar />       ← fixed top, 64px tall
      <PageContent />  ← scrollable, padded
    </MainContent>
  </AppShell>
```

**Sidebar Items (in order):**
```
🏠  Overview          /dashboard
🌐  Network Globe     /dashboard/network
📊  Federation Rounds /dashboard/rounds
🏦  Banks             /dashboard/banks
🚨  Fraud Alerts      /dashboard/alerts
🛡️  Security          /dashboard/security
📈  Analytics         /dashboard/analytics
🧠  Explainability    /dashboard/explain
📋  Compliance        /dashboard/compliance
⚙️  Settings          /dashboard/settings
```

**Sidebar Design:**
- Width: 256px, white background
- Logo at top (shield icon + "FedShield" wordmark)
- Active item: primary-50 background, primary-600 text, left border 3px primary-600
- Hover: bg-subtle transition 150ms
- Bottom: User avatar + name + role badge
- Collapse button for narrow screens

**Topbar Design:**
- Height: 64px, white, border-bottom: 1px solid border
- Left: Page title (dynamic, matches current route)
- Center: Search bar (command palette trigger — Cmd+K)
- Right: [Federation status pill] [Notification bell] [User menu]
- Federation status pill: green "Round 42 Active" or amber "Aggregating..."

---

### 6.2 Page: Overview Dashboard (`/dashboard`)

**Layout: CSS Grid**
```
Row 1: [KPI Cards × 4]
Row 2: [Three.js Network Globe (60%)] [Live Alert Feed (40%)]
Row 3: [AUC Improvement Chart] [Round History Table]
Row 4: [Bank Participation Heatmap] [Risk Distribution Donut]
```

**KPI Cards (Row 1):**
```
Card 1 — Active Banks
  Icon: building-bank (blue)
  Value: "47" (GSAP count-up)
  Sub: "+3 this week"
  Accent: primary-500

Card 2 — Federation Rounds
  Icon: refresh-circle (green)
  Value: "142"
  Sub: "Round 143 in 2h 14m"
  Accent: success

Card 3 — Global AUC
  Icon: chart-line (purple)
  Value: "0.9421"
  Sub: "+0.2301 vs isolated avg"
  Accent: #8B5CF6

Card 4 — Threats Blocked (24h)
  Icon: shield-check (red)
  Value: "2,847"
  Sub: "$1.2M protected"
  Accent: danger
```

**AUC Improvement Chart:**
- Line chart (Recharts)
- X axis: Federation round number
- Y axis: AUC score 0.0–1.0
- Two lines: "Global Model" (blue) vs "Isolated Avg" (gray dashed)
- Annotations: "Round 1: +0.04" → "Round 10: +0.23"
- Fill gradient under global model line

**Bank Participation Heatmap:**
- GitHub-style contribution grid
- X: rounds (last 30), Y: banks
- Color: green intensity = trust score
- Red cells = flagged/rejected updates
- Tooltip: "Bank XYZ — Round 41 — Trust Score: 0.94"

---

### 6.3 Page: Network Globe (`/dashboard/network`)

> **This is the hero feature of the UI — see Section 7 for full Three.js spec**

**Layout:**
- Full-page Three.js canvas (100vw × calc(100vh - 64px))
- Floating control panel (top-right): [Bank Filter] [Show Attacks Toggle] [Animation Speed]
- Floating legend (bottom-left): node colors, edge meanings
- Floating info panel (right side, slides in on node click): Bank details

**What the Globe Shows:**
- 3D Earth-like sphere with wireframe overlay
- Blue nodes = active bank participants (positioned by geography)
- Pulsing green rings = healthy update submission
- Red flash = poisoning attack detected
- Animated arcs = weight updates traveling to aggregation server
- Central glowing orb = aggregation server (rotates slowly)
- On node hover: show bank name, trust score, rounds participated
- On click: slide-in panel with full bank profile

---

### 6.4 Page: Federation Rounds (`/dashboard/rounds`)

**Layout:**
```
Row 1: [Round Status Banner — current round progress]
Row 2: [Rounds Table — sortable, filterable]
Row 3: [Selected Round Detail — expands inline]
```

**Round Status Banner:**
- Large progress bar showing "X of Y banks submitted"
- Countdown timer to round close
- Status: OPEN → AGGREGATING → COMPLETE
- GSAP animated status transitions

**Rounds Table Columns:**
```
Round # | Status | Banks | AUC | Precision | Recall | Poisoning | Timestamp | Actions
```

**Round Detail Expansion:**
- Per-bank submission cards: bank name, trust score, dp_epsilon, status badge
- Poisoning events in this round (if any)
- Global model hash (truncated, copy button)
- Polygon tx hash (link to explorer)
- "Download Global Model" button

---

### 6.5 Page: Fraud Alerts (`/dashboard/alerts`)

**Layout:**
```
Row 1: [Risk Summary Cards — 4 tiers]
Row 2: [Alert Feed (live WebSocket)] [Alert Detail Panel]
```

**Alert Feed:**
- Real-time scrolling list (WebSocket-powered)
- Each alert item:
  ```
  [Risk Badge] [Transaction Hash] [Amount] [Channel] [Fraud Prob %] [Decision] [Time]
  ```
- Color-coded left border: green/amber/orange/red
- Clicking alert → right panel slides in with full detail
- "Block" badge animates with a red pulse
- Filter bar: [All] [Block] [Review] [Allow] + [Search by hash]

**Alert Detail Panel:**
- Transaction features breakdown
- SHAP waterfall chart (feature contributions)
- Historical fraud score for this account
- Model round used
- One-click: "Mark as False Positive" | "Confirm Fraud"

---

### 6.6 Page: Security — Poisoning Events (`/dashboard/security`)

**Layout:**
```
Row 1: [Attack Summary Stats]
Row 2: [Attack Timeline (D3 timeline)] [Attack Type Breakdown (Donut)]
Row 3: [Poisoning Events Table]
Row 4: [Suspended Banks Panel]
```

**Attack Timeline:**
- D3 horizontal timeline
- Events plotted as circles: color = attack type
- Hover: tooltip with bank, round, attack type, anomaly score
- Zoom and pan enabled

**Poisoning Events Table Columns:**
```
Bank | Round | Attack Type | Anomaly Score | Detection Method | On-Chain Evidence | Status
```

**Attack type color coding:**
- gradient_scaling → orange
- sign_flip → red
- backdoor → purple
- sybil → pink
- near_zero → yellow

---

### 6.7 Page: Explainability (`/dashboard/explain`)

**Purpose:** SHAP-based transaction explanation tool

**Layout:**
```
Row 1: [Transaction Input Form]
Row 2: [Fraud Score Gauge] [SHAP Waterfall Chart]
Row 3: [Feature Importance Bar Chart] [Similar Fraud Cases]
```

**Transaction Input Form:**
- Input fields for all 24 features (or paste JSON)
- "Score Transaction" button → triggers API call
- Real-time validation

**SHAP Waterfall Chart:**
- Custom D3 visualization
- Bars: left = reduces fraud probability, right = increases it
- Colors: red for high-impact fraud indicators, blue for low-risk indicators
- Feature names as Y-axis labels
- Base value and final score shown
- Example output:
  ```
  Base value: 0.12
  + is_new_device:      +0.31
  + txn_count_1h:       +0.18
  + mcc_is_high_risk:   +0.12
  - amount_zscore_30d:  -0.04
  Final:                0.69 → HIGH RISK
  ```

**Fraud Score Gauge:**
- SVG semicircular gauge
- Color transitions: green → yellow → orange → red
- Needle animates with GSAP spring easing
- Center displays exact probability + risk tier

---

### 6.8 Page: Compliance (`/dashboard/compliance`)

**Layout:**
```
Row 1: [Compliance Status Overview — regulatory checklist]
Row 2: [Report Generator Panel] [Audit Trail Timeline]
Row 3: [Data Residency Map]
```

**Report Generator:**
- Dropdown: [RBI DPSP] [GDPR Art. 30] [PCI-DSS] [FIU-IND]
- Date range picker
- "Generate Report" → triggers backend PDF generation
- Download button for generated PDF

**Audit Trail Timeline:**
- Vertical timeline of all federation rounds
- Each round entry: round number, global model hash, participant count, chain tx link
- Clicking chain tx opens Polygon explorer in new tab

**Data Residency Map:**
- Three.js mini globe (smaller, non-interactive)
- Shows where data is stored (only within bank boundaries)
- Green fill = bank's country = data stays there
- Label: "Zero cross-border data movement"

---

### 6.9 Page: Multi-Bank Simulation (`/dashboard/simulate`)

**Purpose:** Showcase the system working end-to-end with simulated banks

**Layout:**
```
Row 1: [Simulation Config Panel]
Row 2: [Live Simulation Visualizer — Three.js]
Row 3: [Simulation Logs] [Performance Chart]
```

**Simulation Config:**
- Number of banks: slider 2–10
- Fraud rate: slider 0.1%–5%
- Attack mode: [None] [Gradient Scaling] [Sign Flip] [Backdoor]
- Federation rounds: input 1–20
- "Start Simulation" button

**Live Simulation Visualizer:**
- Three.js animation showing banks as nodes
- Animated weight packets flowing to central server
- Red explosion animation when attack is detected
- Green pulse when round completes
- Counter: current round / total rounds

---

### 6.10 Page: Analytics (`/dashboard/analytics`)

**Charts Required:**
1. AUC over rounds (line chart, dual Y-axis)
2. Fraud detection rate by risk tier (stacked bar)
3. API latency percentiles p50/p95/p99 (line chart)
4. Scoring volume by bank (stacked area, last 30 days)
5. False positive / False negative rate over time (line)
6. Trust score distribution across banks (histogram)
7. DP epsilon usage by bank (horizontal bar)

---

## 7. Three.js & GSAP Animation Specification

> **Agent Instruction:** These are the exact 3D and animation specs. Use Three.js r155+ and GSAP 3.12+.

### 7.1 Main Network Globe (`NetworkGlobe.tsx`)

```typescript
// Setup
const globe = new THREE.Mesh(
  new THREE.SphereGeometry(2, 64, 64),
  new THREE.MeshPhongMaterial({
    color: 0xE8F0FE,
    wireframe: false,
    transparent: true,
    opacity: 0.85,
  })
)

// Wireframe overlay
const wireframe = new THREE.Mesh(
  new THREE.SphereGeometry(2.01, 32, 32),
  new THREE.MeshBasicMaterial({
    color: 0x3B82F6,
    wireframe: true,
    transparent: true,
    opacity: 0.12,
  })
)

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
const directionalLight = new THREE.DirectionalLight(0x4A90E2, 1.2)
directionalLight.position.set(5, 3, 5)

// Background
renderer.setClearColor(0xF0F4FF, 1)

// Camera
const camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000)
camera.position.set(0, 0, 7)

// Controls
const controls = new OrbitControls(camera, renderer.domElement)
controls.enableDamping = true
controls.dampingFactor = 0.05
controls.minDistance = 4
controls.maxDistance = 12
controls.autoRotate = true
controls.autoRotateSpeed = 0.3
```

**Bank Node Rendering:**
```typescript
interface BankNode {
  bankId: string
  lat: number
  lng: number
  trustScore: number
  status: 'active' | 'flagged' | 'suspended'
}

// Convert lat/lng to 3D position on sphere of radius r
function latLngToVector3(lat: number, lng: number, r: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lng + 180) * (Math.PI / 180)
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  )
}

// Node geometry: sphere
const nodeGeometry = new THREE.SphereGeometry(0.06, 16, 16)

// Node material based on status
const getMaterial = (node: BankNode) => {
  if (node.status === 'suspended') return new THREE.MeshPhongMaterial({ color: 0xEF4444, emissive: 0x8B0000 })
  if (node.status === 'flagged') return new THREE.MeshPhongMaterial({ color: 0xF59E0B, emissive: 0x6B3500 })
  // Active: color by trust score (green → blue)
  const hue = node.trustScore * 120 // 0=red, 120=green
  return new THREE.MeshPhongMaterial({ color: new THREE.Color(`hsl(${hue}, 70%, 50%)`), emissive: new THREE.Color(`hsl(${hue}, 60%, 20%)`) })
}
```

**Update Arc Animation (weight packets traveling to server):**
```typescript
// Animated arc using QuadraticBezierCurve3
function createUpdateArc(from: THREE.Vector3, to: THREE.Vector3, color: number): THREE.Line {
  const mid = from.clone().add(to).multiplyScalar(0.5)
  mid.normalize().multiplyScalar(3.5) // Lift arc above globe

  const curve = new THREE.QuadraticBezierCurve3(from, mid, to)
  const points = curve.getPoints(50)
  const geometry = new THREE.BufferGeometry().setFromPoints(points)
  const material = new THREE.LineBasicMaterial({
    color,
    transparent: true,
    opacity: 0,
  })
  return new THREE.Line(geometry, material)
}

// Animate the arc: packet travels from bank to server
function animateArc(arc: THREE.Line, onComplete: () => void) {
  const material = arc.material as THREE.LineBasicMaterial
  gsap.timeline()
    .to(material, { opacity: 0.8, duration: 0.3 })
    .to(material, { opacity: 0, duration: 0.5, delay: 0.8, onComplete })
}
```

**Pulsing Ring (healthy submission):**
```typescript
// Expanding ring on successful submission
function createPulseRing(position: THREE.Vector3): void {
  const ringGeometry = new THREE.RingGeometry(0.05, 0.08, 32)
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: 0x10B981,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide,
  })
  const ring = new THREE.Mesh(ringGeometry, ringMaterial)
  ring.position.copy(position)
  ring.lookAt(new THREE.Vector3(0, 0, 0))
  scene.add(ring)

  gsap.timeline({ onComplete: () => scene.remove(ring) })
    .to(ring.scale, { x: 4, y: 4, z: 4, duration: 1.2, ease: 'power2.out' })
    .to(ringMaterial, { opacity: 0, duration: 0.5 }, '-=0.5')
}
```

**Poisoning Attack Flash:**
```typescript
// Red explosion on poisoning detection
function triggerPoisoningFlash(nodePosition: THREE.Vector3): void {
  // 1. Node turns red with glow
  const flash = new THREE.PointLight(0xFF0000, 3, 2)
  flash.position.copy(nodePosition)
  scene.add(flash)
  gsap.to(flash, { intensity: 0, duration: 1.5, onComplete: () => scene.remove(flash) })

  // 2. Shockwave ring
  const shockwave = createShockwaveRing(nodePosition)
  gsap.timeline({ onComplete: () => scene.remove(shockwave) })
    .to(shockwave.scale, { x: 8, y: 8, z: 8, duration: 1.0, ease: 'power1.out' })
    .to(shockwave.material, { opacity: 0, duration: 0.5 }, '-=0.5')
}
```

### 7.2 GSAP Animations

**Page Entrance — staggered cards:**
```javascript
// Run on every page mount
gsap.from('.stat-card', {
  y: 20,
  opacity: 0,
  duration: 0.5,
  stagger: 0.08,
  ease: 'power2.out',
  clearProps: 'all',
})
```

**Number Count-Up — all metric numbers:**
```javascript
function animateNumber(el: HTMLElement, target: number, decimals: number = 0) {
  gsap.from({ val: 0 }, {
    val: target,
    duration: 1.5,
    ease: 'power2.out',
    onUpdate: function() {
      el.textContent = this.targets()[0].val.toFixed(decimals)
    }
  })
}
```

**Alert Feed — new item entrance:**
```javascript
// Called when new WebSocket alert arrives
function animateNewAlert(element: HTMLElement) {
  gsap.from(element, {
    x: 40,
    opacity: 0,
    duration: 0.35,
    ease: 'power2.out',
  })
  // Red flash for block decisions
  if (element.dataset.decision === 'block') {
    gsap.to(element, {
      backgroundColor: '#FEE2E2',
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      delay: 0.35,
    })
  }
}
```

**Fraud Score Gauge — needle animation:**
```javascript
function animateGauge(probability: number) {
  const angle = -90 + (probability * 180) // -90 to +90 degrees
  gsap.to('#gauge-needle', {
    rotation: angle,
    transformOrigin: '50% 100%',
    duration: 1.2,
    ease: 'elastic.out(1, 0.5)',
  })
}
```

**Sidebar — active route transition:**
```javascript
// Smooth indicator slide between nav items
gsap.to('#nav-indicator', {
  y: targetY,
  duration: 0.3,
  ease: 'power3.out',
})
```

**Round status — progress bar fill:**
```javascript
gsap.to('#round-progress-bar', {
  width: `${(received / expected) * 100}%`,
  duration: 0.5,
  ease: 'power2.out',
})
```

---

## 8. Backend Services Specification

### 8.1 Fastify API Gateway (`apps/api-gateway/`)

**Technology Stack:**
- Runtime: Node.js 22 LTS
- Framework: Fastify 5.x
- Plugins: @fastify/jwt, @fastify/redis, @fastify/websocket, @fastify/rate-limit, @fastify/swagger
- Validation: Zod + @fastify/type-provider-zod
- ORM: Drizzle ORM (PostgreSQL)
- Inference: ONNX Runtime (model loaded from Redis blob)

**Port:** 3000
**Base path:** `/v1`

**Registered Plugins (in order):**
```
1. fastify-sensible          (error helpers)
2. @fastify/helmet            (security headers)
3. @fastify/cors              (CORS for dashboard)
4. @fastify/rate-limit        (1000 req/s per bank)
5. @fastify/jwt               (JWT auth)
6. @fastify/redis             (model cache + pub/sub)
7. @fastify/websocket         (real-time alerts)
8. drizzle-plugin             (custom, wraps pg pool)
9. @fastify/swagger           (OpenAPI docs)
```

**Auth Flow:**
```
Request → Extract JWT from Authorization header
→ Verify JWT with HS256 + JWT_SECRET
→ Decode bank_id claim
→ Check bank status in Redis cache (fallback: DB)
→ If suspended → 403
→ Attach bank to request.bank
→ Route handler runs
```

### 8.2 Federation Server (`apps/federation-server/`)

**Technology Stack:**
- Runtime: Python 3.12
- Framework: FastAPI + Uvicorn
- Async: asyncio + asyncpg
- IPFS: ipfshttpclient
- Blockchain: web3.py + Polygon Mumbai RPC
- ML: numpy, scipy, scikit-learn (for FLTrust + anomaly detection)
- Background tasks: FastAPI BackgroundTasks + Celery (for long aggregation)

**Port:** 8000

**Core Modules:**
```
aggregation/
  fedavg.py           — weighted average of model weights
  fltrust.py          — FLTrust Byzantine-robust aggregation
  trust_scorer.py     — cosine similarity trust computation

poisoning/
  gradient_monitor.py — 3-layer anomaly detection
  norm_checker.py     — gradient norm outlier detection
  history_tracker.py  — per-bank gradient history (last 10 rounds)

ipfs/
  client.py           — async IPFS add/cat operations

blockchain/
  polygon_client.py   — web3.py wrapper for Polygon
  contracts.py        — smart contract ABI + interaction methods
```

### 8.3 Admin Service (`apps/admin-service/`)

**Technology Stack:**
- Runtime: Python 3.12
- Framework: Django 5.x + Django REST Framework
- Task queue: Celery + Redis
- PDF generation: ReportLab (compliance reports)

**Port:** 8002

**Django Apps:**
```
banks/        — Bank CRUD, onboarding, RSA key registration
rounds/       — Federation round lifecycle management
compliance/   — Report generation (RBI, GDPR, PCI-DSS)
audit/        — Audit trail, log aggregation
```

---

## 9. Database Schema

```sql
-- ─────────────────────────────────────────────
-- BANK REGISTRY
-- ─────────────────────────────────────────────

CREATE TABLE banks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    country_code        CHAR(2) NOT NULL,
    regulator_id        TEXT,
    public_key          TEXT NOT NULL UNIQUE,    -- RSA-4096
    api_key_hash        TEXT NOT NULL,
    tier                TEXT DEFAULT 'standard', -- standard | premium | anchor
    status              TEXT DEFAULT 'pending',  -- pending | active | suspended
    privacy_epsilon     DECIMAL(4,2) DEFAULT 1.0,
    joined_at           TIMESTAMPTZ DEFAULT now(),
    last_active_at      TIMESTAMPTZ
);

-- ─────────────────────────────────────────────
-- FEDERATION ROUNDS
-- ─────────────────────────────────────────────

CREATE TABLE federation_rounds (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_number             INTEGER NOT NULL UNIQUE,
    status                   TEXT DEFAULT 'open',  -- open|aggregating|complete|failed
    global_model_hash        TEXT,
    global_model_cid         TEXT,                 -- IPFS CID
    chain_tx_hash            TEXT,                 -- Polygon tx
    participants_expected    INTEGER NOT NULL,
    participants_received    INTEGER DEFAULT 0,
    aggregation_algo         TEXT DEFAULT 'fltrust',
    global_auc               DECIMAL(6,5),
    global_precision         DECIMAL(6,5),
    global_recall            DECIMAL(6,5),
    global_f1                DECIMAL(6,5),
    started_at               TIMESTAMPTZ DEFAULT now(),
    completed_at             TIMESTAMPTZ
);

-- ─────────────────────────────────────────────
-- MODEL UPDATES (per round, per bank)
-- ─────────────────────────────────────────────

CREATE TABLE model_updates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id            UUID NOT NULL REFERENCES federation_rounds(id),
    bank_id             UUID NOT NULL REFERENCES banks(id),
    weight_delta_cid    TEXT NOT NULL,
    weight_hash         TEXT NOT NULL,
    signature           TEXT NOT NULL,
    dp_epsilon_used     DECIMAL(4,2),
    local_samples_used  INTEGER,
    local_auc           DECIMAL(6,5),
    trust_score         DECIMAL(6,5),
    poisoning_flags     JSONB DEFAULT '[]',
    status              TEXT DEFAULT 'received',  -- received|accepted|rejected|flagged
    submitted_at        TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX idx_model_updates_round_bank ON model_updates(round_id, bank_id);

-- ─────────────────────────────────────────────
-- FRAUD PATTERN REGISTRY
-- ─────────────────────────────────────────────

CREATE TABLE fraud_pattern_registry (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_hash            TEXT NOT NULL UNIQUE,
    pattern_type            TEXT NOT NULL,  -- velocity|mule|card_testing|account_takeover
    first_seen_round        INTEGER,
    last_seen_round         INTEGER,
    detection_count         INTEGER DEFAULT 1,
    reporting_bank_count    INTEGER DEFAULT 1,
    severity                TEXT DEFAULT 'medium',
    active                  BOOLEAN DEFAULT true
);

-- ─────────────────────────────────────────────
-- POISONING EVENTS
-- ─────────────────────────────────────────────

CREATE TABLE poisoning_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    update_id           UUID NOT NULL REFERENCES model_updates(id),
    bank_id             UUID NOT NULL REFERENCES banks(id),
    round_id            UUID NOT NULL REFERENCES federation_rounds(id),
    attack_type         TEXT,  -- gradient_scaling|sign_flip|backdoor|sybil
    anomaly_score       DECIMAL(6,5),
    detection_method    TEXT,  -- fltrust|cosine_similarity|norm_check|statistical
    evidence_payload    JSONB,
    chain_tx_hash       TEXT,
    resolved            BOOLEAN DEFAULT false,
    resolution          TEXT,
    detected_at         TIMESTAMPTZ DEFAULT now()
);

-- ─────────────────────────────────────────────
-- REAL-TIME SCORING LOG (TimescaleDB hypertable)
-- ─────────────────────────────────────────────

CREATE TABLE scoring_requests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_id             UUID NOT NULL REFERENCES banks(id),
    txn_ref_hash        TEXT NOT NULL,
    model_round         INTEGER,
    fraud_probability   DECIMAL(6,5),
    risk_tier           TEXT,     -- low|medium|high|critical
    decision            TEXT,     -- allow|review|block
    shap_values         JSONB,    -- SHAP feature contributions
    latency_ms          INTEGER,
    scored_at           TIMESTAMPTZ DEFAULT now()
);

SELECT create_hypertable('scoring_requests', 'scored_at');

-- ─────────────────────────────────────────────
-- COMPLIANCE REPORTS
-- ─────────────────────────────────────────────

CREATE TABLE compliance_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_id         UUID NOT NULL REFERENCES banks(id),
    report_type     TEXT,  -- rbi_dpsp|gdpr_art30|pci_dss|fiu_ind
    period_start    DATE,
    period_end      DATE,
    content_cid     TEXT,
    generated_at    TIMESTAMPTZ DEFAULT now()
);

-- ─────────────────────────────────────────────
-- SHAP CACHE (pre-computed explanations)
-- ─────────────────────────────────────────────

CREATE TABLE shap_explanations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    score_id        UUID NOT NULL REFERENCES scoring_requests(id),
    feature_values  JSONB NOT NULL,  -- {feature_name: shap_value}
    base_value      DECIMAL(6,5),
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ─────────────────────────────────────────────
-- DRIFT MONITORING
-- ─────────────────────────────────────────────

CREATE TABLE drift_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_from      INTEGER NOT NULL,
    round_to        INTEGER NOT NULL,
    auc_delta       DECIMAL(6,5),
    drift_detected  BOOLEAN DEFAULT false,
    drift_features  JSONB,   -- which features drifted
    alert_sent      BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ─────────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────────

CREATE INDEX idx_scoring_bank_time        ON scoring_requests(bank_id, scored_at DESC);
CREATE INDEX idx_scoring_risk_tier        ON scoring_requests(risk_tier, scored_at DESC);
CREATE INDEX idx_model_updates_bank       ON model_updates(bank_id);
CREATE INDEX idx_model_updates_round      ON model_updates(round_id);
CREATE INDEX idx_poisoning_bank           ON poisoning_events(bank_id);
CREATE INDEX idx_poisoning_round          ON poisoning_events(round_id);
CREATE INDEX idx_fraud_patterns_active    ON fraud_pattern_registry(active, severity);
CREATE INDEX idx_drift_rounds             ON drift_reports(round_from, round_to);
```

---

## 10. ML Pipeline Specification

### 10.1 Feature Engineering (24 Features)

```python
# Feature group 1: Amount (3 features)
amount_log              = log1p(txn.amount)
amount_zscore_30d       = (amount - mean_30d) / (std_30d + 1e-9)
amount_percentile_acct  = percentile rank within account history

# Feature group 2: Velocity (5 features)
txn_count_1h            = transactions in last 1 hour
txn_count_24h           = transactions in last 24 hours
txn_count_7d            = transactions in last 7 days
unique_merchants_24h    = distinct merchant IDs in last 24h
unique_devices_7d       = distinct device fingerprints in last 7d

# Feature group 3: Time (4 features)
hour_of_day             = 0–23
day_of_week             = 0–6
is_weekend              = bool
hours_since_last_txn    = float (999.0 if no history)

# Feature group 4: Channel / Device (4 features)
channel_encoded         = 0=upi, 1=netbanking, 2=card, 3=atm
is_new_device           = bool (not seen in account history)
is_new_merchant         = bool
ip_country_change       = bool

# Feature group 5: MCC (2 features)
mcc_risk_score          = 0.0–1.0 (precomputed lookup)
mcc_is_high_risk        = bool

# Feature group 6: Graph (3 features)
account_pagerank        = float (bank's own txn graph)
shared_device_count     = int (devices shared with flagged accounts)
merchant_fraud_rate_30d = float

# Feature group 7: Rolling (1 feature)
account_fraud_rate_90d  = float (account's personal fraud history)

# TOTAL: 22 base features + 2 graph features = 24 features
```

### 10.2 Model: LightGBM

```python
# Rationale for LightGBM:
# 1. Fastest training on tabular data
# 2. Handles class imbalance with is_unbalance=True
# 3. Sub-millisecond inference (critical for <10ms API target)
# 4. Serializable to string — works with federated weight sharing

params = {
    'objective': 'binary',
    'metric': ['auc', 'binary_logloss'],
    'learning_rate': 0.05,
    'num_leaves': 31,
    'min_child_samples': 20,
    'is_unbalance': True,           # handles fraud class imbalance
    'reg_alpha': 0.1,               # L1 regularization
    'reg_lambda': 0.1,              # L2 regularization
    'feature_fraction': 0.8,        # reduces overfitting
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
}
```

### 10.3 Differential Privacy

```python
# Gaussian Mechanism for (ε, δ)-DP
# Privacy guarantee: no single transaction can be identified from weights

def gaussian_noise_sigma(epsilon: float, delta: float, sensitivity: float) -> float:
    return sensitivity * sqrt(2 * log(1.25 / delta)) / epsilon

# Parameters:
# epsilon (ε): privacy budget — bank configures between 0.1 (max privacy) and 10 (min privacy)
# delta (δ): 1e-5 (standard for financial applications)
# sensitivity: max_grad_norm = 1.0 (gradient clipping threshold)

# DP noise is added to leaf values of the LightGBM trees
# This provides plausible deniability for any individual transaction
```

### 10.4 FedAvg Algorithm

```python
def fedavg(weight_updates: dict[str, ModelWeights], trust_scores: dict[str, float]) -> ModelWeights:
    """
    Weighted average of model weights, with FLTrust trust scores as weights.
    This combines FedAvg aggregation with FLTrust security.
    
    For tree models: concatenate trees, prune duplicates, re-normalize leaf values
    """
    total_trust = sum(trust_scores.values())
    global_model = initialize_empty_model()
    
    for bank_id, weights in weight_updates.items():
        contribution_weight = trust_scores[bank_id] / total_trust
        global_model = merge_weighted(global_model, weights, contribution_weight)
    
    return global_model
```

### 10.5 FLTrust Algorithm

```python
def compute_trust_scores(
    server_gradient: np.ndarray,      # computed from server's small trusted dataset
    bank_gradients: dict[str, np.ndarray]
) -> dict[str, float]:
    """
    FLTrust (NDSS 2021):
    Trust score = ReLU(cosine_similarity(bank_gradient, server_gradient))
    
    - Score 1.0: bank's update perfectly aligns with server's gradient direction
    - Score 0.5: some divergence (different data distribution)
    - Score 0.0: actively opposed to server gradient — REJECTED
    
    Key property: A poisoned update pointing in the WRONG direction gets score 0.
    Coordinated attacks (multiple compromised banks) need to fool the server's
    trusted dataset, which is never revealed to participants.
    """
    scores = {}
    for bank_id, grad in bank_gradients.items():
        cos_sim = dot(server_gradient, grad) / (norm(server_gradient) * norm(grad) + 1e-9)
        scores[bank_id] = max(0.0, cos_sim)
    return scores
```

### 10.6 SHAP Integration

```python
import shap

class ShapExplainer:
    def __init__(self, model: lgb.Booster):
        self.explainer = shap.TreeExplainer(model)
    
    def explain(self, features: np.ndarray, feature_names: list[str]) -> dict:
        shap_values = self.explainer.shap_values(features)
        return {
            'feature_contributions': dict(zip(feature_names, shap_values[0])),
            'base_value': float(self.explainer.expected_value[1]),
            'feature_values': dict(zip(feature_names, features[0])),
        }

# Output example:
# {
#   "feature_contributions": {
#     "is_new_device": 0.31,
#     "txn_count_1h": 0.18,
#     "amount_zscore_30d": -0.04,
#     ...
#   },
#   "base_value": 0.12,
#   "feature_values": { ... }
# }
```

### 10.7 Model Drift Monitoring

```python
# After each federation round, compare current model predictions to reference
# Alert conditions:
ALERT_CONDITIONS = {
    'auc_drop':           0.02,  # AUC dropped by >2% round-over-round
    'precision_drop':     0.03,  # Precision dropped by >3%
    'recall_drop':        0.03,  # Recall dropped by >3%
    'feature_drift':      0.15,  # Wasserstein distance on feature distributions
    'prediction_drift':   0.10,  # KL divergence on fraud probability distribution
}

# Evidently AI report metrics:
metrics = [
    DataDriftPreset(),
    ClassificationPreset(),
    ClassificationQualityMetric(),
    ClassificationRocCurve(),
    ClassificationPrecisionRecallCurve(),
]
```

---

## 11. MLSecOps Specification

### 11.1 Three-Layer Gradient Anomaly Detection

```
Layer 1 — Statistical Norm Check
  Compute L2 norm of each bank's gradient
  Compute z-score of that norm within the round's distribution
  Threshold: z-score > 3.5 → flag as gradient_norm_outlier
  Rationale: A poisoned gradient with gradient scaling has abnormally large norm

Layer 2 — Cosine Similarity vs Round Mean
  Compute mean gradient across all submitted updates
  Compute cosine similarity between each bank's update and round mean
  Threshold: cosine_sim < -0.3 → flag as sign_flip_suspected
  Threshold: cosine_sim < 0.1  → flag as low_cosine_similarity
  Rationale: A backdoor or sign-flip attack points in wrong direction

Layer 3 — Historical Deviation for this Bank
  Maintain per-bank gradient norm history (last 10 rounds)
  Compute deviation of current norm from historical mean
  Threshold: deviation > 4.0 sigma → flag as historical_deviation
  Rationale: A newly-compromised bank changes behavior suddenly

Final anomaly score = max(all layer scores)
Decision:
  score > 0.8 → REJECT update, log poisoning event, write to chain
  score > 0.4 → FLAG for manual review, apply reduced trust score
  score <= 0.4 → ACCEPT
```

### 11.2 Attack Simulation (for Demo)

```python
# simulation/attack_simulator.py

class GradientScalingAttack:
    """Multiplies gradient by 10x — caught by norm outlier layer"""
    def poison(self, gradient: np.ndarray) -> np.ndarray:
        return gradient * 10.0

class SignFlipAttack:
    """Negates gradient completely — caught by cosine similarity layer"""
    def poison(self, gradient: np.ndarray) -> np.ndarray:
        return -gradient

class BackdoorAttack:
    """Adds a specific pattern to make model ignore certain features"""
    def poison(self, gradient: np.ndarray, target_feature_idx: int) -> np.ndarray:
        poisoned = gradient.copy()
        poisoned[target_feature_idx] = -abs(gradient[target_feature_idx]) * 5
        return poisoned

class SybilAttack:
    """Multiple fake bank identities submitting coordinated poisoned updates"""
    def __init__(self, n_sybils: int = 3):
        self.n_sybils = n_sybils
    
    def generate_updates(self, base_gradient: np.ndarray) -> list[np.ndarray]:
        return [SignFlipAttack().poison(base_gradient) for _ in range(self.n_sybils)]
```

---

## 12. Blockchain / Smart Contract Specification

### 12.1 Contract: FedShieldRegistry.sol

**Network:** Polygon Mumbai (testnet) / Polygon Mainnet (production)
**Language:** Solidity ^0.8.20
**Dependencies:** OpenZeppelin 5.x (AccessControl, ReentrancyGuard)

**Roles:**
```
DEFAULT_ADMIN_ROLE  → FedShield team (can register banks, assign roles)
AGGREGATOR_ROLE    → Federation server (can finalize rounds, record events)
BANK_ROLE          → Registered banks (for future on-chain features)
```

**Core Functions:**
```
registerBank(bytes32 bankId)
  → onlyRole(DEFAULT_ADMIN_ROLE)
  → Creates BankRecord
  → Emits BankRegistered

finalizeRound(roundNumber, globalModelHash, globalModelCid, participantCount, poisoningEventCount)
  → onlyRole(AGGREGATOR_ROLE)
  → nonReentrant
  → Validates sequential round numbering
  → Stores FederationRound struct
  → Emits RoundFinalized

recordPoisoningEvent(bankId, roundNumber, attackType, anomalyScore)
  → onlyRole(AGGREGATOR_ROLE)
  → Increments bank's poisoningStrikes
  → Auto-suspends at MAX_STRIKES = 3
  → Emits PoisoningDetected, BankSuspended

verifyRound(roundNumber, claimedHash) → (bool valid, bool finalized)
  → Public view — anyone can verify model integrity

getPoisoningHistory(bankId) → PoisoningRecord[]
  → Public view — full attack history for any bank
```

---

## 13. API Contracts (All Endpoints)

### 13.1 Fastify Scoring API — `/v1/`

```
POST /v1/score/transaction
  Auth: Bearer JWT
  Body: {
    bank_id: UUID,
    txn_ref_hash: string (64 chars, SHA-256 of bank's internal txn ID),
    amount_log: number,
    amount_zscore_30d: number,
    amount_percentile_account: number,
    txn_count_1h: integer,
    txn_count_24h: integer,
    txn_count_7d: integer,
    unique_merchants_24h: integer,
    unique_devices_7d: integer,
    hour_of_day: integer (0-23),
    day_of_week: integer (0-6),
    is_weekend: boolean,
    hours_since_last_txn: number,
    channel_encoded: integer (0-3),
    is_new_device: boolean,
    is_new_merchant: boolean,
    ip_country_change: boolean,
    device_country_change: boolean,
    mcc_risk_score: number (0-1),
    mcc_is_high_risk: boolean,
    account_pagerank: number,
    shared_device_count: integer,
    merchant_fraud_rate_30d: number,
    account_fraud_rate_90d: number
  }
  Response 200: {
    fraud_probability: number (0-1),
    risk_tier: "low" | "medium" | "high" | "critical",
    decision: "allow" | "review" | "block",
    model_round: integer,
    latency_ms: integer,
    shap_values: { [feature_name]: number }  // if explain=true param
  }
  Rate limit: 1000 req/s per bank
  Target latency: p50 < 5ms, p99 < 10ms

POST /v1/score/batch
  Body: { transactions: [...] }  // max 10,000
  Response: { results: [...], total: integer, high_risk_count: integer }

GET /v1/score/explain/:txn_ref_hash
  Response: { shap_values, base_value, feature_values, waterfall_data }

WS /v1/alerts/stream
  Auth: JWT in query param ?token=
  Server sends: { type: "fraud_alert", data: { fraud_probability, risk_tier, decision, txn_ref_hash, scored_at } }
  Server sends: { type: "round_complete", data: { round_number, global_auc } }
  Server sends: { type: "poisoning_detected", data: { bank_id, attack_type, round } }

GET /v1/health
  Response: { status: "ok", model_round: integer, uptime_ms: integer }
```

### 13.2 Federation Server API — `/` (internal, not public-facing)

```
POST /rounds/{round_id}/submit
  Body: ModelUpdateSubmission schema
  Response: { status: "accepted", received: integer }

GET /rounds/current
  Response: RoundStatus schema

POST /rounds/create
  Auth: Admin only
  Body: { expected_participants: integer }

GET /banks/{bank_id}/trust-history
  Response: [{ round: integer, trust_score: number }]

GET /health
  Response: { status, current_round, last_aggregation_at }
```

### 13.3 Admin Service API — `/api/` (Django REST)

```
POST /api/banks/                     → Register new bank
GET  /api/banks/                     → List all banks
GET  /api/banks/{id}/                → Bank detail
PUT  /api/banks/{id}/status/         → Update status (suspend/activate)
GET  /api/banks/{id}/compliance/     → Compliance data for a bank

GET  /api/rounds/                    → List federation rounds
GET  /api/rounds/{id}/               → Round detail with per-bank updates
POST /api/rounds/start/              → Start new round

GET  /api/poisoning/                 → All poisoning events
GET  /api/poisoning/{id}/            → Event detail

POST /api/compliance/generate/       → Trigger report PDF generation
GET  /api/compliance/{id}/download/  → Download generated PDF
```

---

## 14. Real-Time System (WebSocket + Redis)

### 14.1 Redis Channels

```
model:global:current          → current global model weights (msgpack blob)
model:global:round            → current round number (string)
alerts:{bank_id}              → real-time fraud alerts per bank (JSON)
alerts:global                 → aggregation server events (round complete, poisoning)
round:status                  → federation round status updates
leaderboard:trust             → sorted set: bank_id → trust score
```

### 14.2 Event Schema

```typescript
// Fraud Alert (from scoring API → bank's dashboard)
{
  type: "fraud_alert",
  bank_id: UUID,
  txn_ref_hash: string,
  fraud_probability: number,
  risk_tier: "low" | "medium" | "high" | "critical",
  decision: "allow" | "review" | "block",
  scored_at: ISO8601
}

// Round Complete (from federation server → all dashboards)
{
  type: "round_complete",
  round_number: integer,
  global_auc: number,
  participant_count: integer,
  poisoning_count: integer,
  global_model_cid: string,
  chain_tx_hash: string,
  completed_at: ISO8601
}

// Poisoning Detected (from federation server → admin dashboard)
{
  type: "poisoning_detected",
  bank_id: UUID,
  round_number: integer,
  attack_type: string,
  anomaly_score: number,
  detection_method: string,
  detected_at: ISO8601
}
```

### 14.3 WebSocket Client Hook (`useAlertStream.ts`)

```typescript
function useAlertStream(bankId: string) {
  const [alerts, setAlerts] = useState<FraudAlert[]>([])
  
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/v1/alerts/stream?token=${jwt}`)
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'fraud_alert') {
        setAlerts(prev => [msg.data, ...prev].slice(0, 100)) // keep last 100
        // Trigger GSAP animation for new item
        animateNewAlert(msg.data)
      }
    }
    
    ws.onerror = () => setTimeout(() => reconnect(), 3000) // auto-reconnect
    return () => ws.close()
  }, [bankId])
  
  return alerts
}
```

---

## 15. CI/CD & Security Pipeline

### 15.1 GitHub Actions Workflows

**`ci.yml` — runs on every PR:**
```yaml
jobs:
  test-python:
    - pytest apps/federation-server/ ml/ mlsecops/ --cov=. --cov-report=xml
    - pytest packages/bank-sdk-python/
  
  test-node:
    - npm test apps/api-gateway/
    - npm test apps/web/
  
  lint:
    - ruff check . (Python)
    - eslint . (JS/TS)
    - mypy apps/federation-server/ (type checking)
  
  build:
    - docker compose -f docker-compose.dev.yml build --no-cache
```

**`security.yml` — runs on main + PRs:**
```yaml
jobs:
  sast:          → Semgrep (python, js, ts, solidity, secrets)
  bandit:        → Python security issues
  eslint-sec:    → eslint-plugin-security
  trivy-image:   → Container vulnerability scanning (CRITICAL+HIGH)
  trivy-iac:     → Terraform misconfiguration scanning
  trufflehog:    → Secret detection in git history
  zap-dast:      → OWASP ZAP API scan against test environment
  slither:       → Solidity static analysis
```

**`deploy.yml` — runs on main merge:**
```yaml
jobs:
  push-images:   → Push to ECR with git SHA tag
  argocd-sync:   → Trigger ArgoCD to sync Helm releases
  notify:        → Slack notification with deployment summary
```

---

## 16. Infrastructure (IaC)

### 16.1 Terraform — AWS (ap-south-1 / Mumbai)

**Resources provisioned:**
```hcl
# Networking
module.vpc                  → VPC with public/private/database subnets
aws_security_group.api      → Port 3000, 8000, 8002 from ALB only
aws_security_group.rds      → Port 5432 from EKS nodes only
aws_security_group.redis    → Port 6379 from EKS nodes only

# Compute
module.eks                  → EKS 1.31
  api_nodes                 → c6i.xlarge × 3 (Fastify)
  ml_nodes                  → g4dn.xlarge × 1 (ML inference, GPU)

# Database
aws_db_instance.fedshield_pg → PostgreSQL 16 + TimescaleDB
  instance_class: db.r6g.xlarge
  storage: 500GB → max 2TB (auto-scaling)
  multi_az: true
  deletion_protection: true
  backup_retention: 30 days

# Cache
aws_elasticache_replication_group.redis
  node_type: cache.r6g.large
  num_clusters: 3
  automatic_failover: true
  encryption: at-rest + in-transit

# Storage
aws_s3_bucket.fedshield_models
  versioning: enabled
  encryption: SSE-KMS
  lifecycle: expire old versions after 90 days

# CDN
aws_cloudfront_distribution.dashboard
  origins: S3 (static assets) + ALB (API)
  cache policy: aggressive for assets, no-cache for API
```

### 16.2 Kubernetes (Helm Charts)

**Services deployed:**
```
fedshield-api-gateway          → Deployment(3 replicas), HPA(3→20), Service, Ingress
fedshield-federation-server    → Deployment(2 replicas), Service
fedshield-admin-service        → Deployment(2 replicas), Service
fedshield-celery-worker        → Deployment(2 replicas)
fedshield-web                  → Deployment(2 replicas), Service, Ingress (CloudFront)
```

**HPA config for api-gateway:**
```yaml
minReplicas: 3
maxReplicas: 20
metrics:
  - CPU: target 60%
  - Custom: requests_per_second target 800
```

---

## 17. Bank SDK Specification

### 17.1 Python SDK (`pip install fedshield-sdk`)

**Public API:**
```python
from fedshield import FedShieldClient, LocalTrainer, FeatureExtractor

# Initialization
client = FedShieldClient(
    api_key="your-bank-api-key",     # issued by FedShield admin
    server_url="https://api.fedshield.io",
    bank_id="uuid-here",
)

# Training round — call once per configured interval (e.g., daily)
trainer = LocalTrainer(
    client=client,
    dp_epsilon=1.0,             # privacy budget (bank's choice)
    dp_delta=1e-5,
    max_grad_norm=1.0,
)

result = trainer.run_round(
    X_train=feature_matrix,    # np.ndarray, shape (n_transactions, 24)
    y_train=fraud_labels,       # np.ndarray, shape (n_transactions,)
)
# result.round_number, result.global_auc, result.trust_score

# Real-time scoring
extractor = FeatureExtractor()
features = extractor.extract(transaction, account_history, graph_stats)
score = client.score(features)
# score.fraud_probability, score.risk_tier, score.decision, score.shap_values
```

### 17.2 SDK Internals

```python
class LocalTrainer:
    def run_round(self, X_train, y_train):
        # 1. Fetch current global model from server
        global_weights = self.client.fetch_global_model()
        
        # 2. Train locally
        delta = self.trainer.train_round(X_train, y_train, global_weights)
        
        # 3. Apply differential privacy
        delta = self.dp.apply(delta, epsilon=self.dp_epsilon, delta=self.dp_delta)
        
        # 4. Upload to IPFS
        cid = self.ipfs.upload(encrypt(delta, self.bank_private_key))
        
        # 5. Sign the hash
        weight_hash = sha256(delta)
        signature = rsa_sign(weight_hash, self.bank_private_key)
        
        # 6. Submit to server
        return self.client.submit_update(
            round_id=current_round,
            weight_delta_cid=cid,
            weight_hash=weight_hash,
            signature=signature,
            dp_epsilon_used=self.dp_epsilon,
            local_samples_used=len(X_train),
            local_auc=self.compute_local_auc(X_train, y_train),
        )
```

---

## 18. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Bank must train ML model entirely on local infrastructure; no raw data leaves the bank | P0 |
| FR-02 | Weight delta must be encrypted before upload to IPFS | P0 |
| FR-03 | Every weight submission must include RSA-4096 digital signature | P0 |
| FR-04 | Aggregation server must verify signature before processing any update | P0 |
| FR-05 | FLTrust algorithm must assign trust scores to all submitted updates | P0 |
| FR-06 | Three-layer gradient anomaly detection must run before aggregation | P0 |
| FR-07 | Poisoned updates must be rejected before contributing to global model | P0 |
| FR-08 | Every completed federation round must be anchored on Polygon blockchain | P0 |
| FR-09 | Every poisoning event must be written on-chain within the round transaction | P0 |
| FR-10 | Scoring API must return decision in <10ms p99 latency | P0 |
| FR-11 | Scoring API must support 1,000 requests/second per bank | P0 |
| FR-12 | Differential privacy must be configurable per bank (epsilon, delta) | P1 |
| FR-13 | Real-time fraud alerts must be delivered via WebSocket within 100ms of scoring | P1 |
| FR-14 | SHAP explanation must be computable for any scoring decision on request | P1 |
| FR-15 | Compliance PDF reports must be generatable for RBI, GDPR, PCI-DSS, FIU-IND | P1 |
| FR-16 | Dashboard must show Three.js network globe with real-time node updates | P1 |
| FR-17 | Model drift must be detected and alerted after each federation round | P1 |
| FR-18 | Multi-bank simulation must be runnable locally with docker-compose.simulation.yml | P2 |
| FR-19 | Bank SDK must be installable as pip package with 3-line integration | P2 |
| FR-20 | SHAP waterfall chart must render in dashboard's Explainability page | P2 |
| FR-21 | Attack simulation scripts must be runnable for demo purposes | P2 |
| FR-22 | Graph-based fraud detection (account network PageRank) must be computed bank-side | P2 |

---

## 19. Non-Functional Requirements

### Performance
```
Scoring API latency:      p50 < 5ms, p95 < 8ms, p99 < 10ms
Scoring throughput:       1,000 TPS per bank, 10,000 TPS global
Aggregation time:         < 60 seconds for 50-bank round
WebSocket delivery:       < 100ms from score to alert delivery
Dashboard load time:      < 2 seconds FCP, < 3.5 seconds LCP
Three.js frame rate:      60 FPS on Chrome (mid-range laptop)
```

### Security
```
All traffic:              TLS 1.3 minimum
Bank authentication:      RSA-4096 digital signatures + JWT
API authentication:       JWT HS256, 1-hour expiry
Secret management:        AWS Secrets Manager in production
Container images:         No CRITICAL vulnerabilities (Trivy gate)
SAST:                     Zero high-severity Semgrep findings on main
Smart contract:           Slither scan must pass before deploy
```

### Reliability
```
API availability:         99.9% SLA
Database:                 Multi-AZ PostgreSQL, automated backups
Redis:                    3-node cluster with automatic failover
Recovery time objective:  < 15 minutes
Recovery point objective: < 5 minutes
Aggregation:              Idempotent — safe to retry if failed mid-round
```

### Observability
```
Metrics:    Prometheus + Grafana (latency, throughput, error rate, AUC)
Logging:    Structured JSON logs → CloudWatch → Grafana Loki
Tracing:    OpenTelemetry → Jaeger (distributed request tracing)
Alerts:     PagerDuty integration for P0 incidents
```

### Scalability
```
Banks:          Support 1–500 participating banks
Transactions:   10,000 TPS sustained (TimescaleDB hypertable)
Storage:        IPFS for model artifacts (unlimited), S3 backup
Horizontal:     All services stateless, HPA configured
```

---

## 20. Feature Roadmap (All Scope — Included as Core)

### Phase 1 — Core MVP (Weeks 1–4)
- [ ] Federated learning pipeline (local training → weight submission → aggregation)
- [ ] FedAvg aggregation
- [ ] Scoring API with LightGBM inference
- [ ] Basic React dashboard (Overview, Rounds, Alerts pages)
- [ ] PostgreSQL schema with all tables
- [ ] Docker Compose local dev environment
- [ ] Bank SDK (Python) — basic version

### Phase 2 — Security Layer (Weeks 5–6)
- [ ] RSA-4096 signature verification
- [ ] FLTrust Byzantine-robust aggregation
- [ ] Three-layer gradient anomaly detection
- [ ] Poisoning events table + admin UI
- [ ] Polygon blockchain integration (round finalization)
- [ ] Smart contract deployment (Polygon Mumbai)

### Phase 3 — Privacy & Intelligence (Weeks 7–8)
- [ ] Differential privacy noise injection
- [ ] Configurable epsilon per bank
- [ ] SHAP explainability integration
- [ ] SHAP waterfall chart component
- [ ] Explainability page in dashboard
- [ ] Fraud pattern registry

### Phase 4 — Real-Time & 3D UI (Weeks 9–10)
- [ ] Three.js Network Globe (full spec from Section 7)
- [ ] GSAP animations throughout dashboard
- [ ] WebSocket real-time alert feed
- [ ] Multi-bank simulation (docker-compose.simulation.yml)
- [ ] Attack simulation scripts (all 4 attack types)
- [ ] Poisoning security page with D3 timeline

### Phase 5 — Graph & Drift (Weeks 11–12)
- [ ] Graph-based fraud detection (NetworkX, PageRank, shared device detection)
- [ ] Evidently drift monitoring after each round
- [ ] Drift reports table + dashboard alerts
- [ ] Analytics page (all 7 charts)
- [ ] Bank contribution heatmap (GitHub-style)

### Phase 6 — Compliance & SDK Polish (Weeks 13–14)
- [ ] Compliance report PDF generation (ReportLab)
- [ ] Four report types: RBI DPSP, GDPR Art. 30, PCI-DSS, FIU-IND
- [ ] Compliance page in dashboard
- [ ] Audit trail timeline component
- [ ] Bank SDK PyPI package (`pip install fedshield-sdk`)
- [ ] Bank SDK Node.js npm package

### Phase 7 — Production Hardening (Weeks 15–16)
- [ ] Terraform AWS infrastructure
- [ ] Kubernetes Helm charts
- [ ] ArgoCD GitOps setup
- [ ] Full CI/CD security pipeline
- [ ] Load testing (k6): 1,000 TPS sustained
- [ ] Penetration testing checklist
- [ ] OpenAPI documentation (Swagger UI)
- [ ] README with full getting-started guide

---

## 21. Success Metrics

| Metric | Baseline (isolated bank) | Target (FedShield, 10 rounds) |
|--------|--------------------------|-------------------------------|
| AUC — small fintech | 0.71 | ≥ 0.92 |
| AUC — large bank | 0.89 | ≥ 0.96 |
| AUC improvement | — | +0.21 average |
| Fraud detection rate | 68% | ≥ 89% |
| False positive rate | 12% | ≤ 4% |
| Scoring API latency (p99) | — | < 10ms |
| Poisoning attack detection rate | 0% | ≥ 95% |
| Compliance report generation | Manual (weeks) | < 30 seconds |
| Cross-bank fraud ring detection | 0% (invisible) | ≥ 70% |

---

## 22. Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Coordinated poisoning (multiple compromised banks) | Medium | Critical | FLTrust server-side root dataset; requires compromising server's trusted data |
| Model inversion (reconstruct transactions from weights) | Low | High | Differential privacy (ε=1.0) makes reconstruction statistically impossible |
| Sybil attack (one party controls many fake banks) | Medium | High | Admin-controlled onboarding with regulator ID verification |
| IPFS unavailability | Medium | High | S3 fallback mirror; CID-addressed so content is verifiable from any source |
| Polygon network congestion | Low | Medium | Gas price oracle + retry logic; events queue during congestion |
| Data drift making global model worse | Medium | Medium | Evidently drift monitoring; automatic rollback to previous round if AUC drops >5% |
| Low participation (few banks join) | High | Medium | Free tier, open-source SDK, regulatory sandbox partnership |
| DP noise degrading model accuracy | Medium | Low | ε=1.0 chosen to balance privacy and AUC; bank can tune higher if comfortable |

---

## 23. Demo Script (5-Minute)

### Minute 1 — The Problem
```
"Here's a small fintech with 10,000 customers.
 [Show isolated bank dashboard — AUC 0.71]
 Their fraud model is trained on their own data only.
 They're missing 78% of cross-bank fraud patterns.
 This is every small bank in India."
```

### Minute 2 — The Solution
```
"They join FedShield.
 [Open Three.js globe — show bank node appearing]
 They run: trainer.run_round(X_train, y_train)
 [Open Wireshark — show ONLY weight bytes and IPFS CID in network traffic]
 Zero transaction data. Zero account IDs. Just math.
 [Show round completing on dashboard — AUC jumps to 0.92]"
```

### Minute 3 — The Attack Defense
```
"Now let's say Bank Z is compromised.
 [Run: python attack_simulator.py --type gradient_scaling --bank bank_z]
 [Watch Three.js globe — red flash on bank Z node]
 [Show poisoning events table — 'REJECTED' badge]
 [Show Polygon explorer — transaction hash with evidence permanently on chain]
 Bank Z is automatically suspended after 3 strikes.
 The attack never touched the global model."
```

### Minute 4 — The Compliance
```
"An RBI inspector wants to audit this.
 [Click 'Generate RBI DPSP Report']
 [30 seconds later — PDF downloads]
 Page 1: What data left the bank? NONE.
 Page 2: Which rounds participated in? Rounds 1–42.
 Page 3: On-chain hash of every model update — verifiable forever.
 This is the only fraud system in India that is audit-ready by design."
```

### Minute 5 — The Numbers
```
"Before FedShield — isolated:    AUC 0.71
 After 10 federation rounds:     AUC 0.94
 That 0.23 difference in AUC =   $400,000 saved annually for a mid-size fintech.
 
 FedShield is the first open-source federated fraud intelligence network.
 Small fintechs get HDFC-level detection without giving anyone their data.
 That's the product."
```

---

## 24. Winning Sentence

> **FedShield is the first open-source federated fraud intelligence network — banks train ML models locally on their own data, share only weight updates secured by differential privacy and Byzantine-robust aggregation, and the immutable on-chain audit trail makes model poisoning attacks permanently prosecutable.**

> **Small fintechs get HDFC-level fraud detection without giving anyone their data.**

---

## APPENDIX A — Technology Stack Summary

| Layer | Technology | Version | Reason |
|-------|-----------|---------|--------|
| Frontend framework | React | 19 | Concurrent features, server components |
| Build tool | Vite | 6.x | Sub-second HMR |
| 3D graphics | Three.js | r165 | WebGL globe + network visualization |
| Animation | GSAP | 3.12 | Professional-grade timeline animations |
| State | Zustand | 5.x | Lightweight, no boilerplate |
| Data fetching | SWR | 2.x | Real-time with WebSocket integration |
| Charts | Recharts + D3 | latest | Recharts for standard charts, D3 for custom |
| Scoring API | Fastify | 5.x | Fastest Node.js HTTP framework (<10ms) |
| Aggregation server | FastAPI | 0.115 | Async Python, excellent for ML integration |
| Admin | Django REST | 5.x | Batteries-included, Celery integration |
| ML model | LightGBM | 4.x | Fastest tabular inference, tree serialization |
| Privacy | python-dp | 1.x | Gaussian mechanism DP |
| Explainability | SHAP | 0.46 | TreeExplainer for LightGBM |
| Drift monitoring | Evidently AI | 0.4 | ML monitoring, DataDrift presets |
| Blockchain | Polygon | Mumbai/Mainnet | Low gas, fast finality |
| Smart contracts | Solidity | 0.8.20 | OpenZeppelin security patterns |
| Contract tooling | Hardhat | 2.x | Testing + deployment |
| IPFS | Kubo | 0.27 | Content-addressed model storage |
| Database | PostgreSQL + TimescaleDB | 16 | Time-series scoring logs |
| Cache | Redis | 7 | Model cache + pub/sub for WebSocket |
| Container | Docker | 25 | Dev + test environments |
| Orchestration | Kubernetes | 1.31 | Production workloads |
| IaC | Terraform | 1.8 | AWS infrastructure |
| GitOps | ArgoCD | 2.10 | Continuous deployment |
| CI/CD | GitHub Actions | — | Full security pipeline |
| Monitoring | Grafana + Prometheus | — | Metrics + dashboards |
| Tracing | OpenTelemetry + Jaeger | — | Distributed tracing |
| Graph analysis | NetworkX | 3.x | Bank-side account graph PageRank |

---

## APPENDIX B — Environment Variables

```bash
# api-gateway
DATABASE_URL=postgres://fedshield:password@postgres:5432/fedshield
REDIS_URL=redis://:password@redis:6379
JWT_SECRET=your-jwt-secret-min-32-chars
ML_ENGINE_URL=http://ml-engine:8001
PORT=3000

# federation-server
DATABASE_URL=postgres://fedshield:password@postgres:5432/fedshield
REDIS_URL=redis://:password@redis:6379
IPFS_URL=http://ipfs:5001
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
CONTRACT_ADDRESS=0x...
AGGREGATOR_PRIVATE_KEY=0x...  # Polygon wallet key
AGGREGATOR_PUBLIC_KEY=...     # RSA public key for FLTrust root dataset signing
PORT=8000

# admin-service
DATABASE_URL=postgres://fedshield:password@postgres:5432/fedshield
SECRET_KEY=your-django-secret-key
CELERY_BROKER_URL=redis://:password@redis:6379/1
PORT=8002

# web (frontend)
VITE_API_URL=https://api.fedshield.io
VITE_ADMIN_URL=https://admin.fedshield.io
VITE_WS_URL=wss://api.fedshield.io
```

---

## APPENDIX C — Local Development Quick Start

```bash
# 1. Clone repository
git clone https://github.com/team-bugbytes/fedshield.git
cd fedshield

# 2. Copy environment template
cp .env.example .env

# 3. Start all services
docker compose -f docker-compose.dev.yml up -d

# 4. Run database migrations
docker compose exec admin-service python manage.py migrate

# 5. Seed demo data (3 simulated banks, 10 rounds)
docker compose exec federation-server python scripts/seed_demo.py

# 6. Open dashboard
open http://localhost:5173

# 7. Run multi-bank simulation (optional, for demo)
docker compose -f docker-compose.simulation.yml up

# 8. Run poisoning attack simulation (for demo)
python simulation/attack_simulator.py --banks 5 --attack gradient_scaling --rounds 3
```

---

*Document version: 2.0 — Final*
*Team: BugBytes (Alok Kumar Sahoo, Apoorva Puranik, Nirmala Patole, Vaibhavi Naik)*
*Institution: A.P. Shah Institute of Technology, Mumbai*
*Hackathon: HackUp 2026*
