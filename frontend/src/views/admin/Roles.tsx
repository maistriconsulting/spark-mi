import { PlatformApi } from "../../api";
import { Badge, ErrorNote, PageHeader, useLoad } from "../../ui";

const yesNo = (value: boolean) => <Badge tone={value ? "success" : "neutral"}>{value ? "sì" : "no"}</Badge>;

export default function Roles({ platform }: { platform: PlatformApi }) {
  const { data, error } = useLoad(() => platform.roles());
  return (
    <>
      <PageHeader title="Ruoli" subtitle="Ruoli fissi di un'organizzazione. Si assegnano da Organizzazioni o da Utenti." />
      <ErrorNote text={error} />
      <div className="card table-wrap">
        <table>
          <thead><tr><th>Ruolo</th><th>Responsabilità prevista</th><th>Vede i progetti</th><th>Crea progetti</th></tr></thead>
          <tbody>
            {data?.map(role => (
              <tr key={role.key}>
                <td><strong>{role.label}</strong></td><td>{role.purpose}</td>
                <td>{yesNo(role.can_read_projects)}</td><td>{yesNo(role.can_create_projects)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="notice notice--info">Le ultime due colonne indicano i permessi applicati oggi. Gli altri compiti saranno attivati insieme alle relative funzioni. La gestione di organizzazioni, utenti e ruoli è per ora riservata al superadmin, che non è un ruolo di organizzazione.</p>
    </>
  );
}
