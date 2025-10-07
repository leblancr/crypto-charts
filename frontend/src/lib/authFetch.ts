const API_BASE = "http://127.0.0.1:8000";

/**
 * Authenticated fetch that attaches the stored JWT token.
 */
export function authFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem("token");
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": token ? `Bearer ${token}` : "",
      "Content-Type": "application/json",
    },
  });
}
