# Modello dati

## Principi
Separare entità, osservazioni, claim ed evidenze. Una società può avere più prodotti; un prodotto più configurazioni; una configurazione più osservazioni di prezzo nel tempo. I dati mancanti restano esplicitamente mancanti.

## Tabelle principali
| Tabella | Scopo |
|---|---|
| projects | Progetti di intelligence |
| campaigns | Campagne e perimetro |
| research_tasks | Task assegnati |
| agent_runs | Esecuzioni, modello, prompt e costo |
| companies | Anagrafica aziende |
| company_sites | Sedi, domini e presenza geografica |
| products | Prodotti e modelli |
| product_configurations | Configurazioni tecniche/commerciali |
| product_features | Caratteristiche e unità |
| technologies | Tecnologie e modalità di controllo |
| applications | Applicazioni |
| industries | Settori |
| company_products | Ruolo azienda-prodotto |
| business_models | Modelli commerciali |
| price_observations | Prezzi/quotazioni osservati |
| sources | Pagine e documenti |
| evidence | Evidenze collegate ai claim |
| claims | Affermazioni atomiche |
| validations | Audit e approvazioni |
| change_log | Storico modifiche |

## Company — campi minimi
id, canonical_name, legal_name, website, country_code, headquarters, company_type, market_role, markets_served, description, first_seen_at, last_verified_at, record_status. Separare il ruolo aziendale dalla classificazione competitiva, che deve avere motivazione e prodotto/use case di riferimento.

## Product — campi minimi
id, company_id, product_name, model, application_type, robot_type, payload_value/unit, reach_value/unit, cycles_value/unit, cycle_conditions, pallet_types, product_types, mixed_sku_support, vision_system, control_method, ai_claim_level, integration_interfaces, safety_description, availability_status. Ogni prestazione va associata a una fonte e alle condizioni operative.

## Price observation — campi minimi
id, company_id, product_id, configuration_id, amount, currency, vat_status, price_type, scope_description, included_items, excluded_items, installation_included, commissioning_included, training_included, service_terms, market_country, observed_at, valid_from, valid_until, source_id, confidence, notes.

price_type: official_list, reseller_listing, published_quote, secondary_report, modeled_estimate, quote_required, not_published. Le stime devono includere intervallo, metodo, assunzioni e riferimenti. Non presentarle come prezzi osservati.

## Sources ed evidence
Source: URL canonico, titolo, publisher, source_type, data pubblicazione se disponibile, data acquisizione, lingua, paese, checksum, access_status e snapshot_uri.
Evidence: source_id, claim_id, estratto breve o riferimento sezione, pagina/posizione, acquired_at, extraction_method, support_type (supports, contradicts, contextualizes).

Rispettare copyright e condizioni d'uso; conservare metadati e riferimenti, evitando copie non necessarie.

## Claims e stati
Claim: soggetto, predicato, valore, unità, contesto, valid_from/to, confidence, verification_status e note.
Stati: unverified, supported_primary, corroborated_independent, secondary_only, conflicting, rejected, human_approved.

## Normalizzazione
Unità SI dove possibile mantenendo il valore originale; valute ISO 4217; paesi ISO 3166-1; nomi normalizzati senza perdere ragione sociale; URL canonicalizzati; timestamp UTC con timezone originale quando utile; tassonomie versionate.

## Esportazioni
CSV/XLSX con ID stabili e URL fonte. Report PDF che distinguono dati osservati, dichiarazioni del fornitore, stime e ipotesi.