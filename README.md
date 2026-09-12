# ARES — AI-Powered Adaptive Emergency Response System

**MENA Ignite Open Gateway Hackathon 2026**  
**Team:** Junior Engineers  
**Members:** Majd Kassem · Zein El Abidine El Assaad

ARES is a network-aware, AI-assisted emergency-response orchestration platform designed to help emergency organizations make faster and more informed operational decisions during large-scale incidents.

The system combines incident intelligence, responder resources, hospital capacity, geographic information, operational constraints, and telecommunications network intelligence to generate and dynamically update an actionable emergency-response strategy.

> **ARES turns fragmented emergency information into faster, network-aware operational decisions when every minute matters.**

---

## Problem

During disasters such as explosions, earthquakes, major fires, infrastructure failures, and mass-casualty incidents, emergency commanders must make high-impact decisions within minutes.

However, critical information is often fragmented across different systems:

- responder teams;
- hospitals;
- relief centers;
- geographic and road information;
- emergency incident data;
- telecommunications systems.

A responder may exist in an operational database while being unreachable through the network.

Similarly, the geographically closest team is not necessarily the best team to deploy if its specialization, availability, connectivity, or route accessibility does not match current operational conditions.

Emergency plans can also become obsolete within minutes when:

- communications fail;
- roads become obstructed;
- casualty estimates increase;
- hospital capacity changes;
- local resources become insufficient;
- responder availability changes.

ARES addresses this operational gap by combining emergency-resource information with network and operational intelligence before recommending deployment — and recalculating the strategy when conditions change.

---

# Final Prototype Capabilities

The current ARES prototype demonstrates:

- Disaster assessment and casualty estimation
- Network-aware responder evaluation
- Responder ranking and deployment prioritization
- Nokia Network as Code / CAMARA integration
- Device reachability intelligence
- Network-supported location intelligence
- Agentic multi-API orchestration
- Resource optimization
- Hospital allocation
- Regional reinforcement
- Dynamic operational replanning
- Network-outage response
- Road-obstruction-aware planning
- Resource-pressure detection and escalation
- Field medical post recommendation
- Safe staging-site selection
- CAMARA observability
- Degraded-mode network resilience
- Human-in-the-loop command governance
- Commander approve/reject workflow
- Interactive Beirut operational dashboard
- Scenario reset and live demonstration controls

ARES is not a static emergency dashboard.

It is designed as an **adaptive operational decision-support system** whose recommendations can change as the incident, network, resource, and accessibility state changes.

---

# Core Concept

ARES operates as an intelligent coordination layer between emergency information sources, telecom-network intelligence, operational resources, and human commanders.

```text
Incident / Operational Data
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
Operational Planning
          ↓
ARES Orchestrator
          ↓
Operational Strategy
          ↓
Dynamic Replanning
          ↓
Human Command Decision
          ↓
Approve / Reject
```

ARES remains **human-in-the-loop by design**.

The system generates and updates recommendations, while emergency commanders retain final operational authority.

> **AI recommends. Network intelligence validates. Humans decide.**

---

# System Architecture

ARES uses a modular architecture in which specialized decision agents contribute to a unified orchestration layer.

```text
┌───────────────────────────────────────────┐
│             DATA / FIELD LAYER            │
│                                           │
│ Incident Data                             │
│ Responder Teams                           │
│ Hospitals                                 │
│ Relief Centers                            │
│ Road Network                              │
│ Candidate Staging Sites                   │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│        TELECOM / NETWORK API LAYER        │
│                                           │
│ Nokia Network as Code / CAMARA            │
│ • Device Reachability                     │
│ • Location Retrieval                      │
│ • Geofencing Integration                  │
│ • Network Observability                   │
│ • Degraded-Mode Handling                  │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│          ARES INTELLIGENCE LAYER          │
│                                           │
│ Disaster Assessment                       │
│ Incident Reassessment                     │
│ Responder Evaluation                      │
│ Responder Ranking                         │
│ Resource Optimization                     │
│ Regional Reinforcement                    │
│ Route Accessibility                       │
│ Field Medical Post Selection              │
│ Safe Staging Site Selection               │
│ Operational Strategy                      │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│          ORCHESTRATION LAYER              │
│                                           │
│ ARES Orchestrator                         │
│ Decision Replanner                        │
│ Command Approval / Governance             │
│ Runtime State Coordination                │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│       PRESENTATION / COMMAND LAYER        │
│                                           │
│ Flask Backend                             │
│ REST API                                  │
│ Interactive Dashboard                     │
│ Leaflet + OpenStreetMap                   │
│ Operational Strategy                      │
│ Dynamic Replanning                        │
│ Commander Approve / Reject                │
└───────────────────────────────────────────┘
```

