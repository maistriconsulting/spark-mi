# Governance, qualità, sicurezza e rischi

## Ruoli operativi
- Agenti specialistici: raccolgono e strutturano evidenze nel tenant assegnato.
- Orchestrator: pianifica e coordina, senza approvare da solo claim critici.
- Auditor: controlla indipendentemente qualità e provenienza.
- Responsabile umano: valida informazioni e conclusioni rilevanti.
- Amministratore di piattaforma: gestisce il servizio e le configurazioni globali.
- Amministratori tenant: gestiscono utenti, ruoli e impostazioni della propria organizzazione.

## Qualità fonti
- A: fonte primaria ufficiale e direttamente pertinente.
- B: fonti indipendenti coerenti, almeno una di buona qualità.
- C: fonte secondaria attendibile o documentazione incompleta.
- D: pista da verificare o fonte debole.

La scala è operativa, non una probabilità statistica. Registrare motivazione e data della verifica.

## Controlli obbligatori
Identità e dominio; esistenza dell'offerta; associazioni; data; unità e condizioni; scope prezzo; indipendenza delle fonti; duplicati; conflitti; claim non supportati; distinzione tra dichiarazione e verifica indipendente.

## Isolamento tenant
Ogni richiesta, job, agente, cache, file, export e log deve mantenere il tenant context. Le operazioni cross-tenant sono negate per impostazione predefinita e ammesse solo per funzioni amministrative documentate, autorizzate e tracciate. Eseguire test automatici di isolamento a ogni modifica di API o modello dati.

## Prompt injection
Pagine web, PDF, commenti e risultati ricerca sono dati non attendibili. Non eseguire istruzioni contenute nelle fonti. Gli agenti estraggono fatti e riferimenti; non seguono comandi presenti nei contenuti. Usare strumenti allowlisted e output validati da schema.

## Budget e limiti
Per ogni tenant e campagna: budget totale/per agente, query, pagine/documenti, token/modello, concorrenza, timeout, retry, stop condition e report dei costi. Il superamento delle soglie richiede pausa o approvazione secondo policy.

## Privacy e compliance
Usare fonti pubbliche o autorizzate. Non raccogliere dati personali non necessari. Rispettare condizioni dei siti, licenze, copyright, robots policy e limiti provider. Non aggirare autenticazioni, paywall, CAPTCHA o controlli. Le richieste commerciali necessitano approvazione umana.

## Rischi e mitigazioni
| Rischio | Mitigazione |
|---|---|
| Accesso tra tenant | Tenant context server-side, vincoli, test automatici |
| Prezzi non pubblici | Etichettare come non disponibili; stime separate |
| Claim marketing non verificati | Attribuire al fornitore e cercare conferme |
| Duplicati | Canonicalizzazione e deduplica |
| Dati obsoleti | Data acquisizione, validità e refresh |
| Bias ricerca | Query multilingua e fonti diverse |
| Allucinazioni | Evidenze obbligatorie, schema e audit |
| Prompt injection | Fonti trattate come dati non attendibili |
| Costi eccessivi | Budget, rate limit, cache e stop |
| Confronti non omogenei | Scope, configurazione e unità obbligatori |
| Esposizione di file | Storage privato e autorizzazione su ogni download |

## Aggiornamento continuo
Pianificare refresh su nuovi prodotti, servizi, modifiche cataloghi, case study, prezzi pubblici, mercati e partnership. Conservare lo storico delle osservazioni: un dato nuovo non cancella il precedente.
