# System Engineering Perspective: Content Streamer Architecture

Let me break this down into a proper layered architecture with critical design decisions at each level.

## Top-Level System Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  (Web App, Mobile, Obsidian Plugin, API Gateway)            │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  (Business Logic, Workflow Orchestration, User Preferences) │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  INTELLIGENCE LAYER                          │
│  (ML Models, Recommendation Engine, Connection Discovery)   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  (Storage, Indexing, Vector DB, Cache)                      │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  INGESTION LAYER                             │
│  (Source Connectors, Parsers, Normalization)                │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                           │
│  (Message Queue, Scheduler, Monitoring, Auth)               │
└─────────────────────────────────────────────────────────────┘
```

## Layer-by-Layer Design Decisions

### **Layer 1: Infrastructure Layer (Foundation)**

**Purpose:** Cross-cutting concerns that support all other layers

**Components:**
- Message Queue/Event Bus
- Task Scheduler
- Authentication & Authorization
- Logging & Monitoring
- Configuration Management
- Secrets Management

**Critical Decisions:**

**D1.1: Deployment Model**
- **Option A:** Monolithic (single deployment unit)
  - *Pros:* Simpler initially, easier debugging, no network overhead
  - *Cons:* Harder to scale individual components, coupling increases over time
- **Option B:** Microservices (separate services per layer/domain)
  - *Pros:* Independent scaling, technology flexibility, fault isolation
  - *Cons:* Network complexity, distributed debugging, operational overhead
- **Option C:** Modular Monolith (single deployment, clear module boundaries)
  - *Pros:* Best of both worlds initially, can extract services later
  - *Cons:* Requires discipline to maintain boundaries
- **Recommendation:** Start with **Modular Monolith**, extract to services only when specific scaling needs arise

**D1.2: Message Queue Technology**
- **Option A:** Redis Streams (lightweight, you likely already have Redis)
- **Option B:** RabbitMQ (robust, great for work queues)
- **Option C:** Kafka (overkill unless you need event sourcing)
- **Recommendation:** **Redis Streams** for simplicity

**D1.3: Scheduler**
- **Option A:** Cron + database locking
- **Option B:** Celery Beat
- **Option C:** Temporal/Airflow (workflow engines)
- **Recommendation:** **Celery Beat** - mature, Python-native

**D1.4: Authentication Strategy**
- Single user (you) vs multi-tenant from day one?
- **If single user:** Simple token-based auth
- **If multi-tenant:** OAuth2 + JWT, plan for data isolation early

---

### **Layer 2: Ingestion Layer**

**Purpose:** Fetch, parse, and normalize content from diverse sources

**Components:**
- Source Connectors (RSS, YouTube, arXiv, Podcasts, etc.)
- Content Parsers (HTML → clean text, PDF extraction)
- Rate Limiters
- Deduplication Service
- Normalization Pipeline

**Critical Decisions:**

**D2.1: Connector Architecture**
- **Option A:** Hardcoded connectors per source type
  - *Pros:* Full control, optimized per source
  - *Cons:* Adding new sources requires code changes
- **Option B:** Plugin system with adapter interface
  - *Pros:* Extensible, community contributions possible
  - *Cons:* More complex initially
- **Recommendation:** **Hardcoded initially**, refactor to plugin system after 5-6 connector types

**D2.2: Content Processing Pipeline**
```
Raw Fetch → Parse → Extract Metadata → Deduplicate → Normalize → Enrich → Store
```
- Should this be synchronous or asynchronous?
- **Recommendation:** **Asynchronous** - fetch triggers message, workers process

**D2.3: Deduplication Strategy**
- Content hashing (exact duplicates)
- Fuzzy matching (near-duplicates)
- URL normalization
- **Decision:** How aggressive? Same article on multiple sites = 1 entry or multiple?

**D2.4: Error Handling**
- Dead sources (404s, feed discontinued)
- Rate limiting from providers
- Malformed content
- **Decision:** Retry policy (exponential backoff?), alerting thresholds

**D2.5: Metadata Schema**
- Core fields: title, author, date, source, URL, content_type
- Source-specific fields: keep in JSON blob or normalize?
- **Recommendation:** Core fields normalized, source-specific in JSONB column

---

### **Layer 3: Data Layer**

**Purpose:** Persist and retrieve content efficiently

**Components:**
- Primary Database (structured data)
- Vector Database (embeddings for semantic search)
- Cache Layer
- Search Index
- Object Storage (full-text content, PDFs, images)

**Critical Decisions:**

**D3.1: Primary Database**
- **Option A:** PostgreSQL (relational, JSONB support, mature)
- **Option B:** MongoDB (document-oriented, flexible schema)
- **Recommendation:** **PostgreSQL** - handles both structured + semi-structured well

**D3.2: Database Schema Design**

**Normalization level:**
```sql
-- Core entities
users (id, email, created_at, preferences_json)
sources (id, user_id, type, url, config_json, last_fetched_at, enabled)
items (id, source_id, external_id, title, author, published_at, url, content_hash)
item_content (item_id, raw_content, parsed_content, metadata_json)
```

**Decision points:**
- Store full content in DB or object storage (S3/MinIO)?
  - **< 1MB:** In database (faster queries)
  - **> 1MB:** Object storage (cost, scalability)

**D3.3: Vector Database Choice**
- **Option A:** pgvector (PostgreSQL extension)
  - *Pros:* Single database, simpler ops, ACID guarantees
  - *Cons:* Not optimized for billion-scale vectors
- **Option B:** Dedicated (Pinecone, Weaviate, Qdrant)
  - *Pros:* Better performance, specialized features
  - *Cons:* Another system to manage
- **Recommendation:** **pgvector** initially, migrate if you hit 100K+ items

**D3.4: Feedback Data Model**
```sql
-- Implicit feedback
interactions (id, user_id, item_id, type, timestamp, metadata_json)
  -- types: viewed, clicked, time_spent, saved, shared, dismissed

