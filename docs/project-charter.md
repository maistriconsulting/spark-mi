# Project charter — SPARK-MI

## Scopo
Progettare e realizzare una piattaforma multi-tenant di Market Intelligence che consenta a organizzazioni diverse di pianificare, eseguire e verificare ricerche su mercati differenti. La piattaforma combina workflow configurabili, agenti AI specialistici, fonti tracciabili, un database strutturato e strumenti di analisi.

SPARK-MI deve essere un prodotto riutilizzabile: nessun settore, paese, prodotto, cliente o caso d'uso deve essere incorporato come perimetro obbligatorio nel codice o nel modello dati.

## Utenti e organizzazioni
- Un'organizzazione (tenant) può avere più utenti.
- Ogni utente può appartenere a una o più organizzazioni, secondo i permessi assegnati.
- Ogni organizzazione può gestire più progetti e campagne.
- Ruoli, budget, configurazioni, dati e report sono associati al tenant.
- Un amministratore di piattaforma può gestire il servizio senza ottenere automaticamente accesso ai contenuti riservati dei tenant.

## Perimetro funzionale
- Gestione organizzazioni, utenti, ruoli e inviti.
- Gestione progetti, campagne, obiettivi, mercati e perimetri di ricerca.
- Pianificazione e orchestrazione di task e agenti.
- Discovery e analisi di aziende, prodotti, servizi, tecnologie, settori, clienti e modelli commerciali.
- Raccolta di fonti, evidenze e claim verificabili.
- Audit, approvazioni, report, esportazioni e storico.
- Configurazione di provider, modelli AI, limiti e budget.
- Tassonomie globali e personalizzazioni controllate per organizzazione.

## Configurabilità
Ogni campagna definisce il proprio perimetro: mercati geografici, lingue, settori, categorie, applicazioni, concorrenti, domande, profondità, fonti consentite e criteri di completamento. I template possono accelerare la configurazione ma non devono imporre uno specifico mercato.

## Output attesi
Piattaforma web multi-tenant; API documentate; database strutturato; orchestratore; agenti specializzati; gestione fonti/evidenze; dashboard; esportazioni; audit trail; strumenti di amministrazione e monitoraggio.

## Fuori perimetro iniziale
- Invio automatico di comunicazioni commerciali senza approvazione.
- Raccolta di dati personali non necessari.
- Accesso o aggiramento di login, paywall, CAPTCHA o controlli.
- Conclusioni strategiche automatiche prive di evidenze e revisione.
- Condivisione dei dati tra tenant senza autorizzazione esplicita e tracciata.

## Definizione di completamento
Il prodotto è pronto quando un'organizzazione può creare uno spazio isolato, invitare utenti, configurare un progetto di ricerca, eseguire workflow, verificare le evidenze e produrre report senza poter leggere o modificare dati appartenenti ad altre organizzazioni.
