# Roadmap e criteri di accettazione

## Fase 0 — Fondamenta di prodotto e requisiti
Definire utenti, organizzazioni, ruoli, modello di tenancy, perimetro funzionale, requisiti non funzionali, provider, tassonomie e decisioni architetturali.
**Accettazione:** charter generico approvato; decision log avviato; modello multi-tenant e threat model revisionati.

## Fase 1 — Foundation
Repository, convenzioni, FastAPI, MariaDB, SQLAlchemy, Alembic, autenticazione, membership, tenant context, logging, segreti e CI essenziale.
**Accettazione:** ambiente riproducibile; migrazioni funzionanti; health check e test minimi; nessun segreto nel repository; test di isolamento tenant superati.

## Fase 2 — Core workspace
Organizzazioni, utenti, ruoli, progetti, campagne, configurazioni, audit e API.
**Accettazione:** più organizzazioni possono operare; un utente accede solo agli spazi per cui ha membership e permessi.

## Fase 3 — Search ed evidence pipeline
Search Gateway astratto, primo provider, acquisizione/parsing HTML e PDF, normalizzazione URL, deduplica, sources/evidence/claims, rate limit, cache e budget.
**Accettazione:** query e risultati tracciati; ogni claim mantiene la fonte; errori di accesso espliciti; nessuna contaminazione tra tenant.

## Fase 4 — Agenti pilota
Competitor, Product/Service, Pricing e Auditor essenziale.
**Accettazione:** schede validate da schema; nessun prezzo inventato; auditor segnala lacune e conflitti; revisione umana del campione.

## Fase 5 — Orchestrazione completa
Aggiungere Technology, Market, Customer, Business Model e Strategic Intelligence; dipendenze, checkpoint, follow-up e approvazioni.
**Accettazione:** campagna end-to-end; task riprendibili senza duplicazioni; budget applicati; stato e motivi degli errori consultabili.

## Fase 6 — Dashboard e reporting
Campagne, job, schede, prezzi, tecnologie, fonti, audit, filtri, confronti ed esportazioni.
**Accettazione:** creazione/monitoraggio campagne; accesso dalle schede alle evidenze originali; export con ID e URL; permessi rispettati.

## Fase 7 — Validazione multi-tenant
Eseguire campagne di prova su mercati e settori differenti con organizzazioni separate; verificare isolamento, copertura, bias, costi, tempi e qualità.
**Accettazione:** nessun accesso cross-tenant; claim pubblicati con evidenze; stime separate dai prezzi osservati; limiti dichiarati.

## Priorità
P0: tenancy, autenticazione, schemi, database, progetti/campagne, Search Gateway, fonti/evidenze, agenti pilota e auditor.
P1: agenti aggiuntivi, orchestrazione avanzata, dashboard ed esportazioni.
P2: refresh programmati, ulteriori provider, analytics, condivisione controllata e opzioni enterprise.