-- Explicit feedback (for RLHF)
feedback (id, user_id, item_id, rating, category, emotion, reasoning_text, timestamp)

-- Highlights
highlights (id, user_id, item_id, text_range, annotation, sentiment, created_at)
```

**D3.5: Time-Series Considerations**
- User engagement patterns over time
- Content freshness decay
- **Decision:** Use TimescaleDB extension for time-series queries?

---

### **Layer 4: Intelligence Layer**

**Purpose:** Learn preferences, recommend content, discover connections

**Components:**
- Feature Extraction Service
- Recommendation Engine
- Preference Learning Pipeline
- Connection Discovery Service
- Model Training Infrastructure

**Critical Decisions:**

**D4.1: ML Architecture Strategy**
- **Phase 1:** Rule-based + simple ML (0-3 months)
- **Phase 2:** Classical ML models (3-6 months)
- **Phase 3:** LLM-based with fine-tuning (6+ months)
- **Decision:** When to introduce each complexity level?

**D4.2: Feature Store**
- Do you need a dedicated feature store (Feast, Tecton)?
- **For your scale:** Probably not - materialized views in PostgreSQL sufficient
- **Recommendation:** Start with computed columns, views, migrate if latency becomes issue

**D4.3: Embedding Strategy**
- **Option A:** Pre-compute embeddings for all content at ingestion
  - *Pros:* Fast retrieval, consistent
  - *Cons:* Storage cost, reprocessing if model changes
- **Option B:** Compute on-demand
  - *Pros:* Flexible, no storage
  - *Cons:* Latency
- **Recommendation:** **Pre-compute** - embeddings are core to your system

**D4.4: Model Serving Architecture**
```
┌─────────────────────────────────────────┐
│         Model Registry                  │
│  (Versions, Metadata, A/B configs)     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Model Serving Layer                 │
│  (Inference API, Batch Scoring)        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Application Logic                   │
└─────────────────────────────────────────┘
```

**Decisions:**
- REST API vs gRPC for inference?
- Real-time inference vs batch scoring?
- **Recommendation:** Batch score daily for digest, real-time for interactive features

**D4.5: RLHF Pipeline Design**
```
User Feedback → Reward Modeling → Policy Training → Evaluation → Deployment
```

**Key decisions:**
- How often to retrain? (Weekly? Monthly? Continuous?)
- Minimum feedback data before RLHF kicks in?
- Fallback strategy when model fails?
- **Recommendation:** 
  - Retrain weekly initially, move to continuous once stable
  - Need 500+ quality feedback samples minimum
  - Always fall back to collaborative filtering baseline

**D4.6: Connection Discovery Algorithm**
- **Option A:** Periodic batch job (weekly)
  - Compute similarity matrix across recent items
  - Identify clusters, cross-domain links
- **Option B:** Incremental (each new item)
  - Check against existing corpus
  - More real-time but higher compute
- **Recommendation:** **Batch** - connections are insight, not time-critical

---

### **Layer 5: Application Layer**

**Purpose:** Business logic, orchestration, user-facing workflows

**Components:**
- Digest Compiler
- Category Management
- Reading Queue Manager
- Export Services (Obsidian, etc.)
- Notification Service
- Preference Management

**Critical Decisions:**

**D5.1: Digest Compilation Strategy**
```
Trigger (EOD/EOW) → Fetch new items → Score/Rank → Apply filters → 
Group by category → Generate digest → Deliver
```

**Decisions:**
- Push vs pull delivery?
  - **Push:** Email, notification
  - **Pull:** User opens app
- **Recommendation:** Both - notification that digest is ready, user pulls when ready

**D5.2: Category System Design**
- **Option A:** Fixed taxonomy (you define categories)
- **Option B:** Dynamic tags (organic growth)
- **Option C:** Hybrid (core categories + flexible tags)
- **Recommendation:** **Hybrid**

**Schema:**
```sql
categories (id, name, parent_id, is_system)  -- hierarchical
item_categories (item_id, category_id, confidence, source)  -- source: manual|predicted
tags (id, name)
item_tags (item_id, tag_id)
```

**D5.3: Reading Queue Management**
- Single queue vs multiple (Read Now, Read Later, Archive)?
- Scheduling: "Show me this on Saturday morning"
- **Decision:** State machine for item lifecycle

```
New → Recommended → Queued → Reading → Completed
                  ↘ Dismissed
                  ↘ Archived
