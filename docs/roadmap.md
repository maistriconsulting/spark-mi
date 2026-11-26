# Roadmap e criteri di accettazione

## Fase 0 — Discovery tecnica e requisiti
Verificare ambiente, API, budget, ruoli, requisiti non funzionali, provider e tassonomie. Definire schemi Pydantic.
**Accettazione:** architettura approvata, decision log avviato, modello dati e contratti agenti revisionati.

## Fase 1 — Foundation
Repository, convenzioni, FastAPI, PostgreSQL, migrazioni, configurazione, logging, segreti e CI essenziale.
**Accettazione:** ambiente riproducibile, migrazioni funzionanti, health check e test minimi, nessun segreto nel repository.

## Fase 2 — Search ed evidence pipeline
Search Gateway astratto, primo provider, acquisizione/parsing HTML e PDF, normalizzazione URL, deduplica, sources/evidence/claims, rate limit, cache e budget.
**Accettazione:** query e risultati tracciati; ogni claim mantiene la fonte; errori di accesso espliciti; contenuti web non possono modificare istruzioni del sistema.

## Fase 3 — Agenti pilota
Competitor, Product, Pricing e Auditor essenziale.
**Accettazione:** almeno 10 aziende pilota esaminate; schede validate da schema; nessun prezzo inventato; auditor segnala lacune e conflitti; revisione umana del campione.

## Fase 4 — Orchestrazione completa
Aggiungere Technology, Market, Customer, Business Model e Strategic Intelligence; dipendenze, checkpoint, follow-up e approvazioni.
**Accettazione:** campagna end-to-end; task riprendibili senza duplicazioni; budget applicati; stato e motivi degli errori consultabili.

## Fase 5 — Dashboard e reporting
Campagne, job, schede aziende/prodotti, prezzi, tecnologie, fonti, audit, filtri, confronti ed esportazioni.
**Accettazione:** creazione/monitoraggio campagne; accesso dalle schede alle evidenze originali; export con ID e URL; permessi rispettati.

## Fase 6 — Validazione di mercato
Eseguire la campagna Italia + benchmark europeo; analizzare copertura, bias, campione dei claim/prezzi, costi e tempi; consolidare report e backlog.
**Accettazione:** 100% claim pubblicati con evidenze; stime separate dai prezzi osservati; limiti dichiarati; report strategico approvato.

## Stima
La stima preliminare di 23–31 giorni è indicativa per un MVP con requisiti stabili e sviluppo parallelo. Va ricalibrata dopo la Fase 0 e il PoC del Search Gateway.

## Priorità
P0: schemi, database, Search Gateway, fonti/evidenze, tre agenti pilota, auditor.
P1: altri agenti, orchestrazione avanzata, dashboard ed esportazioni.
P2: refresh programmati, ulteriori provider, analytics e confronto storico.