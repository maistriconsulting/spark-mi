"""Fixed organization roles (docs/tenancy.md). Superadmin is not one of them."""
from typing import Literal

Role = Literal["owner", "admin", "analyst", "reviewer", "viewer"]

# What the API enforces today. Update together with the routes that check these sets.
PROJECT_WRITERS = frozenset({"owner", "admin", "analyst"})

ROLES: list[dict] = [
    {"key": "owner", "label": "Owner", "purpose": "Gestione completa dell'organizzazione e dei membri."},
    {"key": "admin", "label": "Admin", "purpose": "Gestione di utenti, progetti, campagne e configurazioni."},
    {"key": "analyst", "label": "Analyst", "purpose": "Creazione ed esecuzione delle ricerche."},
    {"key": "reviewer", "label": "Reviewer", "purpose": "Revisione, validazione e approvazione."},
    {"key": "viewer", "label": "Viewer", "purpose": "Sola consultazione."},
]
