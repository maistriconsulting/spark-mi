import { FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import { ErrorNote, useAction } from "../ui";

export default function Login({ notice, onToken }: { notice: string; onToken: (token: string) => Promise<void> }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [initialized, setInitialized] = useState(true);
  const { busy, error, run } = useAction();

  useEffect(() => {
    // Informational only: the login form must stay usable if this check fails.
    api.bootstrapStatus().then(status => setInitialized(status.initialized)).catch(() => undefined);
  }, []);

  function submit(event: FormEvent) {
    event.preventDefault();
    void run(async () => {
      const result = await api.login(email, password).catch((err: Error) => {
        throw err.message === "Email or password incorrect" ? new Error("Email o password non corretti.") : err;
      });
      await onToken(result.access_token);
    });
  }

  return (
    <main className="auth">
      <section className="auth__card">
        <div className="auth__brand">
          <img src="/brand/logo.svg" alt="SPARK" width="148" height="55" />
          <span>Market Intelligence</span>
        </div>
        <div className="auth__body">
          <h1>Accedi</h1>
          {notice && <p className="notice notice--warning">{notice}</p>}
          <form onSubmit={submit}>
            <label>Email<input type="email" autoComplete="username" value={email} onChange={e => setEmail(e.target.value)} required /></label>
            <label>Password<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
            <ErrorNote text={error} />
            <button className="btn--block" disabled={busy}>{busy ? "Accesso..." : "Accedi"}</button>
          </form>
          {!initialized && <p className="footnote">Piattaforma non ancora attivata: il primo account si crea dal server.</p>}
          <p className="footnote">Accesso riservato agli utenti autorizzati.</p>
        </div>
      </section>
    </main>
  );
}
