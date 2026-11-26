# Stato del rilascio

**Aggiornato:** 26 novembre 2026  
**Ramo di riferimento:** `feat/multi-tenant-foundation` (`main` non modificato, PR #2 aperta)  
**Versione distribuita:** `996d78b` (backend e frontend)  
**Schema database:** `0003_audit_events`

## Primo rilascio: foundation e superadmin

Distribuito e **superadmin attivato**: il server riporta `bootstrap-status` `initialized=true` e `BOOTSTRAP_TOKEN` è vuoto. Il bootstrap non è ripetibile. Lo script di attivazione resta in `backend/scripts/activate_superadmin.py`.

## Secondo rilascio: identità Spark e gestione piattaforma

Comprende colori e logo Spark; gestione di organizzazioni, utenti e ruoli riservata al superadmin; registro attività; password temporanee e cambio password; blocco effettivo delle organizzazioni sospese. Dettagli in `backend/README.md`.

Verifiche eseguite:

- 13 test backend superati sul server (SQLite);
- percorso completo nell'interfaccia in locale, con account usa e getta su SQLite; layout controllato a 390 px prima dell'ultima modifica CSS al menu mobile;
- backup delle tabelle prima della migrazione, sul server Fedora in `~/backups/spark-mi/pre-996d78b.json` (permessi 600, contiene hash delle password);
- migrazione `0003_audit_events` applicata su MariaDB;
- in produzione: `/ready` 200, API di gestione senza autenticazione 401, preflight CORS per `PATCH` accettato, bundle pubblicato identico alla build.

**Da verificare dal titolare in produzione:** accesso superadmin e creazione della prima organizzazione.

Rollback: backend a `45f1a1c` (la tabella `audit_events` può restare); frontend da `domains/sparkmi.maistriconsulting.com/backups/public_html-pre-996d78b.tgz`.

## Limiti noti

- Nessun invito via email: la password temporanea va consegnata a mano; il cambio non è obbligatorio al primo accesso.
- Owner e admin non possono gestire i membri della propria organizzazione: lo fa solo il superadmin.
- Cambio o reset della password non revocano i token già emessi (scadono entro la durata configurata); la disattivazione è immediata.
- Il login non ha limitazione dei tentativi.
- La connessione a MariaDB usa TLS ma non verifica il certificato.
- La sessione si perde ricaricando la pagina.
- Il server Fedora è una soluzione temporanea per il backend.
- Il flusso di deploy sul ramo `chore/frontend-dist-deploy` e la guida `docs/hostinger-ssh-deploy.md` sono superati: il frontend si pubblica compilando in locale e sincronizzando `dist/`.
