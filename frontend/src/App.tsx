import { FormEvent, useEffect, useState } from "react";
import { api, PlatformOverview, Project, Tenant } from "./api";

type Session = { userToken: string; tenantToken?: string; tenant?: Tenant; isSuperadmin?: boolean };

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectSlug, setProjectSlug] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [initialized, setInitialized] = useState<boolean | null>(null);
  const [bootstrapPassword, setBootstrapPassword] = useState("");
  const [bootstrapConfirmation, setBootstrapConfirmation] = useState("");
  const [platform, setPlatform] = useState<PlatformOverview | null>(null);

  useEffect(() => {
    api.bootstrapStatus().then(status => setInitialized(status.initialized)).catch(() => setError("Impossibile verificare lo stato della piattaforma."));
  }, []);

  async function loadTenants(userToken: string) {
    const available = await api.tenants(userToken);
    setTenants(available);
    setSession({ userToken });
  }

  async function handleLogin(event: FormEvent) {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      const result = await api.login(email, password);
      if (result.is_superadmin) {
        setSession({ userToken: result.access_token, isSuperadmin: true });
        setPlatform(await api.platformOverview(result.access_token));
      } else await loadTenants(result.access_token);
    } catch (err) { setError(err instanceof Error ? err.message : "Accesso non riuscito"); }
    finally { setBusy(false); }
  }

  async function handleBootstrap(event: FormEvent) {
    event.preventDefault(); setError("");
    if (bootstrapPassword.length < 12) return setError("La password deve contenere almeno 12 caratteri.");
    if (bootstrapPassword !== bootstrapConfirmation) return setError("Le password non coincidono.");
    setBusy(true);
    try {
      const result = await api.bootstrap(bootstrapPassword);
      setSession({ userToken: result.access_token, isSuperadmin: true });
      setPlatform(await api.platformOverview(result.access_token));
      setInitialized(true); setBootstrapPassword(""); setBootstrapConfirmation("");
    } catch (err) { setError(err instanceof Error ? err.message : "Configurazione iniziale non riuscita"); }
    finally { setBusy(false); }
  }

  async function chooseTenant(tenant: Tenant) {
    if (!session) return;
    setError(""); setBusy(true);
    try {
      const result = await api.selectTenant(session.userToken, tenant.id);
      setSession({ userToken: session.userToken, tenantToken: result.access_token, tenant });
      setProjects(await api.projects(result.access_token));
    } catch (err) { setError(err instanceof Error ? err.message : "Impossibile aprire l'organizzazione"); }
    finally { setBusy(false); }
  }

  async function addProject(event: FormEvent) {
    event.preventDefault();
    if (!session?.tenantToken) return;
    setError(""); setBusy(true);
    try {
      const created = await api.createProject(session.tenantToken, {
        name: projectName, slug: projectSlug,
      });
      setProjects([created, ...projects]); setProjectName(""); setProjectSlug("");
    } catch (err) { setError(err instanceof Error ? err.message : "Creazione progetto non riuscita"); }
    finally { setBusy(false); }
  }

  function logout() {
    setSession(null); setTenants([]); setProjects([]); setPassword(""); setError("");
  }

  if (initialized === false && !session) return (
    <main className="auth-shell"><section className="login-card">
      <div className="brand-mark">S</div><p className="eyebrow">CONFIGURAZIONE INIZIALE</p><h1>Attiva SPARK-MI</h1>
      <p className="muted">Crea il primo account amministratore della piattaforma.</p>
      <form onSubmit={handleBootstrap} className="form-stack">
        <label>Email<input type="email" value="info@maistriconsulting.com" disabled /></label>
        <label>Password<input type="password" autoComplete="new-password" value={bootstrapPassword} onChange={e => setBootstrapPassword(e.target.value)} required minLength={12} /></label>
        <label>Conferma password<input type="password" autoComplete="new-password" value={bootstrapConfirmation} onChange={e => setBootstrapConfirmation(e.target.value)} required minLength={12} /></label>
        {error && <p className="error">{error}</p>}<button disabled={busy}>{busy ? "Configurazione..." : "Crea superadmin"}</button>
      </form>
    </section></main>
  );

  if (initialized === null && !session) return <main className="auth-shell"><p className="muted">Verifica configurazione…</p></main>;

  if (!session) return (
    <main className="auth-shell">
      <section className="login-card">
        <div className="brand-mark">S</div>
        <p className="eyebrow">MARKET INTELLIGENCE PLATFORM</p>
        <h1>SPARK-MI</h1>
        <p className="muted">Accedi al tuo spazio di lavoro.</p>
        <form onSubmit={handleLogin} className="form-stack">
          <label>Email<input type="email" autoComplete="username" value={email} onChange={e => setEmail(e.target.value)} required /></label>
          <label>Password<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
          {error && <p className="error">{error}</p>}
          <button disabled={busy}>{busy ? "Accesso..." : "Accedi"}</button>
        </form>
        <p className="footnote">Accesso riservato agli utenti invitati.</p>
      </section>
    </main>
  );

  if (session.isSuperadmin) return (
    <div className="app-shell"><aside className="sidebar"><div className="sidebar-brand"><span className="brand-small">S</span><strong>SPARK-MI</strong></div><div className="workspace-label">PIATTAFORMA</div><div className="workspace-name">Superadmin</div><div className="sidebar-bottom"><span>superadmin globale</span><button onClick={logout}>Esci</button></div></aside>
      <main className="main-content"><header className="topbar"><div><span className="eyebrow">AMMINISTRAZIONE PIATTAFORMA</span><h2>Panoramica globale</h2></div></header>
        <section className="welcome"><div><p className="eyebrow">SPARK-MI</p><h1>Superadmin attivo.</h1><p>Le organizzazioni restano isolate: l’accesso ai loro dati richiede funzioni globali esplicite e tracciate.</p></div></section>
        <section className="project-layout"><div className="create-card"><h3>Organizzazioni</h3><p className="muted">{platform?.tenant_count ?? 0} organizzazioni · {platform?.user_count ?? 0} utenti.</p>{platform?.tenants.map(t => <p key={t.id}>{t.name} <small>({t.slug})</small></p>)}</div></section>
      </main></div>
  );

  if (!session.tenantToken) return (
    <main className="auth-shell">
      <section className="login-card wide">
        <p className="eyebrow">SPAZIO DI LAVORO</p>
        <h1>Seleziona organizzazione</h1>
        <p className="muted">Scegli l'organizzazione su cui lavorare.</p>
        <div className="tenant-list">
          {tenants.map(tenant => <button className="tenant-option" key={tenant.id} onClick={() => chooseTenant(tenant)} disabled={busy}>
            <span><strong>{tenant.name}</strong><small>{tenant.slug} · {tenant.role}</small></span><b>›</b>
          </button>)}
        </div>
        {tenants.length === 0 && <p className="muted">Nessuna organizzazione associata a questo utente.</p>}
        {error && <p className="error">{error}</p>}
        <button className="button-secondary" onClick={logout}>Esci</button>
      </section>
    </main>
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand"><span className="brand-small">S</span><strong>SPARK-MI</strong></div>
        <div className="workspace-label">ORGANIZZAZIONE</div>
        <div className="workspace-name">{session.tenant?.name}</div>
        <nav><a className="nav-active">Panoramica</a><a>Progetti</a><a>Campagne</a><a>Fonti ed evidenze</a><a>Impostazioni</a></nav>
        <div className="sidebar-bottom"><span>{session.tenant?.role}</span><button onClick={logout}>Esci</button></div>
      </aside>
      <main className="main-content">
        <header className="topbar"><div><span className="eyebrow">WORKSPACE</span><h2>Panoramica</h2></div><span className="status-pill">Ambiente iniziale</span></header>
        <section className="welcome"><div><p className="eyebrow">MARKET INTELLIGENCE</p><h1>Le decisioni partono dalle informazioni giuste.</h1><p>Organizza le attività di ricerca, raccogli evidenze e costruisci analisi verificabili.</p></div></section>
        {error && <p className="error">{error}</p>}
        <section className="section-heading"><div><h3>Progetti</h3><p className="muted">I progetti di questa organizzazione.</p></div><span className="count">{projects.length}</span></section>
        <section className="project-layout">
          <div className="project-list">
            {projects.map(project => <article className="project-card" key={project.id}><div className="project-icon">P</div><div><strong>{project.name}</strong><p>{project.description || "Nessuna descrizione"}</p><small>{project.slug} · {project.status}</small></div></article>)}
            {projects.length === 0 && <div className="empty-state"><strong>Nessun progetto ancora</strong><p>Crea il primo progetto per iniziare a organizzare le ricerche.</p></div>}
          </div>
          <form className="create-card form-stack" onSubmit={addProject}>
            <h3>Nuovo progetto</h3>
            <label>Nome progetto<input value={projectName} onChange={e => { setProjectName(e.target.value); setProjectSlug(e.target.value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")); }} required minLength={2} /></label>
            <label>Identificativo<input value={projectSlug} onChange={e => setProjectSlug(e.target.value)} pattern="[a-z0-9][a-z0-9-]{1,98}[a-z0-9]" required /></label>
            <button disabled={busy}>{busy ? "Salvataggio..." : "Crea progetto"}</button>
          </form>
        </section>
      </main>
    </div>
  );
}
