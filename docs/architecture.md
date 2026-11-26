# Architettura tecnica

## Principi
SPARK-MI sarà modulare, indipendente dal fornitore LLM e guidato da workflow. Gli agenti eseguono task circoscritti con input/output tipizzati; l'orchestratore governa stato, dipendenze, retry, checkpoint, budget e approvazioni. Gli agenti non scrivono direttamente dati canonici senza passare dai servizi applicativi e dai controlli.

## Componenti
1. API/backend: progetti, campagne, ricerche, utenti e permessi.
2. Orchestratore: piano di ricerca, dipendenze, routing e stato dei workflow.
3. Agent runtime: ruoli, prompt versionati, strumenti e output strutturati.
4. Search Gateway: adapter verso provider di ricerca web.
5. Browser/document acquisition: acquisizione controllata di pagine e documenti pubblici.
6. Extraction pipeline: parsing HTML/PDF, normalizzazione e deduplica.
7. Evidence service: URL, estratti, data di accesso e collegamento ai claim.
8. Database: PostgreSQL; pgvector opzionale per ricerca semantica.
9. Object storage: documenti, snapshot e checksum.
10. Queue/worker: esecuzione asincrona e concorrenza limitata.
11. Dashboard: campagne, agenti, fonti, risultati, anomalie e approvazioni.
12. Reporting: XLSX/CSV/PDF con collegamenti alle evidenze.
13. Observability: log, metriche, tracing, tempi, token, costi ed errori.

## Stack proposto
| Area | Proposta iniziale |
|---|---|
| Linguaggio | Python |
| API | FastAPI |
| Orchestrazione | LangGraph |
| Database | PostgreSQL |
| Ricerca semantica | pgvector, opzionale |
| Browser automation | Playwright |
| Queue | Redis + worker, da validare nel PoC |
| Frontend | React + TypeScript |
| Deploy iniziale | Docker Compose |

Le scelte sono proposte da validare in Fase 0 e con un proof of concept. Evitare dipendenze obbligatorie non giustificate dal carico reale.

## Workflow end-to-end
1. Utente crea una campagna con geografia, applicazioni, categorie e obiettivi.
2. Planner genera work package e task.
3. Search Gateway esegue discovery con query multilingua.
4. Risultati vengono deduplicati e registrati come candidati, non come fatti.
5. Agenti approfondiscono aziende, prodotti, tecnologie, prezzi e mercati.
6. Extraction pipeline crea record e claim strutturati, collegandoli alle evidenze.
7. Research Auditor verifica i risultati.
8. Informazioni incerte generano follow-up o revisione umana.
9. Dati approvati vengono consolidati.
10. Reporting genera viste e report.

## Stato dei job
Stati minimi: queued, planned, running, waiting_for_dependency, needs_review, completed, failed, cancelled.

Ogni job registra ID, campagna, agente, versione prompt, input, output, fonti, tentativi, tempi, costo e motivazione di fallimento.

## Contratto agenti
Ogni agente riceve un ResearchTask e produce un AgentResult validabile con: task_id, agent_id, status, summary, entities, claims, evidence_refs, gaps, follow_up_tasks, confidence, limitations e model_metadata. Gli schemi saranno implementati in Pydantic e versionati.

## Concorrenza e affidabilità
Limiti configurabili per provider/agente/campagna; rate limit; backoff; timeout; retry solo per errori recuperabili; idempotenza; cache con scadenza; circuit breaker; budget e stop condition. Non aggirare login, paywall, CAPTCHA, robots policy o controlli di accesso.

## Sicurezza
Segreti fuori dal repository; ruoli e permessi; audit log; input sanitizzati; contenuti web trattati come dati non attendibili e non come istruzioni; backup e restore testati.