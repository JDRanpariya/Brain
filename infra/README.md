## Infra

Purpose: The infra layer is the foundation that makes all other layers (ingestion, data, intelligence, backend, frontend) possible and maintainable. Its main role is orchestration, environment management, task scheduling, secrets management, and observability.

| Responsibility               | Why It’s Needed                                                              |
| ---------------------------- | ---------------------------------------------------------------------------- |
| **Environment isolation**    | Keep dev, staging, prod separate. Avoid “it works on my machine” problem.    |
| **Service orchestration**    | Manage multiple services (Postgres, Redis, MinIO, backend, frontend) easily. |
| **Task scheduling**          | Run periodic jobs like fetching content, compiling digest, training models.  |
| **Secrets management**       | Securely store API keys, DB credentials, MinIO passwords.                    |
| **Monitoring & logging**     | Observe system health, catch errors, diagnose bottlenecks.                   |
| **Configuration management** | Central place for env vars, port configs, feature flags, toggles.            |

Infra is all about making the system reproducible, observable, and maintainable.

- Current plan is to use docker compose maybe later think about k8s and if we even need them.

