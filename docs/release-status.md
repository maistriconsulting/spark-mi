# Stato del rilascio — foundation multi-tenant e superadmin

**Aggiornato:** 26 novembre 2026  
**Ramo di riferimento:** `feat/multi-tenant-foundation`  
**Versione distribuita:** `45f1a1c` (codice applicativo backend identico a `3101f02`)

## Stato attuale

Backend e frontend sono **distribuiti**. Il rilascio **non è concluso**: manca l'attivazione del superadmin. Il ramo `main` non è stato modificato.

Eseguito il 26 novembre 2026:

- database verificato vuoto (nessuna tabella) prima della migrazione, quindi nessun dato da salvare; rollback del backend: commit `3ab5a8b`;
- backend aggiornato sul server Fedora, 6 test superati sul server;
- migrazioni applicate su MariaDB fino a `0002_superadmin` (head);
- verifiche pubbliche: `/ready` 200, `bootstrap-status` `initialized=false`, panoramica senza autenticazione 401, bootstrap senza token 404, login errato 401, CORS per l'origine del frontend;
- frontend compilato da `45f1a1c` e pubblicato; pagina di accesso verificata nel browser senza errori in console. Backup del sito precedente in `domains/sparkmi.maistriconsulting.com/backups/public_html-pre-45f1a1c.tgz`;
- script di attivazione provato end-to-end su un'API locale con database SQLite.

Da eseguire: punti 7-11 della sequenza (script di attivazione, con password scelta dal titolare, e login reale). `BOOTSTRAP_TOKEN` è configurato sul server e resta attivo fino a quel momento.

## Limiti noti

- Dopo l'attivazione non esiste alcuna funzione (API, script o interfaccia) per creare organizzazioni e membership: la piattaforma non è ancora utilizzabile per progetti.
- Il login non ha limitazione dei tentativi.
- La connessione a MariaDB usa TLS ma non verifica il certificato.
- La sessione si perde ricaricando la pagina; le voci del menu laterale non sono ancora funzionanti.
- Il server Fedora è una soluzione temporanea per il backend.

## Perimetro funzionale del primo rilascio

Il primo rilascio comprende:

- account globale superadmin con email iniziale fissata a `info@maistriconsulting.com`;
- bootstrap monouso protetto da `X-Bootstrap-Token`;
- password scelta al momento dell'attivazione, con lunghezza minima di 12 caratteri;
- autenticazione ordinaria;
- verifica del ruolo superadmin lato database;
- panoramica globale della piattaforma e lista delle organizzazioni attive;
- mantenimento dell'isolamento tenant.

Il superadmin è un attributo globale dell'utente, non un ruolo di membership. Il bootstrap crea **solo l'utente superadmin**: non crea tenant né membership. Di conseguenza, l'account non ottiene automaticamente accesso ai dati delle organizzazioni.

Le API tenant-scoped continuano a richiedere il tenant context e una membership attiva. Il superadmin non aggira `get_tenant_context`.

La gestione e modifica delle organizzazioni non fanno parte del perimetro di questo rilascio. Non sono previste ulteriori funzionalità nel batch corrente.

## Endpoint interessati

- `POST /api/v1/auth/bootstrap`: inizializzazione protetta; richiede l'header `X-Bootstrap-Token`. Il token errato o assente rende l'endpoint non disponibile (404); se esiste già un utente o un tenant, la richiesta viene rifiutata con 409.
- `GET /api/v1/auth/bootstrap-status`: indica se l'inizializzazione risulta già completata.
- `POST /api/v1/auth/login`: autenticazione ordinaria.
- `GET /api/v1/auth/platform/overview`: panoramica riservata al superadmin globale.

Il token di bootstrap non deve essere inserito nel frontend, nel repository, nei log o nella cronologia dei comandi. La chiamata di inizializzazione deve essere eseguita da un contesto fidato sul server, con password inserita interattivamente.

## Verifiche già eseguite in ambiente di sviluppo

Secondo il rapporto di revisione e integrazione:

- test backend: 6 superati;
- compilazione Python di applicazione e migrazioni: superata;
- build frontend Vite: superata;
- `git diff --check`: superato;
- test esistente di isolamento tenant: superato.

Questi risultati non sostituiscono le verifiche sull'ambiente reale dopo il deploy.

## Sequenza vincolante per il rilascio

1. Predisporre l'accesso autorizzato al server Fedora.
2. Verificare il commit di rilascio e lo stato del servizio.
3. Eseguire e verificare il backup del database; predisporre il rollback del backend.
4. Distribuire il backend dal commit `3101f02`.
5. Applicare la migrazione Alembic `0002_superadmin`.
6. Configurare temporaneamente `BOOTSTRAP_TOKEN` nell'ambiente protetto del servizio e riavviare il backend.
7. Eseguire `backend/scripts/activate_superadmin.py` da console interattiva sul server (vedi `backend/README.md`), con password scelta e digitata al momento.
8. Costruire e pubblicare il frontend dallo stesso commit, dopo aver verificato la disponibilità degli endpoint backend.
9. Verificare il login reale di `info@maistriconsulting.com`, l'accesso alla panoramica globale e la lista delle organizzazioni.
10. Con il token ancora configurato, verificare che un nuovo tentativo di bootstrap venga rifiutato con `409`.
11. Rimuovere `BOOTSTRAP_TOKEN`, riavviare il servizio e verificare che l'endpoint risponda `404`.

Lo script del punto 7 esegue anche le verifiche API del punto 9 e i punti 10 e 11. Il frontend non contiene un modulo di bootstrap, quindi la sua pubblicazione non dipende dal punto 7.

Non pubblicare il frontend prima del backend: la nuova interfaccia richiama endpoint introdotti da questa integrazione.

## Criterio di chiusura

Il batch può essere dichiarato concluso solo dopo il completamento della sequenza di rilascio, la verifica del login reale e la conferma che il token temporaneo è stato rimosso e il bootstrap non è più ripetibile.

Fino ad allora lo stato resta: **distribuito, in attesa di attivazione, non concluso**.
