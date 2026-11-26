# Modello dati

## Principi
Il modello separa organizzazioni, utenti, progetti, campagne, entità analizzate, osservazioni, claim ed evidenze. I dati operativi e di ricerca appartengono a un tenant. Le tassonomie comuni possono essere globali; ogni personalizzazione deve dichiarare il proprio ambito.

## Entità multi-tenant
| Tabella | Scopo | Ambito |
|---|---|---|
| tenants | Organizzazioni clienti | Globale |
| users | Identità utenti | Globale |
| tenant_memberships | Appartenenza, ruolo e stato utente-organizzazione | Tenant |
| invitations | Inviti a entrare in un'organizzazione | Tenant |
| projects | Progetti di intelligence | Tenant |
| campaigns | Campagne e perimetro | Tenant |
| research_tasks | Task assegnati | Tenant |
| agent_runs | Esecuzioni, modello, prompt e costo | Tenant |
| companies | Anagrafiche aziende analizzate | Tenant |
| company_sites | Sedi, domini e presenza geografica | Tenant |
| products | Prodotti e modelli | Tenant |
| product_configurations | Configurazioni tecniche/commerciali | Tenant |
| product_features | Caratteristiche e unità | Tenant |
| technologies | Tecnologie e modalità di controllo | Tenant |
| applications | Applicazioni | Tenant |
| industries | Settori | Tenant |
| company_products | Relazioni azienda-prodotto | Tenant |
| business_models | Modelli commerciali | Tenant |
| price_observations | Prezzi/quotazioni osservati | Tenant |
| sources | Pagine e documenti | Tenant |
| evidence | Evidenze collegate ai claim | Tenant |
| claims | Affermazioni atomiche | Tenant |
| validations | Audit e approvazioni | Tenant |
| change_log | Storico modifiche | Tenant |

## Regole di ownership
- Ogni tabella tenant-owned contiene tenant_id NOT NULL.
- Ogni relazione tra record tenant-owned verifica che i record appartengano allo stesso tenant.
- Gli identificativi pubblici non sostituiscono mai il controllo di ownership.
- Le chiavi uniche applicative includono tenant_id quando l'unicità è limitata all'organizzazione.
- Le query e le operazioni di scrittura passano da repository/service che applicano tenant scope.
- I job asincroni, gli eventi, le cache, i file e gli export conservano il tenant context.
- Le tassonomie globali sono in sola lettura per i tenant; eventuali estensioni sono tenant-scoped.

## Tenant e membership
tenants: id, slug, display_name, legal_name, status, plan_code, created_at, updated_at.
users: id, email_normalized, password_hash o external_identity, display_name, status, created_at.
tenant_memberships: id, tenant_id, user_id, role, status, invited_by, created_at.
Ruoli iniziali: owner, admin, analyst, reviewer, viewer. I permessi effettivi devono essere verificati lato server.

## Project e campaign
projects: id, tenant_id, name, description, owner_user_id, status, created_at, updated_at.
campaigns: id, tenant_id, project_id, name, objectives, geography, languages, industries, categories, scope_config, source_policy, budget_config, status, created_at.
Il perimetro è configurabile e versionato; non contiene valori obbligatori riferiti a uno specifico settore o paese.

## Entità di ricerca
Le entità companies, products, configurations, technologies, applications, industries e business_models hanno tenant_id e campi descrittivi normalizzati. Il modello deve consentire di aggiungere nuove categorie senza migrazioni specifiche per ogni mercato. Le tassonomie condivise usano tabelle di riferimento separate.

## Price observation
id, tenant_id, company_id, product_id, configuration_id, amount, currency, vat_status, price_type, scope_description, included_items, excluded_items, installation_included, commissioning_included, training_included, service_terms, market_country, observed_at, valid_from, valid_until, source_id, confidence, notes.

price_type: official_list, reseller_listing, published_quote, secondary_report, modeled_estimate, quote_required, not_published. Le stime includono intervallo, metodo e assunzioni; non sono presentate come prezzi osservati.

## Sources ed evidence
Source: id, tenant_id, canonical_url, title, publisher, source_type, publication_date, acquired_at, language, country, checksum, access_status, snapshot_uri.
Evidence: id, tenant_id, source_id, claim_id, excerpt_or_locator, page_or_position, acquired_at, extraction_method, support_type (supports, contradicts, contextualizes).

Le fonti pubbliche possono essere acquisite separatamente da ciascun tenant. Un eventuale archivio globale condiviso richiede policy esplicite, provenienza, diritti di utilizzo e separazione tra metadati condivisibili e note private.

## Claims e stati
Claim: id, tenant_id, subject, predicate, value, unit, context, valid_from, valid_to, confidence, verification_status.
Stati: unverified, supported_primary, corroborated_independent, secondary_only, conflicting, rejected, human_approved.

## Prezzi, normalizzazione ed esportazioni
Unità SI dove possibile mantenendo il valore originale; valute ISO 4217; paesi ISO 3166-1; timestamp UTC con timezone originale quando utile; tassonomie versionate. CSV/XLSX includono ID stabili e URL fonte. Report distinguono dati osservati, dichiarazioni, stime e ipotesi.

## Indici e integrità
Prevedere indici composti che iniziano da tenant_id per le tabelle tenant-owned e foreign key composite dove necessario per impedire relazioni cross-tenant. Verificare i vincoli reali in MariaDB e nelle migrazioni Alembic.
