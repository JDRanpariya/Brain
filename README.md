# Brain
Fully Open Source Personalized Content Streamer

# Architecture

┌─────────────────────────────────────────────────────────────────┐
│                          Presentation                           │
│  React + TypeScript SPA (Next.js/SvelteKit optional)            │
│  Obsidian plugin ↔ REST API                                     │
└─────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────┐
│                          Application                            │
│  FastAPI backend: digest compiler, reading queue, exports, API  │
│  Business workflows, preference overrides                       │
└─────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────┐
│                          Intelligence                           │
│  Precomputed embeddings (sentence-transformers)                 │
│  Recommendation engine: ranking model + fallback rules          │
│  Reward model (for RLHF) + offline policy training pipeline     │
│  Connection discovery (batch graph/clustering)                  │
└─────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────┐
│                             Data                                │
│  PostgreSQL (primary) + JSONB + pgvector                        │
│  MinIO (object store) for large files, transcript storage       │
│  Redis (cache, ephemeral state)                                 │
└─────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────┐
│                           Ingestion                             │
│  Connectors (start hardcoded, evolve to plugin adapters)        │
│  Async pipeline: fetchers → parser workers → normalization      │
│  Deduplication, transcript extraction, metadata enrichment      │
└─────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────┐
│                        Infrastructure                           │
│  Docker Compose (local) → Kubernetes if needed                  │
│  Redis Streams (task bus), Celery (workers), Celery Beat        │
│  Secrets manager, logging, Prometheus + Grafana, Sentry         │
└─────────────────────────────────────────────────────────────────┘


# TODO
- [ ] Use [YT Api](https://developers.google.com/youtube/v3) to get videos uploaded by my subscribed channels yesterday.
  - [X] get list of all channels and store it in db
  - [ ] For each channel get videos uploaded yesterday/last 24 hours.
- [ ] Setup .env and find out ways to show the data in neat format
- [ ] on hover it should play the video in small frame
- [ ] on shortcut it should go to my obsidian with resource template, add to weekly review as well
- [ ] Figure out consumption sources

### Consumption Sources
- [ ] Personal Youtube Subscriptions
- [ ] Research Papers
  - [ ] arXiv Sanity Preserver to track ML related papers
  - [ ] Use PubMed Alerts, Google Scholar Alerts, and Semantic Scholar for neuroscience, biology, and anthropology.
  - [ ] Explore Services like Zotero, Paperpile, and Mendeley can help organize relevant papers.
  - [ ] AI based Filtering and clustering and abstract summarization.
    - [ ] AI-assisted Abstract Summarization and Relevance Scoring
    - [ ] Train an LLM (like GPT) on papers you find interesting to generate scores for relevance.
    - [ ] Use embeddings (like OpenAI's text-embedding-ada-002) to vectorize abstracts and compare them to abstracts you previously liked.
  - [ ] Tracking Research Trends Over Time???
  - [ ] Follow leading researchers on Google Scholar and ResearchGate to track influential publications?? 


# Workflow
![](https://github.com/JDRanpariya/Brain/blob/main/brain.jpeg)
