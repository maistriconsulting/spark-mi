import { FormEvent, useState } from "react";
import { api, Project, Role, Tenant } from "../api";
import { Badge, ErrorNote, PageHeader, slugify, useAction, useLoad } from "../ui";

// Mirrors PROJECT_WRITERS in the backend, which is what actually enforces it.
const PROJECT_WRITERS: Role[] = ["owner", "admin", "analyst"];

export default function Workspace({ token }: { token: string }) {
  const { data: tenants, error: loadError } = useLoad(() => api.tenants(token));
  const [active, setActive] = useState<{ tenant: Tenant; token: string } | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const { busy, error, run } = useAction();

  const open = (tenant: Tenant) => run(async () => {
    const scoped = (await api.selectTenant(token, tenant.id)).access_token;
    setProjects(await api.projects(scoped));
    setActive({ tenant, token: scoped });
  });

  function create(event: FormEvent) {
    event.preventDefault();
    if (!active) return;
    void run(async () => {
      const created = await api.createProject(active.token, { name, slug });
      setProjects(list => [created, ...list]); setName(""); setSlug("");
    });
  }

  if (!active) return (
    <>
      <PageHeader title="Progetti" subtitle="Scegli l'organizzazione su cui lavorare." />
      <ErrorNote text={loadError || error} />
      <div className="list">
        {tenants?.map(t => (
          <button key={t.id} type="button" className="list__button" onClick={() => open(t)} disabled={busy}>
            <span><strong>{t.name}</strong><small>{t.slug}</small></span><Badge tone="info">{t.role}</Badge>
          </button>
        ))}
        {tenants?.length === 0 && <p className="empty">Non fai parte di nessuna organizzazione attiva.</p>}
      </div>
    </>
  );

  const canCreate = PROJECT_WRITERS.includes(active.tenant.role);
  return (
    <>
      <PageHeader title={active.tenant.name} subtitle={`Progetti · il tuo ruolo: ${active.tenant.role}`}>
        <button type="button" className="btn--secondary" onClick={() => setActive(null)}>Cambia organizzazione</button>
      </PageHeader>
      <ErrorNote text={error} />
      {canCreate && (
        <form className="card form-row" onSubmit={create}>
          <label>Nome progetto<input value={name} onChange={e => { setName(e.target.value); setSlug(slugify(e.target.value)); }} required minLength={2} /></label>
          <label>Identificativo<input value={slug} onChange={e => setSlug(e.target.value)} pattern="[a-z0-9][a-z0-9\-]{1,98}[a-z0-9]" required /></label>
          <button disabled={busy}>Crea progetto</button>
        </form>
      )}
      <div className="list">
        {projects.map(p => (
          <article className="list__item" key={p.id}>
            <span><strong>{p.name}</strong><small>{p.slug}{p.description ? ` · ${p.description}` : ""}</small></span>
            <Badge tone="success">{p.status}</Badge>
          </article>
        ))}
        {projects.length === 0 && <p className="empty">Nessun progetto.</p>}
      </div>
    </>
  );
}
