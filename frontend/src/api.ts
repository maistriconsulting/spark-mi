const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "https://sparkmi-api.bianconiglio.eu/api/v1";

async function request<T>(path: string, token?: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    // FastAPI returns a string for application errors and an array for validation errors.
    throw new Error(typeof body.detail === "string" ? body.detail : `Richiesta non riuscita (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export type Tenant = { id: number; name: string; slug: string; role: string };
export type Project = { id: number; name: string; slug: string; description: string | null; status: string; created_at: string };
export type Token = { access_token: string; is_superadmin: boolean };
export type BootstrapStatus = { initialized: boolean };
export type PlatformOverview = { user_count: number; tenant_count: number; tenants: Tenant[] };

export const api = {
  bootstrapStatus: () => request<BootstrapStatus>("/auth/bootstrap-status"),
  login: (email: string, password: string) =>
    request<Token>("/auth/login", undefined, { method: "POST", body: JSON.stringify({ email, password }) }),
  tenants: (token: string) => request<Tenant[]>("/auth/tenants", token),
  selectTenant: (token: string, tenant_id: number) =>
    request<{ access_token: string }>("/auth/select-tenant", token, { method: "POST", body: JSON.stringify({ tenant_id }) }),
  projects: (token: string) => request<Project[]>("/projects", token),
  createProject: (token: string, data: { name: string; slug: string; description?: string }) =>
    request<Project>("/projects", token, { method: "POST", body: JSON.stringify(data) }),
  platformOverview: (token: string) => request<PlatformOverview>("/auth/platform/overview", token),
};
