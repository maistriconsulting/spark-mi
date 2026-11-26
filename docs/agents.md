# Agenti e responsabilità

## Master Orchestrator
Pianifica il lavoro, scompone gli obiettivi, assegna task, controlla dipendenze e copertura, governa budget e stop condition, avvia follow-up e sintetizza risultati validati. Opera sempre nel tenant e nel progetto autorizzati.

## A1 — Competitor Intelligence
Individua organizzazioni, fornitori, operatori e alternative rilevanti per il mercato selezionato. Classifica concorrenti diretti, indiretti/sostitutivi, fornitori tecnologici e partner, con motivazione documentata.

## A2 — Product & Service Intelligence
Crea schede di prodotti, servizi, modelli e configurazioni. Le caratteristiche sono adattate alla categoria di ricerca e devono mantenere unità, fonte e contesto.

## A3 — Pricing Intelligence
Raccoglie prezzi ufficiali, listini/rivenditori, offerte pubblicate e riferimenti secondari. Registra valuta, data, geografia, configurazione, IVA, inclusioni/esclusioni e condizioni. Se il prezzo non è pubblico: not_published o quote_required. Le stime sono separate e documentate. Mai inventare prezzi.

## A4 — Technology Intelligence
Analizza tecnologie, componenti, processi, software, brevetti e modalità di controllo pertinenti al perimetro della campagna. Distingue caratteristiche documentate da dichiarazioni e inferenze.

## A5 — Market Intelligence
Studia settori, geografia, domanda, driver, barriere, trend e dimensione del mercato quando supportata da fonti e metodologia.

## A6 — Customer Intelligence
Definisce profili cliente, bisogni, problemi, criteri d'acquisto, processi decisionali e trigger economici. Usa informazioni pubbliche o autorizzate.

## A7 — Business Model Intelligence
Confronta canali, modalità di vendita, partnership, licenze, abbonamenti, servizi, formule finanziarie e ricavi ricorrenti pertinenti al mercato.

## A8 — Strategic Intelligence
Confronta opzioni strategiche e modelli di posizionamento definiti nel progetto. Ogni giudizio è collegato a evidenze o marcato come ipotesi.

## A9 — Research Auditor
Verifica esistenza delle entità, associazioni, qualità e indipendenza delle fonti, freschezza, unità, configurazione e prezzo, duplicati, conflitti e claim non supportati. Può riaprire task e chiedere prove aggiuntive.

## Configurabilità
Gli agenti sono moduli riutilizzabili. Per ogni campagna l'orchestratore abilita gli agenti necessari, fornisce tassonomie e istruzioni contestuali e definisce output richiesti. Nessun agente deve incorporare nomi di clienti, mercati o settori specifici nel prompt di sistema.

## Collaborazione
Competitor crea candidati e passa approfondimenti a Product. Product richiede al Pricing confronti su configurazioni precise. Technology verifica claim tecnici. Market e Customer organizzano settori e bisogni. Business Model confronta le modalità commerciali. Strategic lavora su dataset con stato di validazione esplicito. Auditor controlla in modo indipendente.

## Regola anti-conferma circolare
La ripetizione dello stesso claim da parte di più agenti non è corroborazione. La verifica richiede fonti primarie o indipendenti e provenienza registrata.