```

**D5.4: Export Service Design**
- Real-time sync vs batch export?
- Obsidian-specific: Watch folder? Plugin? REST API?
- **Recommendation:** Batch export on demand + real-time for marked items

**Template decision:**
```markdown
---
title: {{title}}
author: {{author}}
source: {{source}}
date: {{published_date}}
categories: [{{categories}}]
rating: {{your_rating}}
---

{{content}}

## Your Notes
{{highlights}}

## AI Insights
{{connections}}
```

**D5.5: Preference Management**
- Explicit preferences (topic weights, source priorities)
- Implicit learning (the AI part)
- **Decision:** UI for explicit overrides? Or trust the model?
- **Recommendation:** Start with explicit controls, gradually reduce as model improves

---

### **Layer 6: Presentation Layer**

**Purpose:** User interfaces and external integrations

**Components:**
- Web Application
- API Gateway
- Obsidian Plugin
- (Future: Mobile app, browser extension)

**Critical Decisions:**

**D6.1: Frontend Architecture**
- **Option A:** Traditional server-rendered (Django templates, Flask + Jinja)
- **Option B:** SPA (React, Vue, Svelte)
- **Option C:** Hybrid (Next.js, SvelteKit)
- **Recommendation:** **SPA with React** - interactive features (drag-drop categories, real-time feedback) benefit from reactivity

**D6.2: API Design**
- RESTful vs GraphQL?
- **REST Pros:** Simpler, cacheable, widely understood
- **GraphQL Pros:** Flexible queries, single endpoint
- **Recommendation:** **REST** - your use cases are straightforward

**Key endpoints:**
```
GET  /api/digest/daily
GET  /api/digest/weekly
GET  /api/items?category=X&status=Y
POST /api/items/{id}/feedback
POST /api/items/{id}/categorize
GET  /api/connections
POST /api/export/obsidian
```

**D6.3: Real-time Updates**
- WebSockets for live updates?
- Server-Sent Events?
- Polling?
- **For your use case:** Polling is sufficient (digests aren't real-time)

**D6.4: Obsidian Integration Architecture**
- **Option A:** Direct file system access (if self-hosted)
- **Option B:** REST API → Obsidian plugin polls
- **Option C:** Obsidian plugin → your API
- **Recommendation:** **Option C** - cleaner separation, works for cloud-hosted Obsidian

---

## Cross-Cutting Decisions

### **CD1: Data Privacy & Security**
Since this handles your personal content consumption:
- **Decision:** Self-hosted vs cloud?
  - Self-hosted: Full control, privacy, but ops burden
  - Cloud: Convenience, but third-party sees your data
- **Recommendation:** Start self-hosted (Docker Compose), migrate to cloud if needed
- Encryption at rest for sensitive content?
- How to handle API keys for external services (YouTube, etc.)?

### **CD2: Observability Strategy**
- **Logging:** Structured logs (JSON), centralized (ELK stack?)
- **Metrics:** Prometheus + Grafana for system health
- **Tracing:** OpenTelemetry if distributed
- **ML Metrics:** Model performance dashboard
  - Precision/recall of recommendations
  - User engagement rates
  - Feedback volume over time

### **CD3: Testing Strategy**
- **Unit tests:** Core business logic
- **Integration tests:** End-to-end workflows
- **ML tests:** Model performance, data quality
- **Decision:** Test coverage threshold? (80%?)

### **CD4: Scalability Horizon**
Design for your expected scale:
- **Year 1:** 1 user, 50 sources, 500 items/day = 180K items/year
- **Year 3:** 10 users, 100 sources, 5K items/day = 1.8M items/year

Most components can handle this on single machine. Premature optimization = waste.

**Bottleneck prediction:**
1. Vector search (100K+ items)
2. ML inference (if real-time)
3. Storage (multimedia content)

### **CD5: Development Phases**

**Phase 1: MVP (4-6 weeks)**
- Layers: Infrastructure + Ingestion + Data + Basic Application + Simple Web UI
- Features: 3 source types, daily digest, manual categorization
- **Goal:** Usable system generating value

**Phase 2: Preference Learning (2-3 months)**
- Add: Intelligence layer (basic ML)
- Features: Implicit feedback tracking, simple recommendations
- **Goal:** System learns from usage

**Phase 3: Advanced Intelligence (3-6 months)**
- Enhance: Intelligence layer (LLM integration, RLHF)
- Features: Connection discovery, auto-categorization
- **Goal:** System becomes autonomous

---

## Recommended Technology Stack

Given all decisions above:

**Infrastructure:**
- Container: Docker + Docker Compose → Kubernetes (if needed)
- Message Queue: Redis + Celery
- Scheduler: Celery Beat
- Auth: JWT tokens

**Backend:**
- Language: Python (ML ecosystem, rapid development)
- Framework: FastAPI (async, great API docs, modern)
- ORM: SQLAlchemy

**Data:**
- Primary DB: PostgreSQL 15+ (with pgvector)
- Cache: Redis
- Object Storage: MinIO (S3-compatible, self-hostable)

**Intelligence:**
- Embeddings: sentence-transformers
- Vector search: pgvector → Qdrant (if scaling needed)
- ML Framework: scikit-learn → PyTorch (for deep learning)
- LLM: Ollama (self-hosted) or OpenAI API
- RLHF: TRL library (Transformer Reinforcement Learning)

**Frontend:**
- Framework: React + TypeScript
- Build: Vite
- UI: Tailwind CSS + shadcn/ui
- State: React Query (for API) + Zustand (for local state)

**Obsidian:**
- Plugin using Obsidian API + your REST API

**Monitoring:**
- Logging: Python logging → stdout → Docker logs
- Metrics: Prometheus + Grafana (add later)
- Error tracking: Sentry (optional)

---

## Key Architectural Principles

1. **Loose Coupling:** Each layer depends only on interface of layer below
2. **High Cohesion:** Related functionality grouped together
3. **Separation of Concerns:** ML training ≠ serving ≠ application logic
4. **Fail Gracefully:** If ML fails, fall back to simpler methods
5. **Observable:** Every layer emits metrics and logs
6. **Testable:** Each component can be tested in isolation
7. **Evolvable:** Start simple, add complexity only when needed

## What Makes This Different From Standard CRUD App?

The **Intelligence Layer** is your differentiator. Most systems are:
```
UI → Business Logic → Database
```

Yours is:
```
UI → Business Logic → Intelligence (learns, predicts, discovers) → Database
```

This creates a **feedback loop** where the system improves over time. The architecture must support:
- Continuous learning pipeline
- Experimentation (A/B testing models)
- Feature engineering workflows
- Model versioning and rollback

That's why the Intelligence Layer is first-class, not an afterthought.