---

# AI / Decision Agents

ARES separates operational responsibilities into specialized modules so that each stage can be independently developed, tested, and extended.

## Disaster Assessment Agent

Analyzes incident information and estimates:

- incident severity;
- affected geographic area;
- exposed population;
- estimated casualties;
- estimated critical casualties.

## Incident Ingestion Agent

Transforms incoming incident information into structured operational data that can be consumed by the rest of the ARES pipeline.

## Incident Reassessment Agent

Re-evaluates the incident when operational conditions or incident characteristics change.

## Network Intelligence Agent

Connects telecommunications information with responder evaluation and orchestration.

It enables network state to influence operational decisions instead of treating connectivity as a passive status indicator.

## Responder Evaluator

Determines whether responder teams are operationally eligible for deployment.

Factors can include:

- specialization;
- location;
- distance;
- availability;
- device reachability;
- current operational constraints.

## Responder Ranker

Prioritizes eligible responders according to operational suitability.

## Response Planning Agent

Calculates required emergency resources and produces responder assignments and hospital allocations.

## Resource Escalation Agent

Detects situations where available local resources are insufficient for the estimated emergency requirements.

## Regional Reinforcement Agent

Calculates additional resources that can be requested from surrounding response capacity when local resources are insufficient.

## Operational Strategy Agent

Combines operational outputs into a prioritized emergency-response strategy.

The final prototype also accounts for runtime resource pressure and changing operational conditions.

## Field Medical Post Agent

Evaluates the operational need and potential placement of a temporary field medical post during high-casualty scenarios.

## Staging Site Agent

Evaluates candidate locations for safe operational staging based on incident and resource context.

## Route Access Agent

Introduces road-accessibility constraints into deployment planning.

This allows ARES to demonstrate that a responder can be:

- available;
- reachable;
- geographically close;

while still being operationally unsuitable if its route becomes obstructed.

---

# ARES Orchestration Layer

The final prototype introduces a dedicated orchestration layer:

```text
app/orchestration/
├── __init__.py
├── ares_orchestrator.py
├── command_approval.py
└── decision_replanner.py
```

## ARES Orchestrator

The orchestrator coordinates the specialized ARES agents and combines their outputs into a unified operational state.

Instead of requiring the dashboard or API layer to independently execute every decision module, the orchestrator provides a structured workflow for processing incident, responder, network, resource, and planning information.

## Decision Replanner

The decision replanner compares the current operational state with changing conditions.

When a material change occurs, ARES can produce a revised plan.

Examples include:

- responder network loss;
- road obstruction;
- resource pressure;
- incident escalation;
- changes in responder eligibility.

## Command Approval

ARES includes a human-in-the-loop command-governance layer.

Operational recommendations can be:

- reviewed;
- approved;
- rejected;
- associated with commander information and notes.

This prevents the prototype from treating AI-generated recommendations as autonomous real-world emergency commands.

---

# Nokia Network as Code / CAMARA Integration

Telecommunications intelligence is integrated into the ARES decision loop rather than being used only as a communication channel.

The prototype primarily demonstrates:

- **Device Reachability**
- **Location Retrieval**

The repository also contains experimental geofencing functionality and resilience logic around network/API availability.

---

## Device Reachability

ARES can evaluate whether a responder device is reachable through the telecommunications network.

```text
Responder Available
        ↓
Device Reachability
        ↓
    Reachable?
      /    \
    Yes     No
     ↓       ↓
Evaluate   Exclude / Replan
```

This allows telecom-network state to directly affect operational deployment recommendations.

A nearby responder is not automatically considered deployable if the system determines that communications cannot reliably reach that responder.

---

## Location Retrieval

Network-supported location information can contribute to:

- responder proximity assessment;
- distance calculations;
- responder ranking;
- deployment prioritization;
- operational awareness.

Location uncertainty can also be represented as part of the network-derived information.

---

## Geofencing

The repository contains Nokia Network as Code geofencing functionality for subscription-based location events.

