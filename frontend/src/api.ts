const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "https://sparkmi-api.bianconiglio.eu/api/v1";

let onSessionExpired: () => void = () => {};
export function setSessionExpiredHandler(handler: () => void) { onSessionExpired = handler; }

async function request<T>(path: string, token?: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  }).catch(() => { throw new Error("Impossibile raggiungere il server."); });
  if (!response.ok) {
    // A 401 on an authenticated call means the token expired or the user was deactivated.
    if (response.status === 401 && token) onSessionExpired();
    const body = await response.json().catch(() => ({}));
    // FastAPI returns a string for application errors and an array for validation errors.
    throw new Error(typeof body.detail === "string" ? body.detail
      : response.status === 422 ? "Controlla i dati inseriti." : `Richiesta non riuscita (${response.status})`);
  }
  return (response.status === 204 ? undefined : await response.json()) as T;
}

const send = (method: string, data?: unknown): RequestInit =>
  ({ method, body: data === undefined ? undefined : JSON.stringify(data) });

export type Role = "owner" | "admin" | "analyst" | "reviewer" | "viewer";
export type Tenant = { id: number; name: string; slug: string; role: Role };
export type Project = { id: number; name: string; slug: string; description: string | null; status: string; created_at: string };
export type Token = { access_token: string; is_superadmin: boolean };
export type Me = { id: number; email: string; full_name: string; is_superadmin: boolean };
export type BootstrapStatus = { initialized: boolean };

export type RoleInfo = { key: Role; label: string; purpose: string; can_read_projects: boolean; can_create_projects: boolean };
export type AdminTenant = { id: number; name: string; slug: string; status: "active" | "suspended"; created_at: string; member_count: number; owner_count: number };
export type UserMembership = { tenant_id: number; tenant_name: string; role: Role; status: "active" | "revoked" };
export type AdminUser = { id: number; email: string; full_name: string; is_active: boolean; is_superadmin: boolean; created_at: string; memberships: UserMembership[] };
export type UserWithPassword = { user: AdminUser; temporary_password: string };
export type AuditEntry = { id: number; created_at: string; actor_email: string | null; action: string; target_type: string; target_id: number; tenant_id: number | null; detail: Record<string, unknown> };

export const api = {
  bootstrapStatus: () => request<BootstrapStatus>("/auth/bootstrap-status"),
  login: (email: string, password: string) => request<Token>("/auth/login", undefined, send("POST", { email, password })),
  me: (token: string) => request<Me>("/auth/me", token),
  changePassword: (token: string, current_password: string, new_password: string) =>
    request<void>("/auth/change-password", token, send("POST", { current_password, new_password })),
  tenants: (token: string) => request<Tenant[]>("/auth/tenants", token),
  selectTenant: (token: string, tenant_id: number) => request<Token>("/auth/select-tenant", token, send("POST", { tenant_id })),
  projects: (token: string) => request<Project[]>("/projects", token),
  createProject: (token: string, data: { name: string; slug: string; description?: string }) =>
    request<Project>("/projects", token, send("POST", data)),
};

export const platformApi = (token: string) => ({
  roles: () => request<RoleInfo[]>("/platform/roles", token),
  tenants: () => request<AdminTenant[]>("/platform/tenants", token),
  createTenant: (data: { name: string; slug: string }) => request<AdminTenant>("/platform/tenants", token, send("POST", data)),
  updateTenant: (id: number, data: { name?: string; status?: AdminTenant["status"] }) =>
    request<AdminTenant>(`/platform/tenants/${id}`, token, send("PATCH", data)),
  users: () => request<AdminUser[]>("/platform/users", token),
  createUser: (data: { email: string; full_name: string }) => request<UserWithPassword>("/platform/users", token, send("POST", data)),
  updateUser: (id: number, data: { full_name?: string; is_active?: boolean }) =>
    request<AdminUser>(`/platform/users/${id}`, token, send("PATCH", data)),
  resetPassword: (id: number) => request<UserWithPassword>(`/platform/users/${id}/reset-password`, token, send("POST")),
  setMembership: (tenantId: number, userId: number, role: Role, status: UserMembership["status"] = "active") =>
    request<AdminUser>(`/platform/tenants/${tenantId}/members/${userId}`, token, send("PUT", { role, status })),
  audit: () => request<AuditEntry[]>("/platform/audit?limit=200", token),
});

export type PlatformApi = ReturnType<typeof platformApi>;
