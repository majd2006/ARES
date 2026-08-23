# ARES — AI-Powered Adaptive Emergency Response System

**MENA Ignite Open Gateway Hackathon 2026**
**Team:** Junior Engineers
**Members:** Majd Kassem · Zein El Abidine El Assaad

ARES is a network-aware, AI-assisted emergency-response orchestration platform designed to help emergency organizations make faster and more informed operational decisions during large-scale incidents.

The system combines incident information, responder resources, hospital capacity, geographic data, and telecommunications network intelligence to generate and dynamically update an actionable emergency-response plan.

> **ARES turns fragmented emergency information into faster, network-aware operational decisions when every minute matters.**

---

## Problem

During disasters such as explosions, earthquakes, major fires, infrastructure failures, and mass-casualty incidents, emergency commanders must make high-impact decisions within minutes.

However, the required information is often fragmented across different systems:

* responder teams;
* hospitals;
* relief centers;
* geographic information;
* emergency incident data;
* telecommunications systems.

A responder may exist in an operational database while being unreachable on the network.

Similarly, the closest team is not necessarily the most suitable team if its specialization, availability, or connectivity does not match the incident.

ARES addresses this operational gap by combining emergency-resource information with real-time network-aware signals before recommending deployment.

---

## Core Concept

ARES operates as an AI-assisted coordination layer between emergency information sources and human decision-makers.

The orchestration workflow is:

```text
Incident
   ↓
Disaster Assessment
   ↓
Network Intelligence
   ↓
Responder Evaluation
   ↓
Responder Ranking
   ↓
Resource Optimization
   ↓
Response Planning
   ↓
Operational Strategy
   ↓
Dynamic Replanning
```

ARES remains **human-in-the-loop by design**.

The system recommends operational actions, while emergency commanders retain final authority.

---

## Key Capabilities

### Disaster Assessment

ARES evaluates incident information to determine factors such as:

* incident severity;
* affected geographic area;
* estimated exposed population;
* estimated casualties;
* estimated critical casualties.

### Network-Aware Responder Evaluation

Responder availability is evaluated using both operational information and telecom-network intelligence.

Factors include:

* responder specialization;
* distance from the incident;
* deployment eligibility;
* device reachability;
* network-supported location information.

An unreachable responder can be removed from immediate deployment consideration.

### Responder Ranking

Eligible responder teams are prioritized according to operational suitability, including:

* proximity;
* specialization;
* network reachability;
* current operational constraints.

### Resource Optimization

ARES estimates and allocates resources such as:

* medical teams;
* rescue teams;
* ambulances;
* volunteers;
* hospital capacity.

### Hospital Allocation

Critical casualties can be distributed across available hospitals according to their remaining capacity rather than sending all casualties to a single facility.

### Regional Reinforcement

If local resources are insufficient, ARES can calculate additional reinforcement requirements from nearby resources.

### Dynamic Replanning

ARES is designed to recalculate its operational strategy when conditions change.

Examples include:

* incident escalation;
* loss of network connectivity;
* responder unavailability;
* resource shortages;
* changing hospital capacity.

---

# Nokia Network as Code Integration

Telecommunications information is part of the ARES decision loop rather than being used only as a communication channel.

The current prototype demonstrates two main Nokia Network as Code capabilities.

## Device Reachability

ARES can query whether a responder device is reachable through the telecom network.

The result can directly affect deployment eligibility.

```text
Responder available in database
            ↓
Nokia Device Reachability
            ↓
Reachable?
       ↙          ↘
     Yes           No
      ↓             ↓
Evaluate       Exclude from
for dispatch   immediate deployment
```

## Location Retrieval

Network-supported location information can be used for:

* responder proximity assessment;
* distance calculations;
* responder ranking;
* deployment prioritization.

## Geofencing

The repository also contains an experimental Nokia Network as Code geofencing integration that supports subscription-based location events.

The primary demonstrated hackathon workflow focuses on **Device Reachability** and **Location Retrieval**.

---

# AI / Decision Modules

ARES uses a modular architecture so that individual stages can be tested and extended independently.

```text
app/agents/
├── disaster_assessment_agent.py
├── incident_ingestion_agent.py
├── incident_reassessment_agent.py
├── network_agent.py
├── operational_strategy_agent.py
├── regional_reinforcement_agent.py
├── resource_escalation_agent.py
├── responder_evaluator.py
└── response_planning_agent.py
```

### Disaster Assessment Agent

Analyzes the incident and estimates severity and human impact.

### Incident Ingestion Agent

Transforms incoming incident information into structured operational data.

