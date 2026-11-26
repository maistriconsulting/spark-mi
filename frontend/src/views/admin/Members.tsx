import { FormEvent, useState } from "react";
import { Role, UserMembership } from "../../api";
import { Badge, ConfirmButton } from "../../ui";

export const ROLE_KEYS: Role[] = ["owner", "admin", "analyst", "reviewer", "viewer"];

export type MemberRow = { key: number; title: string; subtitle?: string; role: Role; status: UserMembership["status"] };
type Change = (key: number, role: Role, status: UserMembership["status"]) => void;

/** Memberships seen from either side: users of a tenant, or tenants of a user. */
export function MemberList({ rows, busy, onChange, empty }: { rows: MemberRow[]; busy: boolean; onChange: Change; empty: string }) {
  if (rows.length === 0) return <p className="muted">{empty}</p>;
  return (
    <ul className="members">
      {rows.map(row => (
        <li key={row.key}>
          <span className="members__who"><strong>{row.title}</strong>{row.subtitle && <small>{row.subtitle}</small>}</span>
          {row.status === "active" ? (
            <span className="actions">
              <select aria-label={`Ruolo di ${row.title}`} value={row.role} disabled={busy}
                onChange={e => onChange(row.key, e.target.value as Role, "active")}>
                {ROLE_KEYS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
              <ConfirmButton label="Revoca" confirmLabel="Conferma revoca" disabled={busy}
                onConfirm={() => onChange(row.key, row.role, "revoked")} />
            </span>
          ) : (
            <span className="actions">
              <Badge tone="danger">revocato · {row.role}</Badge>
              <button type="button" className="btn--secondary" disabled={busy}
                onClick={() => onChange(row.key, row.role, "active")}>Ripristina</button>
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}

export function AddMember({ label, options, busy, onAdd }:
  { label: string; options: { id: number; label: string }[]; busy: boolean; onAdd: (id: number, role: Role) => void }) {
  const [id, setId] = useState("");
  const [role, setRole] = useState<Role>("viewer");
  if (options.length === 0) return null;
  function submit(event: FormEvent) {
    event.preventDefault();
    if (!id) return;
    onAdd(Number(id), role); setId("");
  }
  return (
    <form className="form-row" onSubmit={submit}>
      <label>{label}
        <select value={id} onChange={e => setId(e.target.value)} required>
          <option value="">Seleziona…</option>
          {options.map(o => <option key={o.id} value={o.id}>{o.label}</option>)}
        </select>
      </label>
      <label>Ruolo
        <select value={role} onChange={e => setRole(e.target.value as Role)}>
          {ROLE_KEYS.map(r => <option key={r} value={r}>{r}</option>)}
        </select>
      </label>
      <button disabled={busy}>Aggiungi</button>
    </form>
  );
}
