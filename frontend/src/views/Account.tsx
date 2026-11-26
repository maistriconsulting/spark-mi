import { FormEvent, useState } from "react";
import { api, Me } from "../api";
import { ErrorNote, PageHeader, useAction } from "../ui";

export default function Account({ token, me }: { token: string; me: Me }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [done, setDone] = useState(false);
  const [mismatch, setMismatch] = useState("");
  const { busy, error, run } = useAction();

  function submit(event: FormEvent) {
    event.preventDefault(); setDone(false);
    if (next !== confirm) return setMismatch("Le nuove password non coincidono.");
    setMismatch("");
    void run(async () => {
      await api.changePassword(token, current, next);
      setCurrent(""); setNext(""); setConfirm(""); setDone(true);
    });
  }

  return (
    <>
      <PageHeader title="Profilo" subtitle={`${me.full_name} · ${me.email}`} />
      <section className="card card--narrow">
        <h2>Cambia password</h2>
        <form onSubmit={submit}>
          <label>Password attuale<input type="password" autoComplete="current-password" value={current} onChange={e => setCurrent(e.target.value)} required /></label>
          <label>Nuova password (minimo 12 caratteri)<input type="password" autoComplete="new-password" value={next} onChange={e => setNext(e.target.value)} required minLength={12} maxLength={128} /></label>
          <label>Ripeti la nuova password<input type="password" autoComplete="new-password" value={confirm} onChange={e => setConfirm(e.target.value)} required /></label>
          <ErrorNote text={mismatch || error} />
          {done && <p className="notice notice--success">Password aggiornata.</p>}
          <button disabled={busy}>{busy ? "Salvataggio..." : "Aggiorna password"}</button>
        </form>
      </section>
    </>
  );
}