### Incident Reassessment Agent

Re-evaluates the incident when conditions change.

### Network Intelligence Agent

Connects telecom-network information with responder evaluation.

### Responder Evaluator

Determines whether responders are operationally eligible for deployment.

### Responder Ranker

Ranks eligible responders according to deployment priority.

### Response Planning Agent

Determines required resources and operational assignments.

### Resource Escalation Agent

Detects when current resources are insufficient.

### Regional Reinforcement Agent

Calculates reinforcement that can be obtained from surrounding resources.

### Operational Strategy Agent

Combines outputs from the other modules into a structured emergency-response strategy.

---

# Technical Architecture

```text
┌──────────────────────────────────────┐
│         DATA / FIELD LAYER           │
│                                      │
│ Incident Data                        │
│ Responder Teams                      │
│ Hospitals                            │
│ Relief Centers                       │
└─────────────────┬────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────┐
│        NETWORK API LAYER             │
│                                      │
│ Nokia Network as Code                │
│ • Device Reachability                │
│ • Location Retrieval                 │
│ • Geofencing integration             │
└─────────────────┬────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────┐
│       ARES INTELLIGENCE LAYER        │
│                                      │
│ Disaster Assessment                  │
│ Responder Evaluation                 │
│ Ranking                              │
│ Resource Optimization                │
│ Regional Reinforcement               │
│ Operational Strategy                 │
└─────────────────┬────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────┐
│      PRESENTATION / ACTION LAYER     │
│                                      │
│ Flask Backend                        │
│ REST Endpoints                       │
│ Interactive Dashboard               │
│ Leaflet + OpenStreetMap              │
│ Dynamic Replanning                   │
└──────────────────────────────────────┘
```

---

# Technology Stack

### Backend

* Python
* Flask

### Telecom Integration

* Nokia Network as Code
* Nokia Network as Code Python SDK
* REST API integration
* Device Reachability
* Location Retrieval

### Frontend

* HTML
* CSS
* JavaScript
* Leaflet
* OpenStreetMap

### Data / Intelligence

* modular Python decision agents;
* geographic distance calculations;
* responder-ranking logic;
* emergency-resource optimization;
* simulated operational datasets.

---

# Project Structure

```text
ARES/
│
├── app/
│   │
│   ├── agents/
│   │   ├── disaster_assessment_agent.py
│   │   ├── incident_ingestion_agent.py
│   │   ├── incident_reassessment_agent.py
│   │   ├── network_agent.py
│   │   ├── operational_strategy_agent.py
│   │   ├── regional_reinforcement_agent.py
│   │   ├── resource_escalation_agent.py
│   │   ├── responder_evaluator.py
│   │   └── response_planning_agent.py
│   │
│   ├── models/
│   │   └── resources.py
│   │
│   ├── network/
│   │   ├── nokia_client.py
│   │   └── nokia_geofencing.py
│   │
│   ├── optimization/
│   │   ├── resource_optimizer.py
│   │   └── responder_ranker.py
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   ├── templates/
│   │   └── dashboard.html
│   │
│   └── main.py
│
├── data/
│   └── demo_scenario.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd ARES
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The hackathon prototype uses:

```text
Flask==3.1.3
requests==2.34.2
python-dotenv==1.2.3
network_as_code==10.0.0
```

---

# Environment Configuration

Create a `.env` file in the project root.

```text
NOKIA_API_KEY=your_nokia_network_as_code_api_key
```

Never commit the real `.env` file or API key to GitHub.

An `.env.example` file is provided to document the required configuration safely.

---

# Running ARES

From the root of the repository:

```bash
python -m app.main
```

The Flask application starts on:

```text
http://127.0.0.1:5000
```

The server is configured to listen on port `5000`.

---

# API Endpoints

The current Flask backend exposes the following routes.

| Method | Endpoint                          | Purpose                                      |
| ------ | --------------------------------- | -------------------------------------------- |
| GET    | `/`                               | ARES operational dashboard                   |
| GET    | `/api/status`                     | Current system / dashboard state             |
| POST   | `/api/incidents`                  | Submit incident information                  |
| POST   | `/api/events/geofence`            | Handle geofencing-related events             |
| POST   | `/api/simulations/network-outage` | Simulate responder network loss              |
| POST   | `/api/simulations/reset`          | Reset simulation state                       |
| POST   | `/api/reassessment/reset`         | Reset incident reassessment state            |
| POST   | `/api/geofencing/reset`           | Reset geofencing state                       |
| POST   | `/api/demo/reset`                 | Reset the demonstration                      |
| POST   | `/api/demo/baseline`              | Load the baseline demonstration scenario     |
| POST   | `/api/demo/escalate`              | Escalate the incident and trigger replanning |

---

# Demonstration Workflow

The hackathon demonstration illustrates how the operational plan changes as the emergency evolves.

```text
1. Load baseline incident
        ↓
