const TOKEN_KEY = "prakriti_token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable: ignore */
  }
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = "GET", json, body } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload = body;
  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(json);
  }
  let res;
  try {
    res = await fetch(path, { method, headers, body: payload });
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running?", 0);
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* no JSON body */
  }
  if (!res.ok) {
    let msg = `Request failed (${res.status}).`;
    const d = data && data.detail;
    if (typeof d === "string") msg = d;
    else if (Array.isArray(d) && d.length) msg = d.map((x) => x.msg).join("; ");
    throw new ApiError(msg, res.status);
  }
  return data;
}

export const register = (email, password) =>
  request("/api/auth/register", { method: "POST", json: { email, password } });
export const login = (email, password) =>
  request("/api/auth/login", { method: "POST", json: { email, password } });
export const logout = () => request("/api/auth/logout", { method: "POST" });
export const me = () => request("/api/auth/me");

export function upload(file) {
  const form = new FormData();
  form.append("file", file);
  return request("/api/analyze/upload", { method: "POST", body: form });
}

export const listAnalyses = () => request("/api/analyses");
export const getAnalysis = (id) => request(`/api/analyses/${id}`);
export const deleteAnalysis = (id) => request(`/api/analyses/${id}`, { method: "DELETE" });