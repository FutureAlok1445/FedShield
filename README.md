# 🛡️ FedShield: Enterprise-Grade Federated Fraud Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Node.js 22](https://img.shields.io/badge/Node.js-22-green.svg)](https://nodejs.org/)
[![React 19](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-darkgray.svg)](https://soliditylang.org/)

FedShield is a next-generation, privacy-preserving **Federated Learning Platform** designed specifically for the global financial sector. It enables a consortium of banks to collaboratively train a highly accurate, generalized fraud detection model **without ever sharing sensitive raw customer transaction data or Personally Identifiable Information (PII).**

By exchanging only mathematically encrypted model weight updates (gradients) rather than raw databases, FedShield effectively destroys the data silos that protect organized fraud rings. It allows financial institutions to detect coordinated, cross-border attacks in real-time while strictly maintaining compliance with stringent data privacy regulations such as **GDPR (Europe)**, **CCPA (California)**, and the **RBI DPSP (India)**.

---

## 📖 Table of Contents

1. [The Business Case & Problem Statement](#1-the-business-case--problem-statement)
2. [The FedShield Solution (Core Pillars)](#2-the-fedshield-solution-core-pillars)
3. [Deep Dive: Mathematical Security & Defenses](#3-deep-dive-mathematical-security--defenses)
4. [System Architecture Visualized](#4-system-architecture-visualized)
5. [Exhaustive Repository Structure](#5-exhaustive-repository-structure)
6. [Step-by-Step Data Flow Lifecycle](#6-step-by-step-data-flow-lifecycle)
7. [User Interface & GUI Overview](#7-user-interface--gui-overview)
8. [Environment Setup & Deployment Guide](#8-environment-setup--deployment-guide)
9. [API Documentation Reference](#9-api-documentation-reference)
10. [Simulation & Testing](#10-simulation--testing)

---

## 1. The Business Case & Problem Statement

### The "Siloed Knowledge" Problem
Organized fraud rings execute sophisticated attacks by distributing small, seemingly legitimate transactions across multiple banks. For example:
- Bank A sees a $500 transfer (Looks normal).
- Bank B sees a $500 transfer (Looks normal).
- Bank C sees a $500 transfer (Looks normal).

In isolation, traditional ML models at each bank fail to flag these transactions. However, if that same entity is making simultaneous $500 transfers across 20 different banks within 5 minutes, it is a highly coordinated attack.

### The Regulatory Roadblock
Why don't banks just share their transaction data to catch these rings? **Because it is illegal.** Data privacy laws strictly prohibit financial institutions from pooling raw customer data (names, account balances, transaction histories) into centralized databases.

---

## 2. The FedShield Solution (Core Pillars)

FedShield solves this paradox using a combination of cutting-edge cryptography, distributed AI, and zero-trust networking:

1. **Federated Learning (LightGBM):** Instead of centralizing data, FedShield distributes the AI. Banks train a LightGBM ML model locally on their own secure, on-premise data. They only export the resulting mathematical "knowledge" (the gradients/leaf values).
2. **Differential Privacy (DP):** Before the gradients leave the bank, the SDK injects calibrated Gaussian noise. This ensures that even if a gradient is intercepted, adversaries cannot execute a "Model Inversion Attack" to reverse-engineer individual transactions.
3. **Byzantine-Robust Aggregation (FLTrust):** Standard Federated Averaging (FedAvg) can be destroyed if a single bank is hacked and sends poisoned data. FedShield utilizes the **FLTrust** algorithm to mathematically verify the integrity of incoming gradients before averaging them.
4. **Blockchain Auditability:** The final, aggregated global model hash is permanently anchored to the Polygon Blockchain, providing regulators with an immutable, cryptographic audit trail proving compliance.

---

## 3. Deep Dive: Mathematical Security & Defenses

To truly understand the enterprise readiness of FedShield, you must understand the mathematics securing its data pipeline.

### 3.1. Differential Privacy (The Gaussian Mechanism)
To guarantee DP, the Bank SDK limits the influence of any single transaction on the model:
- **Sensitivity ($S$):** The gradient is clipped to a maximum L2 norm (e.g., $S = 1.0$).
- **Variance ($\sigma^2$):** The system computes the required noise standard deviation based on the strict privacy budget ($\epsilon$): $\sigma = \frac{S \sqrt{2 \ln(1.25/\delta)}}{\epsilon}$
- **Execution:** $\Delta w_{private} = \text{clip}(\Delta w, S) + \mathcal{N}(0, \sigma^2)$

### 3.2. FLTrust Aggregation (Byzantine Robustness)
If a malicious actor compromises a bank and attempts a "Sign-Flip Attack" or "Gradient Scaling Attack" to destroy the global model, FedShield neutralizes it:
- The server maintains a small, highly secure root dataset to compute a reference "golden" gradient ($g_0$).
- When Bank $i$ submits its gradient ($g_i$), the server computes the **Cosine Similarity** to check the directional alignment:
  $c_i = \frac{g_0 \cdot g_i}{\|g_0\| \|g_i\|}$
- **Trust Score:** The system applies a ReLU function. If a bank's gradient moves in the opposite direction of the trusted gradient, its trust score is zeroed out: $T_i = \max(0, c_i)$
- **Aggregation:** Gradients are scaled by their Trust Score. Honest banks are merged; malicious banks are discarded.

### 3.3. The 3-Layer Anomaly Detector
Before a gradient even reaches the FLTrust aggregator, it must pass three strict gates:
1. **Norm Check:** Is the gradient magnitude a statistical outlier? ($Z_{score} > 3.5$)
2. **Directional Check:** Does the cosine similarity against the round's mean indicate a sign-flip attack? ($c_i < -0.3$)
3. **Historical Deviation:** Has this specific bank drastically changed its gradient distribution compared to its last 10 rounds? ($> 4\sigma$ deviation).

---

## 4. System Architecture Visualized

```mermaid
graph TD
    subgraph "Bank Environments (On-Premise / Edge)"
        SDK_A[FedShield Python SDK]
        SDK_B[FedShield Python SDK]
        SDK_A --> |1. Train LightGBM| Model_A[(Local Model)]
        SDK_B --> |1. Train LightGBM| Model_B[(Local Model)]
        Model_A --> |2. Inject DP Noise & Sign RSA| Payload_A[Encrypted Gradient]
        Model_B --> |2. Inject DP Noise & Sign RSA| Payload_B[Encrypted Gradient]
    end

    subgraph "FedShield Central Cloud"
        Gateway[API Gateway - Fastify / Node.js]
        Admin[Admin Service - Django]
        FedServer[Federation Server - FastAPI]
        
        Payload_A -.-> |HTTPS POST| FedServer
        Payload_B -.-> |HTTPS POST| FedServer
        
        FedServer --> |3. RSA Verify & 3-Layer Defense| FLTrust[FLTrust Aggregator]
        FLTrust --> |4. Average Trust Scores| Global[Global Super Model]
    end

    subgraph "Blockchain & Compliance"
        Global --> |5. Hash Anchor| Polygon[Polygon L2 Smart Contract]
        Admin --> |6. ReportLab| PDF[Regulatory PDFs]
    end
    
    subgraph "Real-Time Transaction Scoring"
        Gateway --> |Sub 10ms Inference| Redis[Redis Pub/Sub]
        Redis --> |WebSocket Stream| Dashboard[React 3D Dashboard]
    end
```

---

## 5. Deep-Dive Repository Structure & Component Logic

Every file in FedShield serves a distinct architectural purpose. Here is the complete breakdown of how the system is constructed and the internal logic of each component.

### `/.github/workflows/` (CI/CD Pipeline)
- `ci.yml`: Automates testing. Ensures no broken code is merged.
- `security.yml`: Essential for a finance app. Runs **TruffleHog** to catch leaked API keys, **Slither** to detect vulnerabilities in the Solidity smart contract, and **ESLint security plugins** to catch XSS/Injection vectors in the Node.js API.

### `/apps/admin-service/` (Django Admin API)
The relational brain of the system. It handles state that requires persistence and relational queries (Users, Banks, Compliance).
- `admin_service/settings.py`: Configures Django. It implements **Django REST Framework (DRF)** using a hybrid of Session Authentication (for the web admin panel) and Token Authentication (for server-to-server API calls).
- `banks/models.py`: Defines the `Bank` database schema. It stores the bank's RSA `public_key` used to verify their identity, and tracks their `privacy_epsilon` (how much noise they apply to their data).
- `banks/views.py`: API endpoints. Protected by `@permission_classes([IsAuthenticated])` to ensure only the central consortium authority can register or suspend banks.
- `audit/models.py`: Defines analytical schemas such as the `ScoringRequest` (which logs every transaction decision and its latency) and `DriftReport` (which tracks if the AI model's accuracy is decaying over time).
- `compliance/tasks.py`: Contains asynchronous **Celery** workers. Instead of blocking the API, when a regulator requests a GDPR report, this worker spins up in the background and uses the **ReportLab** library to dynamically draw a secure PDF proving the bank participated using Differential Privacy without leaking PII.

### `/apps/api-gateway/` (Fastify Real-time Gateway)
Built in Node.js/Fastify for extreme throughput, handling the sub-10ms real-time transaction scoring.
- `src/index.js`: Bootstraps the server. It registers `helmet` for HTTP header security, rate limiters to prevent DDoS, and an explicit CORS whitelist so only authorized domains can hit the API.
- `src/inference/onnxRunner.js`: The high-speed scoring engine. It maps incoming JSON transactions to the exact 24 canonical ML features, multiplies them by their trained weights, applies a Sigmoid activation function, and calculates the final `fraud_probability` (0.0 to 1.0). It also computes SHAP values (feature importance) for explainability.
- `src/routes/score.js`: The `/v1/score/transaction` endpoint. It verifies the bank's JWT token, calls `onnxRunner.js`, and immediately publishes the result to Redis.
- `src/routes/alerts.js`: Opens a WebSocket connection. It subscribes to the Redis Pub/Sub channels and streams active fraud alerts directly to the React dashboard in real-time.
- `src/plugins/db.js`: Implements a **fail-closed** architecture using a PostgreSQL connection pool. If the database connection drops, the system defaults to a safe "unknown" state rather than failing open and allowing fraudulent transactions through.

### `/apps/federation-server/` (FastAPI Aggregation Engine)
Written in Python/FastAPI because it requires heavy mathematical computation (Numpy/SciPy) to aggregate the AI models.
- `main.py`: The entry point. It manages the state of the FL "rounds". When a bank submits data, it enforces strict API Key auth, uses the `cryptography` library to cryptographically verify the RSA-4096 signature against the bank's public key, and runs strict `NaN/Inf` checks to ensure hackers haven't sent "Not-a-Number" payloads to crash the server's math engine.
- `aggregation/fltrust.py`: The core defense mechanism. Instead of blindly averaging data, it calculates the **Cosine Similarity** between the bank's gradient and a trusted root gradient. If the angle is too wide, the bank is assigned a Trust Score of 0.0, neutralizing them.
- `poisoning/gradient_monitor.py`: A 3-layer anomaly detector. It computes the L2 Norm (magnitude) of the gradients to catch "Scaling Attacks" and calculates Z-scores to identify statistical outliers before they reach the aggregator.
- `poisoning/history_tracker.py`: Maintains a sliding window of historical bank behaviors. If a bank was historically honest but suddenly acts erratically, it flags a 4-sigma deviation.
- `blockchain/polygon_client.py`: Uses the `web3.py` library. After a successful round, it takes the SHA-256 hash of the final model and signs a transaction to the Polygon blockchain. This provides an immutable receipt that regulators can audit.

### `/packages/bank-sdk-python/` (Client Integration SDK)
The library distributed to participating banks to install inside their own firewalls.
- `fedshield/features.py`: The **Single Source of Truth**. It contains the exact logic to extract 24 specific features (amount, velocity, geo-distance, MCC risk) from raw transactions, ensuring every bank trains on identically structured data.
- `fedshield/trainer.py`: Orchestrates the local AI training using **LightGBM**. It automatically handles 80/20 train-validation splitting. Crucially, it uses `scale_pos_weight` to handle the extreme class imbalance typical in fraud detection (where 99% of transactions are legitimate). It extracts the model's leaf values and serializes them to raw bytes (avoiding Python's `pickle` library, which is vulnerable to Remote Code Execution).
- `fedshield/privacy.py`: Implements the Differential Privacy Gaussian Mechanism. It clips the gradients to a maximum norm and injects mathematically calibrated noise based on the $\epsilon$ budget to protect customer privacy.
- `fedshield/client.py`: A secure HTTP wrapper using `requests.Session`. It automatically hashes the noisy gradient, signs it with the bank's private RSA key, and submits the payload to the Federation Server.

### `/contracts/` (Blockchain Smart Contracts)
- `FedShieldRegistry.sol`: Written in Solidity and deployed to Polygon L2. It acts as the ultimate source of truth. It stores the `modelHash` of every completed round via `finalizeRound()`. It also contains the `recordPoisoningEvent()` function, which acts as a judicial ledger. It implements an automatic **3-strike rule**: if a bank is caught submitting poisoned data 3 times, the contract automatically flags `isBankSuspended = true`, locking them out of the network permanently.

### `/apps/web/` (React Dashboard)
- `src/components/three/NetworkGlobe.tsx`: Uses `three.js` to render a 3D WebGL globe. It plots banks by coordinates and mathematically draws quadratic bezier curves across the sphere to visualize cross-border fraud in real-time.
- `src/animations/gsap.ts`: Uses GSAP (GreenSock) for cinematic animations, managing complex UI timelines so elements don't just pop in, but glide smoothly.
- `src/pages/AnalyticsPage.tsx`: Implements `recharts` to draw complex SVG data visualizations (Area charts for Latency SLAs, Dual-Line charts for AUC accuracy trends).
- `src/hooks/useAlertStream.ts`: A custom React hook that manages the WebSocket connection, featuring automatic exponential backoff to gracefully reconnect if the server goes down.

### `/simulation/` (Testing & Benchmarking)
- `bank_simulator.py`: A live CLI simulator that imports the SDK and mimics an entire federation locally. It spawns honest banks and malicious banks (executing sign-flip, scaling, and sybil attacks) to definitively prove that the FLTrust algorithm and Anomaly Detectors function perfectly in real-world adversarial conditions.

---

## 6. Step-by-Step Data Flow Lifecycle

1. **Round Initiation:** Admin Service calls Federation Server `/rounds/create`. Status is set to `open`.
2. **Local Extraction:** Bank A receives raw transactions. The SDK `FeatureExtractor` converts them into standardized 24-dimensional arrays.
3. **Local Training:** Bank A's SDK trains a local LightGBM model (`trainer.py`). It splits the data 80/20, handles fraud imbalance, and extracts the model's leaf decision values.
4. **Privacy Encryption:** The SDK clips the leaf values to a maximum norm and applies Gaussian DP noise.
5. **Cryptography:** The noisy gradient is hashed via SHA-256 and signed with the Bank's RSA-4096 Private Key.
6. **Submission:** The payload (Hash, Signature, DP Epsilon) is POSTed to the Federation Server.
7. **Verification & Defense:** The Federation Server verifies the RSA signature using the bank's registered Public Key. It runs the NaN/Inf guards, and passes it through the 3-Layer Anomaly Detector. If flagged, the bank is given a strike on the blockchain.
8. **Aggregation:** Once the `expected_participants` threshold is met, the server computes the `SERVER_GRADIENT` on its trusted dataset, assigns trust scores to all banks, scales their gradients, and averages them.
9. **Anchoring:** The final global model hash is pushed to the Polygon blockchain, and the API Gateway begins using the new weights for real-time sub-10ms scoring.

---

## 7. User Interface & GUI Overview

The FedShield Web Dashboard (built with React 19, Vite, Three.js, and GSAP) provides fraud analysts with a cinematic, real-time command center.

### The Dashboard Layout (ASCII Map)
```text
+-----------------------------------------------------------------------------+
|  FedShield OS v1.0   [ Dashboard ] [ Analytics ] [ Network ] [ Admin ]      |
+-----------------------------------------------------------------------------+
| +-------------------------+ +---------------------------------------------+ |
| |  GLOBAL THREAT LEVEL    | |                                             | |
| |  [====      ] MEDIUM    | |                                             | |
| +-------------------------+ |           (Interactive 3D Globe)            | |
| |  ACTIVE BANKS           | |              * Bank A (NY)                  | |
| |  [ 12 / 15 Online ]     | |                 \                           | |
| +-------------------------+ |                  \ (Fraud Arc)              | |
| |  FL ROUND STATUS        | |                   \                         | |
| |  Round #42 - Aggregating| |              * Bank B (London)              | |
| +-------------------------+ |                                             | |
|                             +---------------------------------------------+ |
| +-------------------------------------------------------------------------+ |
| | LIVE ALERT FEED (WebSocket)                                             | |
| | > [CRITICAL] Cross-border velocity anomaly detected (Bank A -> Bank C)  | |
| | > [WARNING]  Bank B submitted gradient with low cosine similarity.      | |
| | > [INFO]     Round 41 model anchored to Polygon: 0x9f8a...2b4c          | |
| +-------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------+
```

### GUI Component Breakdown
1. **The Network Globe (Three.js):** A high-fidelity, interactive 3D globe. Connected banks are rendered as glowing nodes. When cross-border fraud is detected, quadratic bezier arcs shoot across the globe, accompanied by expanding pulse rings.
2. **GSAP Animations:** The dashboard uses GSAP (GreenSock) to provide smooth, professional staggered entrances, animated number count-ups for KPIs, and fluid gauge charts.
3. **Analytics (Recharts):** Complex D3.js/Recharts implementations displaying live AUC Trends, FLTrust Score bar charts, and Gateway Latency area graphs.
4. **Alert Stream:** A live, auto-scrolling terminal feed powered by a resilient WebSocket hook (`useAlertStream`) with exponential backoff.

---

## 8. Environment Setup & Deployment Guide

FedShield is architected as a modern microservices stack. Follow these instructions carefully to spin up the entire cluster locally.

### Prerequisites
- Node.js 22 LTS
- Python 3.12+
- Docker & Docker Compose
- 16GB+ RAM (Recommended for running all services locally simultaneously)

### 8.1. Configure Environment Variables
Create a `.env` file in the root directory. This is the **exact, complete** configuration required to run the stack locally.

```env
# ─── API Gateway (Fastify) ────────────────────────────
DATABASE_URL=postgres://fedshield:password@localhost:5432/fedshield
REDIS_URL=redis://localhost:6379
JWT_SECRET=fedshield-super-secure-dev-jwt-secret-32chars
PORT=3000

# ─── Federation Server (FastAPI) ─────────────────────
FEDERATION_API_KEY=dev-federation-key
IPFS_URL=http://localhost:5001
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
CONTRACT_ADDRESS=  # Leave blank to safely bypass blockchain in local dev
AGGREGATOR_PRIVATE_KEY=
FEDERATION_PORT=8000

# ─── Admin Service (Django) ──────────────────────────
DJANGO_SECRET_KEY=fedshield-dev-django-secret-change-in-prod
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3 # Uses SQLite locally for rapid setup
CELERY_BROKER_URL=redis://localhost:6379/1
ADMIN_PORT=8002

# ─── Web (Frontend / Vite) ──────────────────────────
VITE_API_URL=http://localhost:3000
VITE_ADMIN_URL=http://localhost:8002
VITE_WS_URL=ws://localhost:3000
```

### 8.2. Bootstrapping Infrastructure (Docker)
Start the foundational databases (PostgreSQL and Redis) using Docker. This avoids messy local installations.

```bash
docker run -d --name fedshield-pg -p 5432:5432 -e POSTGRES_USER=fedshield -e POSTGRES_PASSWORD=password -e POSTGRES_DB=fedshield postgres:15-alpine
docker run -d --name fedshield-redis -p 6379:6379 redis:7-alpine
```

### 8.3. Launching the Microservices
You will need **4 terminal windows**. Run these commands from the repository root.

**Terminal 1: Admin Service (Django API & Celery)**
```bash
cd apps/admin-service
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

**Terminal 2: Federation Server (FastAPI FL Engine)**
```bash
cd apps/federation-server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3: API Gateway (Node.js/Fastify Engine)**
```bash
cd apps/api-gateway
npm install
npm run dev
```

**Terminal 4: Web Dashboard (React/Vite)**
```bash
npm install
npm run dev --workspace apps/web
```

*Access the 3D dashboard at `http://localhost:5173`.*

---

## 9. API Documentation Reference

### 9.1. Register a Bank (Admin Service)
**POST** `http://localhost:8002/api/banks/`
Requires `Authorization: Token <YOUR_ADMIN_TOKEN>`

**Request:**
```json
{
  "name": "Global Standard Bank",
  "country_code": "US",
  "tier": "tier1",
  "privacy_epsilon": 1.0,
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkq... (RSA PEM)",
  "regulator_id": "REG-8472"
}
```

### 9.2. Submit a Gradient (Federation Server)
**POST** `http://localhost:8000/rounds/{round_id}/submit`
Requires `Authorization: Bearer dev-federation-key`

**Request:**
```json
{
  "bank_id": "uuid-of-bank",
  "weight_delta_cid": "QmYwAPJzv5CZsnA625s3Xf2Smuxa...",
  "weight_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "signature": "base64-rsa-signature-string",
  "dp_epsilon_used": 1.0,
  "local_samples_used": 15000,
  "local_auc": 0.942
}
```

### 9.3. Score a Transaction (API Gateway)
**POST** `http://localhost:3000/v1/score/transaction`
Requires `Authorization: Bearer <BANK_JWT_TOKEN>`

**Request:**
```json
{
  "transaction_id": "tx-99281",
  "amount": 450.00,
  "mcc": 5912,
  "is_new_device": true,
  "geo_distance_km": 150.5
}
```

**Response:**
```json
{
  "fraud_probability": 0.87,
  "risk_tier": "critical",
  "decision": "block",
  "latency_ms": 4.2
}
```

---

## 10. Simulation & Testing

To prove the mathematical validity of the FLTrust algorithm and the Anomaly Detector, FedShield includes a real-time attack simulator.

Run the simulation:
```bash
cd simulation
python -m venv venv
source venv/bin/activate
pip install numpy lightgbm scikit-learn
python bank_simulator.py
```

**What it does:**
The simulator spawns 10 banks. 7 are honest, 3 are malicious. The malicious banks automatically execute complex attacks:
1. **Gradient Scaling Attack:** Multiplying their weights by 50x to hijack the global model.
2. **Sign Flip Attack:** Reversing their gradient to destroy model convergence.
3. **Sybil Attack:** Submitting multiple coordinated micro-attacks.

**Expected Output:**
You will see the 3-Layer detector and FLTrust algorithm actively intercept the malicious payloads, assigning them a trust score of `0.0` (zeroing out their impact), while successfully aggregating the 7 honest banks.

---
*FedShield: Built with precision for zero-trust financial environments. For enterprise licensing and support, contact the architecture team.*
