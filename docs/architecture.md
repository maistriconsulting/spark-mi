# Architettura tecnica

## Principi
SPARK-MI è una piattaforma SaaS multi-tenant, modulare e indipendente dal fornitore LLM. L'orchestratore governa workflow, dipendenze, retry, checkpoint, budget e approvazioni. Gli agenti eseguono task circoscritti con input/output tipizzati e non scrivono direttamente nei dati canonici.

Il tenant attivo è determinato dal contesto autenticato e verificato dal backend. Non deve essere accettato come criterio di autorizzazione un tenant_id arbitrario inviato dal client.

## Componenti
1. Frontend: dashboard, gestione organizzazioni, progetti, campagne e report.
2. API/backend: autenticazione, autorizzazione, tenant context e servizi applicativi.
3. Orchestratore: pianificazione, dipendenze, routing, stato e checkpoint.
4. Agent runtime: ruoli, prompt versionati, strumenti e output strutturati.
5. Search Gateway: adapter verso provider di ricerca.
6. Browser/document acquisition: acquisizione controllata di pagine e documenti accessibili.
7. Extraction pipeline: parsing HTML/PDF, normalizzazione e deduplica.
8. Evidence service: URL, estratti, data di accesso e collegamento ai claim.
9. Database relazionale: organizzazioni, utenti, progetti, dati di ricerca e audit.
10. Object storage: documenti, snapshot e checksum con percorsi e policy per tenant.
11. Queue/worker: esecuzione asincrona e concorrenza limitata.
12. Reporting: XLSX/CSV/PDF con collegamenti alle evidenze.
13. Observability: log, metriche, tracing, tempi, token, costi ed errori.

## Stack proposto
| Area | Proposta iniziale |
|---|---|
| Linguaggio | Python |
| API | FastAPI |
| Orchestrazione | LangGraph |
| ORM e migrazioni | SQLAlchemy + Alembic |
| Database iniziale | MariaDB |
| Database alternativi | PostgreSQL, previa verifica compatibilità |
| Browser automation | Playwright |
| Queue | Redis + worker |
| Frontend | React + TypeScript |
| Deploy | Docker Compose su VPS o ambiente container |
| Test | pytest, test API e test di isolamento tenant |

MariaDB è il target iniziale per la compatibilità con l'infrastruttura disponibile. Lo schema deve evitare funzionalità proprietarie non necessarie e mantenere le query portabili dove ragionevole. PostgreSQL resta un'opzione futura, non un requisito per il primo rilascio.

## Workflow end-to-end
1. L'utente autenticato seleziona un'organizzazione di cui è membro.
2. Il backend verifica membership e ruolo e crea un tenant context non falsificabile dal client.
3. L'utente crea un progetto e una campagna con perimetro configurabile.
4. Il planner genera work package e task.
5. Il Search Gateway esegue discovery con query multilingua.
6. I risultati vengono deduplicati e registrati come candidati, non come fatti.
7. Gli agenti approfondiscono le entità e i temi previsti dalla campagna.
8. La pipeline crea record e claim strutturati collegati alle evidenze.
9. L'auditor verifica i risultati.
10. I dati approvati vengono consolidati e resi disponibili al tenant.
11. Reporting genera viste ed esportazioni nel perimetro autorizzato.

## Contratto agenti
Ogni agente riceve un ResearchTask e produce un AgentResult validabile con: task_id, tenant_id, project_id, agent_id, status, summary, entities, claims, evidence_refs, gaps, follow_up_tasks, confidence, limitations e model_metadata. Gli schemi saranno implementati in Pydantic e versionati.

## Stato dei job
Stati minimi: queued, planned, running, waiting_for_dependency, needs_review, completed, failed, cancelled. Ogni job registra tenant_id, progetto, campagna, agente, versione prompt, input, output, fonti, tentativi, tempi, costo e motivazione di fallimento.

## Concorrenza e affidabilità
Limiti configurabili per provider, agente, campagna e tenant; rate limit; backoff; timeout; retry solo per errori recuperabili; idempotenza; cache con scadenza; circuit breaker; budget e stop condition. Le chiavi di cache devono includere il corretto ambito di visibilità per evitare contaminazioni tra tenant.

## Sicurezza
Segreti fuori dal repository; autenticazione robusta; ruoli e permessi; tenant scoping obbligatorio; audit log; input sanitizzati; contenuti web trattati come dati non attendibili e non come istruzioni; backup e restore testati. I test devono verificare accessi negati tra tenant su API, query, file, job, export e log.
