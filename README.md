# SPARK Market Intelligence

**SPARK-MI** è una piattaforma modulare di Market Intelligence basata su agenti AI coordinati. È progettata per essere utilizzata da più aziende, su mercati, settori, aree geografiche e categorie di prodotto differenti.

Ogni azienda lavora in uno spazio isolato (tenant) con utenti, progetti, campagne, fonti, dati, agenti, budget e report propri. Il motore applicativo, gli strumenti e le tassonomie comuni possono essere condivisi senza esporre i dati riservati tra aziende.

## Obiettivi
- Gestire più aziende e più utenti con ruoli e permessi.
- Creare progetti e campagne di ricerca indipendenti per qualsiasi mercato.
- Coordinare agenti specialistici attraverso workflow configurabili.
- Conservare fonti, evidenze, claim, verifiche e storico.
- Confrontare aziende, prodotti, tecnologie, prezzi, clienti e modelli commerciali.
- Produrre report ed esportazioni tracciabili.
- Controllare costi, qualità, sicurezza e accesso ai dati.

## Documentazione
- [Project charter](docs/project-charter.md)
- [Architettura tecnica](docs/architecture.md)
- [Agenti e responsabilità](docs/agents.md)
- [Modello dati](docs/data-model.md)
- [Isolamento multi-tenant](docs/tenancy.md)
- [Piano di ricerca](docs/research-plan.md)
- [Roadmap](docs/roadmap.md)
- [Governance e qualità](docs/governance.md)

## Principi
1. Ogni informazione rilevante deve avere fonte e data di rilevazione.
2. Prezzi osservati, quotazioni e stime devono essere distinti.
3. Dati mancanti non vanno inventati.
4. Separare fatti, dichiarazioni, inferenze e ipotesi.
5. I dati di un tenant non sono accessibili agli altri tenant.
6. Le decisioni strategiche restano soggette a validazione umana.
7. Le configurazioni specifiche di un mercato non devono diventare vincoli del prodotto.

> Stato: repository in fase di definizione tecnica. Target e stime nei documenti sono criteri di pianificazione, non risultati di ricerca già ottenuti.