The primary demonstrated hackathon workflow focuses on **Device Reachability** and **Location Retrieval**.

---

# CAMARA Resilience and Observability

The final prototype includes additional handling for telecommunications API behavior.

ARES exposes network/CAMARA state to the operational workflow so that the system can distinguish between available network intelligence and degraded conditions.

The architecture is designed so that a temporary API or network limitation does not automatically collapse the entire emergency-response workflow.

Instead, the system can expose degraded network intelligence and preserve the distinction between:

- confirmed network information;
- simulated/demo information;
- degraded or unavailable network information.

This improves operational transparency and prevents network uncertainty from being silently treated as verified data.

---

# Dynamic Operational Replanning

Dynamic replanning is one of the central capabilities of the final ARES prototype.

A baseline operational plan can be generated using the current:

- incident assessment;
- responder state;
- network state;
- hospital capacity;
- available resources;
- geographic constraints.

ARES then evaluates whether subsequent changes materially affect the existing plan.

```text
Baseline Operational Plan
          ↓
Operational Change
          ↓
Material Impact?
       /       \
     No         Yes
     ↓           ↓
Maintain      Re-evaluate
Plan          Responders
                 ↓
             Recalculate
                 ↓
             Revised Plan
```

Examples of replanning triggers include:

- responder network outage;
- road obstruction;
- responder unavailability;
- resource pressure;
- incident escalation;
- changing operational constraints.

---

# Network-Outage Replanning

A key demonstration scenario simulates the loss of connectivity to a responder included in the baseline plan.

Example:

```text
BASELINE

R01 + R02 + R03
      ↓
Network outage affects R01
      ↓
R01 becomes operationally unsuitable
      ↓
ARES detects material change
      ↓
Replanning
      ↓
R02 + R03 / revised resource strategy
```

This demonstrates why network intelligence can become an operational input rather than simply a communications feature.

---

# Road-Obstruction Replanning

The final prototype also introduces road-access constraints.

During the live demo, a road obstruction can change the accessibility of responder resources.

ARES can then reassess the operational strategy based on the updated route state.

This demonstrates an important distinction:

> **The closest responder is not necessarily the fastest deployable responder.**

A team can be physically close to the incident but operationally disadvantaged by route obstruction.

---

# Resource Pressure and Reinforcement

ARES compares estimated incident requirements with available response resources.

When the system detects insufficient local capacity, it can:

1. identify the resource deficit;
2. escalate the requirement;
3. calculate regional reinforcement;
4. update the operational strategy.

This can include requirements involving:

- medical teams;
- rescue teams;
- ambulances;
- volunteers;
- hospital capacity.

---

# Hospital Allocation

ARES can distribute estimated critical casualties across available hospitals according to remaining capacity.

This avoids a simplistic strategy where all casualties are routed to the nearest hospital regardless of available capacity.

The allocation logic supports a more balanced operational response.

---

# Field Medical Post Recommendation

When casualty pressure and transport requirements justify additional medical capacity, ARES can evaluate a field medical post as part of the response strategy.

The field medical post module demonstrates how future versions of ARES could support temporary medical infrastructure planning during mass-casualty incidents.

---

# Safe Staging Site Selection

ARES includes a staging-site decision module for evaluating candidate operational locations.

Staging areas can support:

- responder coordination;
- equipment organization;
- ambulance operations;
- reinforcement arrival;
- temporary command activities.

This adds geographic operational planning beyond simple responder-to-incident routing.

---

# Beirut Demonstration Scenario

The final prototype includes a Beirut-focused demonstration scenario.

Scenario-specific data is located under:

```text
data/
├── beirut_demo_scenario.py
├── beirut_road_network.py
├── beirut_staging_sites.py
└── demo_scenario.py
```

The scenario is designed to demonstrate the complete ARES workflow under a severe urban emergency.

ARES evaluates:

- disaster severity;
- estimated exposed population;
- estimated casualties;
- critical casualties;
- responder availability;
- responder specialization;
- network reachability;
- responder location;
- hospital capacity;
- regional reinforcement;
- road accessibility;
- staging-site options;
- field medical requirements.

The scenario can then be modified during runtime to demonstrate adaptive replanning.

---

# Human-in-the-Loop Command Governance

ARES is a **decision-support system**, not an autonomous emergency commander.

The final prototype therefore includes explicit command governance.

The dashboard allows recommendations to be reviewed and supports command decisions such as:

