import { useEffect, useMemo, useState } from "react";
import { api, Me, platformApi, setSessionExpiredHandler } from "./api";
import Login from "./views/Login";
import Account from "./views/Account";
import Workspace from "./views/Workspace";
import Tenants from "./views/admin/Tenants";
import Users from "./views/admin/Users";
import Roles from "./views/admin/Roles";
import Audit from "./views/admin/Audit";

type Session = { token: string; me: Me };
type View = "tenants" | "users" | "roles" | "audit" | "workspace" | "account";

const ADMIN_NAV: [View, string][] = [["tenants", "Organizzazioni"], ["users", "Utenti"], ["roles", "Ruoli"], ["audit", "Registro"]];
const COMMON_NAV: [View, string][] = [["workspace", "Progetti"], ["account", "Profilo"]];

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [view, setView] = useState<View>("workspace");
  const [notice, setNotice] = useState("");
  const platform = useMemo(() => (session ? platformApi(session.token) : null), [session]);

  useEffect(() => {
    setSessionExpiredHandler(() => { setSession(null); setNotice("Sessione scaduta: accedi di nuovo."); });
  }, []);

  async function start(token: string) {
    const me = await api.me(token);
    setNotice(""); setView(me.is_superadmin ? "tenants" : "workspace"); setSession({ token, me });
  }

  if (!session || !platform) return <Login notice={notice} onToken={start} />;

  const nav = session.me.is_superadmin ? [...ADMIN_NAV, ...COMMON_NAV] : COMMON_NAV;
  const logout = () => { setNotice(""); setSession(null); };

  return (
    <div className="app">
      <header className="topbar">
        <img src="/brand/logo.svg" alt="SPARK" width="108" height="40" />
        <span className="topbar__product">Market Intelligence</span>
        <span className="topbar__user">{session.me.email}</span>
        <button type="button" className="btn--on-dark" onClick={logout}>Esci</button>
      </header>
      <nav className="sidebar" aria-label="Principale">
        {nav.map(([key, label]) => (
          <button key={key} type="button" className={`nav-item${view === key ? " is-active" : ""}`}
            aria-current={view === key ? "page" : undefined} onClick={() => setView(key)}>{label}</button>
        ))}
      </nav>
      <main className="main">
        {view === "tenants" && <Tenants platform={platform} />}
        {view === "users" && <Users platform={platform} />}
        {view === "roles" && <Roles platform={platform} />}
        {view === "audit" && <Audit platform={platform} />}
        {view === "workspace" && <Workspace token={session.token} />}
        {view === "account" && <Account token={session.token} me={session.me} />}
      </main>
    </div>
  );
}
