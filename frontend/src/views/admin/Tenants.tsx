import { FormEvent, useState } from "react";
import { AdminTenant, AdminUser, PlatformApi } from "../../api";
import { Badge, ConfirmButton, ErrorNote, PageHeader, plural, slugify, useAction, useLoad } from "../../ui";
import { AddMember, MemberList } from "./Members";

export default function Tenants({ platform }: { platform: PlatformApi }) {
  const { data, error: loadError, reload } = useLoad(() => Promise.all([platform.tenants(), platform.users()]));
  const [openId, setOpenId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const { busy, error, clearError, run } = useAction();
  const [tenants, users] = data ?? [[] as AdminTenant[], [] as AdminUser[]];

  const mutate = (action: () => Promise<unknown>) => run(async () => { await action(); await reload(); });

  function create(event: FormEvent) {
    event.preventDefault();
    void mutate(async () => {
      const created = await platform.createTenant({ name, slug });
      setName(""); setSlug(""); setOpenId(created.id);
    });
  }

  return (
    <>
      <PageHeader title="Organizzazioni" subtitle={data ? `${plural(tenants.length, "organizzazione", "organizzazioni")} · ${plural(users.length, "utente", "utenti")}` : "Caricamento…"} />
      <ErrorNote text={loadError || (openId === null ? error : "")} />
      <form className="card form-row" onSubmit={create}>
        <label>Nuova organizzazione<input value={name} onChange={e => { setName(e.target.value); setSlug(slugify(e.target.value).slice(0, 80)); }} required minLength={2} maxLength={160} /></label>
        <label>Identificativo (non modificabile)<input value={slug} onChange={e => setSlug(e.target.value)} pattern="[a-z0-9][a-z0-9\-]{1,78}[a-z0-9]" required /></label>
        <button disabled={busy}>Crea organizzazione</button>
      </form>
      <div className="list">
        {tenants.map(tenant => {
          const open = openId === tenant.id;
          const memberships = users.flatMap(u => u.memberships.filter(m => m.tenant_id === tenant.id).map(m => ({ user: u, m })));
          const memberIds = new Set(memberships.map(x => x.user.id));
          return (
            <article className="record" key={tenant.id}>
              <div className="record__head">
                <span className="record__title"><strong>{tenant.name}</strong><small>{tenant.slug} · {plural(tenant.member_count, "membro attivo", "membri attivi")} · {tenant.owner_count} owner</small></span>
                <span className="actions">
                  {tenant.status === "active" ? <Badge tone="success">attiva</Badge> : <Badge tone="warning">sospesa</Badge>}
                  {tenant.owner_count === 0 && <Badge tone="warning">senza owner</Badge>}
                  <button type="button" className="btn--secondary" aria-expanded={open} onClick={() => { clearError(); setOpenId(open ? null : tenant.id); }}>{open ? "Chiudi" : "Gestisci"}</button>
                </span>
              </div>
              {open && (
                <div className="record__body">
                  <ErrorNote text={error} />
                  <Rename key={tenant.name} tenant={tenant} busy={busy} onSave={value => mutate(() => platform.updateTenant(tenant.id, { name: value }))} />
                  <h3>Membri</h3>
                  <MemberList busy={busy} empty="Nessun membro."
                    rows={memberships.map(({ user, m }) => ({ key: user.id, title: user.full_name, subtitle: user.email + (user.is_active ? "" : " · utente disattivato"), role: m.role, status: m.status }))}
                    onChange={(userId, role, status) => mutate(() => platform.setMembership(tenant.id, userId, role, status))} />
                  <AddMember label="Aggiungi un utente" busy={busy}
                    options={users.filter(u => u.is_active && !memberIds.has(u.id)).map(u => ({ id: u.id, label: `${u.full_name} (${u.email})` }))}
                    onAdd={(userId, role) => mutate(() => platform.setMembership(tenant.id, userId, role))} />
                  <h3>Stato</h3>
                  {tenant.status === "active"
                    ? <ConfirmButton label="Sospendi organizzazione" confirmLabel="Conferma: blocca l'accesso a tutti i membri" disabled={busy}
                        onConfirm={() => mutate(() => platform.updateTenant(tenant.id, { status: "suspended" }))} />
                    : <button type="button" disabled={busy} onClick={() => mutate(() => platform.updateTenant(tenant.id, { status: "active" }))}>Riattiva organizzazione</button>}
                </div>
              )}
            </article>
          );
        })}
        {data && tenants.length === 0 && <p className="empty">Nessuna organizzazione: crea la prima qui sopra.</p>}
      </div>
    </>
  );
}

function Rename({ tenant, busy, onSave }: { tenant: AdminTenant; busy: boolean; onSave: (name: string) => void }) {
  const [value, setValue] = useState(tenant.name);
  return (
    <form className="form-row" onSubmit={e => { e.preventDefault(); onSave(value); }}>
      <label>Nome<input value={value} onChange={e => setValue(e.target.value)} required minLength={2} maxLength={160} /></label>
      <button disabled={busy || value === tenant.name}>Salva nome</button>
    </form>
  );
}
