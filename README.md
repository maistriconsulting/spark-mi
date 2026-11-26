# SPARK Market Intelligence

**SPARK-MI** è una piattaforma modulare di Market Intelligence basata su agenti AI coordinati. È progettata per essere utilizzata da più aziende, su mercati, settori, aree geografiche e categorie di prodotto differenti.

Ogni azienda lavora in uno spazio isolato (tenant) con utenti, progetti, campagne, fonti, dati, agenti, budget e report propri. Il motore applicativo, gli strumenti e le tassonomie comuni possono essere condivisi senza esporre i dati riservati tra aziende.

## Repository

- `backend/`: API FastAPI, autenticazione, tenancy e accesso MariaDB.
- `frontend/`: React + TypeScript, compilato come sito statico per Hostinger.
- `docs/`: architettura, modello dati, agenti, tenancy, governance e roadmap.

## Foundation in sviluppo

La prima foundation implementa autenticazione email/password, bootstrap iniziale protetto, selezione organizzazione, membership e ruoli, tenant context verificato lato server, progetti tenant-scoped, health checks e prima dashboard web.

## Sviluppo

Consultare [backend/README.md](backend/README.md) e [frontend/README.md](frontend/README.md). Configurazione ambiente di riferimento: [.env.example](.env.example).

Non inserire mai credenziali, token o chiavi reali nel repository. I file `.env` sono esclusi da Git.

## Documentazione
- [Project charter](docs/project-charter.md)
- [Architettura tecnica](docs/architecture.md)
- [Agenti e responsabilità](docs/agents.md)
- [Modello dati](docs/data-model.md)
- [Isolamento multi-tenant](docs/tenancy.md)
- [Piano di ricerca](docs/research-plan.md)
- [Roadmap](docs/roadmap.md)
- [Governance e qualità](docs/governance.md)