2. Assess disaster impact
        ↓
3. Evaluate and rank responders
        ↓
4. Generate resource plan
        ↓
5. Escalate incident
        ↓
6. Detect additional resource requirements
        ↓
7. Request regional reinforcement
        ↓
8. Simulate network loss
        ↓
9. Remove affected responder
        ↓
10. Recalculate operational strategy
```

This demonstrates that ARES is not simply a static emergency dashboard.

The system reacts to changing operational and telecommunications conditions.

---

# Demo Scenario

The baseline simulated scenario includes:

* an urban emergency zone;
* responder teams with different specializations;
* hospitals with limited available capacity;
* relief-center resources;
* Nokia network information.

ARES evaluates these inputs to produce:

* disaster assessment;
* responder eligibility;
* responder rankings;
* recommended emergency resources;
* responder assignments;
* hospital allocation;
* operational reserves;
* regional reinforcement recommendations.

During escalation or network loss, the response strategy is recalculated.

---

# Testing

The repository contains dedicated scripts for testing major ARES components.

Examples include:

```text
test_demo_scenario.py
test_disaster_assessment_agent.py
test_incident_ingestion_agent.py
test_incident_reassessment_agent.py
test_network_agent.py
test_network_location.py
test_nokia_reachability.py
test_operational_strategy_agent.py
test_regional_reinforcement_agent.py
test_resource_escalation_agent.py
test_resource_optimizer.py
test_responder_evaluator.py
test_responder_ranker.py
test_response_planning_agent.py
```

For example:

```bash
python -m tests.test_nokia_reachability
```

and:

```bash
python -m tests.test_response_planning_agent
```

Some Nokia Network as Code tests require a valid API key.

---

# Prototype Scope

ARES is currently a **hackathon software prototype**.

The disaster, responder, relief-center, and hospital datasets used in the demonstration are simulated to validate the end-to-end orchestration architecture.

The prototype demonstrates:

* multi-stage emergency decision logic;
* Nokia Network as Code integration;
* responder reachability evaluation;
* network-supported location use;
* resource optimization;
* hospital allocation;
* dynamic incident reassessment;
* regional reinforcement;
* network-loss replanning;
* interactive operational visualization.

ARES is not currently deployed as a production emergency-management system.

Production use would require:

* validated emergency datasets;
* cybersecurity controls;
* resilient infrastructure;
* regulatory and safety review;
* integration with official emergency-management systems;
* production telecom and public-safety agreements.

---

# Future Development

Potential extensions include:

* real-time hospital capacity feeds;
* ambulance and responder telemetry;
* live road and traffic information;
* additional Open Gateway network intelligence;
* Quality on Demand;
* expanded geofencing;
* satellite-based incident assessment;
* drone-based damage mapping;
* ML-assisted damage estimation;
* multi-incident coordination;
* multi-agency regional resource optimization.

---

# Business Potential

ARES is designed as a potential **B2G / B2B2G emergency-response platform** for:

* governments;
* municipalities;
* civil defense organizations;
* emergency medical services;
* relief organizations;
* smart-city operators;
* telecommunications partners.

Potential commercialization models include:

1. annual agency or city platform licensing;
2. deployment and systems-integration services;
3. telecom/API partnerships;
4. regional multi-agency emergency-management deployments.

The central value proposition is to coordinate existing emergency assets more intelligently without requiring every organization to replace its existing operational systems.

---

# Team

## Junior Engineers

### Majd Kassem

Third-year engineering student
Co-Developer

### Zein El Abidine El Assaad

Third-year engineering student
Co-Developer

Shared responsibilities included:

* system architecture;
* backend implementation;
* AI / decision orchestration;
* Nokia Network as Code integration;
* testing;
* dashboard development;
* hackathon demonstration preparation.

---

# Hackathon

**MENA Ignite Open Gateway Hackathon 2026**

**Theme:**
Smart Cities, Urban Safety & Mega-Project Infrastructure

**Project:**
ARES — AI-Powered Adaptive Emergency Response System

---

## Disclaimer

ARES is an experimental decision-support prototype developed for the MENA Ignite Open Gateway Hackathon 2026.

It is not intended to autonomously replace emergency commanders, medical personnel, or official public-safety decision-making systems.
