import { AuditEntry, PlatformApi } from "../../api";
import { ErrorNote, formatDate, PageHeader, useLoad } from "../../ui";

const ACTIONS: Record<string, string> = {
  "tenant.create": "Organizzazione creata",
  "tenant.update": "Organizzazione modificata",
  "user.create": "Utente creato",
  "user.update": "Utente modificato",
  "user.reset_password": "Password rigenerata",
  "user.change_password": "Password cambiata",
  "membership.set": "Ruolo o accesso modificato",
};

const LABELS: Record<string, string> = { name: "nome", slug: "identificativo", email: "utente", tenant: "organizzazione", role: "ruolo", status: "stato", full_name: "nome", is_active: "attivo" };

const VALUES: Record<string, string> = { active: "attivo", suspended: "sospeso", revoked: "revocato" };

const describe = (entry: AuditEntry) => Object.entries(entry.detail)
  .filter(([key]) => key !== "previous")
  .map(([key, value]) => `${LABELS[key] ?? key}: ${typeof value === "boolean" ? (value ? "sì" : "no") : key === "status" ? VALUES[String(value)] ?? String(value) : String(value)}`)
  .join(" · ");

export default function Audit({ platform }: { platform: PlatformApi }) {
  const { data, error } = useLoad(() => platform.audit());
  return (
    <>
      <PageHeader title="Registro attività" subtitle="Ultime 200 operazioni amministrative." />
      <ErrorNote text={error} />
      <div className="card table-wrap">
        <table>
          <thead><tr><th>Quando</th><th>Chi</th><th>Operazione</th><th>Dettaglio</th></tr></thead>
          <tbody>
            {data?.map(e => <tr key={e.id}><td>{formatDate(e.created_at)}</td><td>{e.actor_email ?? "—"}</td><td>{ACTIONS[e.action] ?? e.action}</td><td>{describe(e)}</td></tr>)}
          </tbody>
        </table>
        {data?.length === 0 && <p className="empty">Nessuna operazione registrata.</p>}
      </div>
    </>
  );
}
