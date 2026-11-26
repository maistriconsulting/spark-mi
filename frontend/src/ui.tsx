import { ReactNode, useCallback, useEffect, useState } from "react";

export const slugify = (value: string) =>
  value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export const plural = (count: number, one: string, many: string) => `${count} ${count === 1 ? one : many}`;

export const formatDate = (value: string) =>
  new Date(value).toLocaleString("it-IT", { dateStyle: "short", timeStyle: "short" });

const message = (error: unknown) => (error instanceof Error ? error.message : "Operazione non riuscita");

/** Runs one action at a time, exposing busy state and the last error. */
export function useAction() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const run = useCallback(async (action: () => Promise<unknown>) => {
    setBusy(true); setError("");
    try { await action(); return true; }
    catch (err) { setError(message(err)); return false; }
    finally { setBusy(false); }
  }, []);
  const clearError = useCallback(() => setError(""), []);
  return { busy, error, clearError, run };
}

export function useLoad<T>(loader: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  // The loader is read once per mount or explicit reload.
  const reload = useCallback(async () => {
    try { setData(await loader()); setError(""); }
    catch (err) { setError(message(err)); }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { void reload(); }, [reload]);
  return { data, error, reload };
}

export function ErrorNote({ text }: { text: string }) {
  return text ? <p className="notice notice--danger" role="alert">{text}</p> : null;
}

export function Badge({ tone = "neutral", children }: { tone?: "neutral" | "success" | "warning" | "danger" | "info"; children: ReactNode }) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}

export function PageHeader({ title, subtitle, children }: { title: string; subtitle?: string; children?: ReactNode }) {
  return (
    <header className="page-header">
      <div><h1>{title}</h1>{subtitle && <p className="muted">{subtitle}</p>}</div>
      {children}
    </header>
  );
}

/** Two-step button for actions that cut off access. Avoids blocking browser dialogs. */
export function ConfirmButton({ label, confirmLabel, onConfirm, disabled, className = "btn--secondary" }:
  { label: string; confirmLabel: string; onConfirm: () => void; disabled?: boolean; className?: string }) {
  const [armed, setArmed] = useState(false);
  if (!armed) return <button type="button" className={className} disabled={disabled} onClick={() => setArmed(true)}>{label}</button>;
  return (
    <span className="actions">
      <button type="button" className="btn--danger" disabled={disabled} onClick={() => { setArmed(false); onConfirm(); }}>{confirmLabel}</button>
      <button type="button" className="btn--secondary" onClick={() => setArmed(false)}>Annulla</button>
    </span>
  );
}

export function TemporaryPassword({ email, password, onClose }: { email: string; password: string; onClose: () => void }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="notice notice--warning" role="status">
      <p><strong>Password temporanea per {email}</strong></p>
      <p><code className="secret">{password}</code></p>
      <p>Viene mostrata solo ora. Consegnala con un canale riservato e chiedi di cambiarla al primo accesso.</p>
      <div className="actions">
        <button type="button" onClick={() => navigator.clipboard.writeText(password).then(() => setCopied(true))}>{copied ? "Copiata" : "Copia"}</button>
        <button type="button" className="btn--secondary" onClick={onClose}>Chiudi</button>
      </div>
    </div>
  );
}
