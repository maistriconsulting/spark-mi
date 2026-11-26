# Isolamento multi-tenant

## Modello iniziale
SPARK-MI adotta un modello shared application / shared database con separazione logica rigorosa tramite tenant_id. È il compromesso iniziale più semplice da gestire e scalare. L'architettura deve consentire in futuro database o schema dedicato per clienti con requisiti enterprise.

## Identità e contesto
1. L'utente si autentica.
2. Seleziona un'organizzazione di cui risulta membro attivo.
3. Il backend verifica membership, stato e ruolo.
4. Il tenant context viene creato lato server per la richiesta.
5. Tutti i servizi, repository, task asincroni e accessi a file ricevono il contesto verificato.

Il client non può ottenere accesso a un tenant cambiando tenant_id in URL, query string, body, header o identificativo di una risorsa.

## Autorizzazione
Ruoli iniziali:
- owner: gestione completa dell'organizzazione e dei membri.
- admin: gestione utenti, progetti, campagne e configurazioni del tenant.
- analyst: creazione ed esecuzione di ricerche.
- reviewer: revisione, validazione e approvazione.
- viewer: sola consultazione autorizzata.

`superadmin` non è un ruolo di membership: è un flag globale dell'utente, assegnabile solo tramite controlli amministrativi della piattaforma. Non aggira il tenant context delle API tenant-scoped; le funzioni globali devono dichiararlo esplicitamente, richiedere il controllo server-side del flag e produrre audit.

Applicare il principio del minimo privilegio. Le autorizzazioni vanno verificate lato server per ogni operazione, non solo nascondendo elementi nell'interfaccia.

## Protezione dei dati
- tenant_id obbligatorio su ogni record tenant-owned.
- Foreign key e vincoli coerenti per impedire associazioni tra tenant differenti.
- Query filtrate dal tenant context in un livello applicativo centrale.
- File object storage organizzati per tenant con policy di accesso.
- Cache, code, eventi, log applicativi ed export con namespace tenant.
- Nessun dato di un tenant nei prompt, report o risultati di un altro tenant.
- Operazioni amministrative cross-tenant soggette a permessi elevati e audit.

## Dati condivisi
Le tassonomie di base e i template pubblici possono essere globali. I dati raccolti durante una ricerca, le note, le evidenze private, i report e le configurazioni restano tenant-scoped. Un'eventuale condivisione volontaria deve essere esplicita, granulare, revocabile e tracciata.

## Test obbligatori
- Un utente del tenant A non può leggere, modificare o cancellare record del tenant B.
- Non è possibile collegare un prodotto del tenant A a un'azienda del tenant B.
- Job, agenti, cache, file ed export non possono attraversare il confine tenant.
- La rimozione di membership revoca l'accesso alle richieste successive.
- I ruoli viewer e analyst non possono eseguire azioni riservate.
- I test coprono ID indovinati, URL diretti, API, filtri, paginazione e operazioni in background.

## Evoluzione
Per clienti con esigenze particolari si potrà introdurre database dedicato, chiavi di cifratura dedicate, retention personalizzata e localizzazione geografica dei dati, senza cambiare il modello funzionale di progetti e campagne.
