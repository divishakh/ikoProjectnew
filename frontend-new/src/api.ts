const TOKEN_KEY = "prakriti_token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable: ignore */
  }
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

type Options = { method?: string; json?: unknown; body?: FormData };

async function request<T>(path: string, { method = "GET", json, body }: Options = {}): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let payload: BodyInit | undefined = body;
  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(json);
  }

  let res: Response;
  try {
    res = await fetch(path, { method, headers, body: payload });
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running?", 0);
  }

  let data: unknown = null;
  try {
    data = await res.json();
  } catch {
    /* no JSON body */
  }

  if (!res.ok) {
    let msg = `Request failed (${res.status}).`;
    const detail = (data as { detail?: unknown } | null)?.detail;
    if (typeof detail === "string") msg = detail;
    else if (Array.isArray(detail) && detail.length) {
      msg = detail.map((d) => (d as { msg?: string }).msg ?? "Invalid input").join("; ");
    }
    throw new ApiError(msg, res.status);
  }
  return data as T;
}

export type AuthResponse = { access_token: string; token_type: string; email: string };
export type Me = { id: number; email: string };

export const register = (email: string, password: string) =>
  request<AuthResponse>("/api/auth/register", { method: "POST", json: { email, password } });

export const login = (email: string, password: string) =>
  request<AuthResponse>("/api/auth/login", { method: "POST", json: { email, password } });

export const logout = () => request<{ status: string }>("/api/auth/logout", { method: "POST" });

export const me = () => request<Me>("/api/auth/me");

export type Prediction = {
  mode: string;
  message?: string;
  classes?: string[];
  probabilities?: number[];
  label?: string;
  warning?: string;
  windows_used?: number;
};

export type AnalysisResult = {
  filename: string;
  saved: boolean;
  id?: number;
  recording: { channel: string; sampling_hz: number; duration_s: number; samples: number };
  filter: { type: string; order: number; low_hz: number; high_hz: number; zero_phase: boolean; method: string };
  quality: { beats_found: number; beats_kept: number; kept_fraction: number; ok: boolean; rule: string };
  signal: { t: number[]; raw: number[]; filtered: number[]; peaks_t: number[] };
  beat_intervals_s: number[];
  features?: Record<string, number>;
  median_beat?: { t: number[]; y: number[] };
  prediction: Prediction;
  ayurgenomics?: AyurProfile | null;
};

export const uploadRecording = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return request<AnalysisResult>("/api/analyze/upload", { method: "POST", body: form });
};

export type AyurItem = { text: string; kind: "study" | "classical" | "hypothesis" | "note"; sources: string[]; note?: string };
export type AyurSection = { id: string; title: string; items: AyurItem[] };
export type AyurProfile = {
  prakriti: string;
  available: string[];
  summary: string;
  sections: AyurSection[];
  tastes: { note: string; items: Record<string, { effect: "increases" | "pacifies" | "neutral" }> };
  concepts: { title: string; kind: string; text: string; sources: string[] }[];
  caveats: string[];
  sources: Record<string, { short: string; citation: string }>;
};

export const getAyurgenomics = (prakriti: string) =>
  request<AyurProfile>(`/api/ayurgenomics/${encodeURIComponent(prakriti)}`);