```text
ARES Recommendation
        ↓
Commander Review
      /       \
  APPROVE    REJECT
      ↓         ↓
Decision state recorded
```

Commander information and notes can be associated with the decision workflow.

This architecture preserves human authority over high-impact emergency decisions.

---

# Interactive Operational Dashboard

ARES includes a web-based command dashboard built using:

- Flask;
- HTML;
- CSS;
- JavaScript;
- Leaflet;
- OpenStreetMap.

The dashboard visualizes operational information including the active incident and relevant response resources.

It also exposes the system's operational strategy, network intelligence, replanning behavior, and command controls.

The final dashboard is designed for demonstration of the complete ARES decision loop rather than simply displaying static emergency data.

---

# Technology Stack

## Backend

- Python
- Flask
- REST API architecture

## Telecom Integration

- Nokia Network as Code
- Nokia Network as Code Python SDK
- CAMARA / Open Gateway APIs
- Device Reachability
- Location Retrieval
- Geofencing integration

## Frontend

- HTML
- CSS
- JavaScript
- Leaflet
- OpenStreetMap

## Intelligence / Decision Layer

- modular Python decision agents;
- agent orchestration;
- dynamic decision replanning;
- geographic distance calculations;
- responder-ranking logic;
- resource optimization;
- hospital-capacity allocation;
- route-access evaluation;
- staging-site evaluation;
- command governance.

---

# Project Structure

```text
ARES/
│
├── app/
│   │
│   ├── agents/
│   │   ├── disaster_assessment_agent.py
│   │   ├── field_medical_post_agent.py
│   │   ├── incident_ingestion_agent.py
│   │   ├── incident_reassessment_agent.py
│   │   ├── network_agent.py
│   │   ├── operational_strategy_agent.py
│   │   ├── regional_reinforcement_agent.py
│   │   ├── resource_escalation_agent.py
│   │   ├── responder_evaluator.py
│   │   ├── response_planning_agent.py
│   │   ├── route_access_agent.py
│   │   └── staging_site_agent.py
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
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── ares_orchestrator.py
│   │   ├── command_approval.py
│   │   └── decision_replanner.py
│   │
│   ├── simulation/
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── dashboard.css
│   │   └── js/
│   │       └── dashboard.js
│   │
│   ├── templates/
│   │   └── dashboard.html
│   │
│   └── main.py
│
├── data/
│   ├── beirut_demo_scenario.py
│   ├── beirut_road_network.py
│   ├── beirut_staging_sites.py
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

## 1. Clone the Repository

```bash
git clone https://github.com/majd2006/ARES.git
cd ARES
```

## 2. Create a Virtual Environment

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

## 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

The prototype currently uses:

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

Never commit a real `.env` file or API key to the repository.

An `.env.example` file is provided to document the required configuration safely.

---

# Running ARES

From the repository root:

```bash
python -m app.main
```

The Flask application starts on:

```text
http://127.0.0.1:5000
```

Open this address in a browser to access the ARES operational dashboard.

---

# REST API and Demo Controls

The Flask backend exposes REST endpoints supporting:

- dashboard state retrieval;
- incident submission;
- simulation control;
- network-outage simulation;
- incident reassessment;
- geofencing events;
- demo reset;
- baseline scenario loading;
- incident escalation;
- command approval;
- command rejection;
- runtime operational replanning.

Key final-prototype controls include:

```text
POST /api/demo/reset
POST /api/simulations/network-outage
POST /api/command/approve
POST /api/command/reject
```

Additional routes are implemented in `app/main.py` for the complete dashboard and demonstration workflow.

---

# Demonstration Workflow

A typical final ARES demonstration follows this operational sequence:

```text
1. Load Beirut baseline scenario
        ↓
2. Assess disaster impact
        ↓
3. Evaluate telecom/network state
        ↓
4. Evaluate and rank responders
        ↓
5. Calculate resource requirements
        ↓
6. Allocate hospital capacity
        ↓
7. Evaluate staging / field medical needs
        ↓
8. Generate operational strategy
        ↓
9. Present recommendation to commander
        ↓
10. Introduce operational disruption
        ↓
11. Detect material change
        ↓
12. Dynamically replan
        ↓
13. Present revised operational strategy
        ↓
