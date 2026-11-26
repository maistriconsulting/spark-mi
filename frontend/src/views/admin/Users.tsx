import { FormEvent, useState } from "react";
import { AdminTenant, AdminUser, PlatformApi, UserWithPassword } from "../../api";
import { Badge, ConfirmButton, ErrorNote, PageHeader, plural, TemporaryPassword, useAction, useLoad } from "../../ui";
import { AddMember, MemberList } from "./Members";

export default function Users({ platform }: { platform: PlatformApi }) {
  const { data, error: loadError, reload } = useLoad(() => Promise.all([platform.users(), platform.tenants()]));
  const [openId, setOpenId] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [secret, setSecret] = useState<UserWithPassword | null>(null);
  const [search, setSearch] = useState("");
  const { busy, error, clearError, run } = useAction();
  const [users, tenants] = data ?? [[] as AdminUser[], [] as AdminTenant[]];
  const query = search.trim().toLowerCase();
  const visible = users.filter(u => !query || `${u.full_name} ${u.email}`.toLowerCase().includes(query));

  const mutate = (action: () => Promise<unknown>) => run(async () => { await action(); await reload(); });

  function create(event: FormEvent) {
    event.preventDefault();
    void mutate(async () => {
      const created = await platform.createUser({ email, full_name: fullName });
      setSecret(created); setEmail(""); setFullName(""); setSearch(""); setOpenId(created.user.id);
    });
  }

  return (
    <>
      <PageHeader title="Utenti" subtitle={data ? plural(users.length, "utente", "utenti") : "Caricamento…"} />
      <ErrorNote text={loadError || (visible.some(u => u.id === openId) ? "" : error)} />
      {secret && <TemporaryPassword key={secret.temporary_password} email={secret.user.email} password={secret.temporary_password} onClose={() => setSecret(null)} />}
      <form className="card form-row" onSubmit={create}>
        <label>Nome e cognome<input value={fullName} onChange={e => setFullName(e.target.value)} required minLength={2} maxLength={160} autoComplete="off" /></label>
        <label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} required autoComplete="off" /></label>
        <button disabled={busy}>Crea utente</button>
      </form>
      <input className="search" type="search" placeholder="Cerca per nome o email" aria-label="Cerca utenti" value={search} onChange={e => setSearch(e.target.value)} />
      <div className="list">
        {visible.map(user => {
          const open = openId === user.id;
          const joined = new Set(user.memberships.map(m => m.tenant_id));
          const count = user.memberships.filter(m => m.status === "active").length;
          return (
            <article className="record" key={user.id}>
              <div className="record__head">
                <span className="record__title"><strong>{user.full_name}</strong><small>{user.email} · {plural(count, "organizzazione", "organizzazioni")}</small></span>
                <span className="actions">
                  {user.is_superadmin && <Badge tone="info">superadmin</Badge>}
                  {user.is_active ? <Badge tone="success">attivo</Badge> : <Badge tone="danger">disattivato</Badge>}
                  <button type="button" className="btn--secondary" aria-expanded={open} onClick={() => { clearError(); setOpenId(open ? null : user.id); }}>{open ? "Chiudi" : "Gestisci"}</button>
                </span>
              </div>
              {open && (
                <div className="record__body">
                  <ErrorNote text={error} />
                  <Rename key={user.full_name} user={user} busy={busy} onSave={value => mutate(() => platform.updateUser(user.id, { full_name: value }))} />
                  <h3>Organizzazioni e ruoli</h3>
                  <MemberList busy={busy} empty="Non fa parte di nessuna organizzazione."
                    rows={user.memberships.map(m => ({ key: m.tenant_id, title: m.tenant_name, role: m.role, status: m.status }))}
                    onChange={(tenantId, role, status) => mutate(() => platform.setMembership(tenantId, user.id, role, status))} />
                  {user.is_active && <AddMember label="Aggiungi a un'organizzazione" busy={busy}
                    options={tenants.filter(t => !joined.has(t.id)).map(t => ({ id: t.id, label: t.name }))}
                    onAdd={(tenantId, role) => mutate(() => platform.setMembership(tenantId, user.id, role))} />}
                  <h3>Accesso</h3>
                  {user.is_superadmin ? <p className="muted">Il superadmin non può essere disattivato; la password si cambia dal Profilo.</p> : (
                    <div className="actions">
                      <ConfirmButton label="Genera nuova password" confirmLabel="Conferma: la password attuale smette di funzionare" disabled={busy}
                        onConfirm={() => mutate(async () => setSecret(await platform.resetPassword(user.id)))} />
                      {user.is_active
                        ? <ConfirmButton label="Disattiva utente" confirmLabel="Conferma disattivazione" disabled={busy}
                            onConfirm={() => mutate(() => platform.updateUser(user.id, { is_active: false }))} />
                        : <button type="button" disabled={busy} onClick={() => mutate(() => platform.updateUser(user.id, { is_active: true }))}>Riattiva utente</button>}
                    </div>
                  )}
                </div>
              )}
            </article>
          );
        })}
        {data && visible.length === 0 && <p className="empty">Nessun utente trovato.</p>}
      </div>
    </>
  );
}

function Rename({ user, busy, onSave }: { user: AdminUser; busy: boolean; onSave: (name: string) => void }) {
  const [value, setValue] = useState(user.full_name);
  return (
    <form className="form-row" onSubmit={e => { e.preventDefault(); onSave(value); }}>
      <label>Nome e cognome<input value={value} onChange={e => setValue(e.target.value)} required minLength={2} maxLength={160} /></label>
      <button disabled={busy || value === user.full_name}>Salva nome</button>
    </form>
  );
}