14. Commander approves or rejects
```

Operational disruptions can include scenarios such as:

- network outage;
- road obstruction;
- incident escalation;
- resource pressure.

This demonstrates that ARES continuously reasons over changing operational conditions rather than displaying a fixed emergency plan.

---

# Testing

ARES contains dedicated tests for individual agents as well as higher-level orchestration, resilience, and replanning behavior.

Important final-prototype tests include:

```text
test_ares_orchestrator.py
test_beirut_regional_reinforcement.py
test_beirut_scenario.py
test_demo_scenario.py
test_disaster_assessment_agent.py
test_dynamic_replanning.py
test_incident_ingestion_agent.py
test_incident_reassessment_agent.py
test_network_agent.py
test_network_location.py
test_network_resilience.py
test_nokia_geofencing.py
test_nokia_reachability.py
test_operational_strategy_agent.py
test_orchestrator_resilience.py
test_regional_reinforcement_agent.py
test_resource_escalation_agent.py
test_resource_optimizer.py
test_responder_evaluator.py
test_responder_ranker.py
test_response_planning_agent.py
test_runtime_resource_pressure.py
```

The full test suite can be executed with:

```bash
python -m pytest -q
```

Some Nokia Network as Code integration tests may require valid API credentials.

---

# Prototype Scope

ARES is currently a **hackathon software prototype**.

The disaster, responder, hospital, road, staging-site, and relief-resource datasets used by the demonstration are designed to validate the end-to-end orchestration architecture.

The prototype demonstrates the technical feasibility of combining:

- emergency incident assessment;
- responder intelligence;
- telecom-network intelligence;
- resource optimization;
- operational planning;
- geographic constraints;
- dynamic replanning;
- command governance.

ARES is **not currently deployed as a production emergency-management system**.

Production deployment would require:

- validated real-world emergency datasets;
- official responder and hospital integrations;
- production-grade cybersecurity;
- authentication and authorization infrastructure;
- high-availability deployment;
- resilient telecommunications integration;
- regulatory and safety review;
- integration with official emergency-management systems;
- operational validation with emergency professionals.

---

# Design Philosophy

ARES follows three important principles.

### 1. Network intelligence should influence operational decisions

A responder that cannot reliably be reached should not be treated identically to a responder with confirmed communications.

### 2. Emergency plans must be adaptive

A valid plan at one moment may become invalid after a network outage, road obstruction, resource shortage, or incident escalation.

### 3. Humans retain authority

ARES supports emergency commanders.

It does not replace them.

---

# Future Development

Potential extensions include:

- real-time hospital capacity feeds;
- ambulance and responder telemetry;
- live road and traffic APIs;
- additional CAMARA / Open Gateway capabilities;
- Quality on Demand;
- expanded geofencing;
- programmable connectivity;
- satellite-based incident assessment;
- drone-based damage mapping;
- ML-assisted damage estimation;
- multi-incident coordination;
- multi-agency resource optimization;
- resilient cloud/edge deployment;
- integration with official emergency-dispatch systems.

---

# Business Potential

ARES is designed as a potential **B2G / B2B2G emergency-response platform** for:

- governments;
- municipalities;
- civil defense organizations;
- emergency medical services;
- humanitarian and relief organizations;
- smart-city operators;
- telecommunications partners.

Potential commercialization models include:

1. annual agency or city platform licensing;
2. deployment and systems-integration services;
3. telecom/API partnerships;
4. regional multi-agency emergency-management deployments.

The central value proposition is to coordinate existing emergency assets more intelligently without requiring every organization to replace its existing operational systems.

---

# Repository

Source code:

**https://github.com/majd2006/ARES**

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

- system architecture;
- backend implementation;
- AI / decision orchestration;
- Nokia Network as Code integration;
- dynamic replanning;
- testing;
- dashboard development;
- hackathon demonstration preparation.

---

# Hackathon

**MENA Ignite Open Gateway Hackathon 2026**

**Theme:**  
Smart Cities, Urban Safety & Mega-Project Infrastructure

**Project:**  
ARES — AI-Powered Adaptive Emergency Response System

---

# Disclaimer

ARES is an experimental decision-support prototype developed for the MENA Ignite Open Gateway Hackathon 2026.

It is not intended to autonomously replace emergency commanders, medical personnel, or official public-safety decision-making systems.

All operational scenarios and recommendations demonstrated by the prototype should be interpreted within the context of research, experimentation, and hackathon evaluation.