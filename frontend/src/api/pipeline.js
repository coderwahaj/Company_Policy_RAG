const API_BASE = import.meta.env.VITE_API_BASE_URL;

async function parseResponse(res) {
  const text = await res.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { message: text };
  }

  if (!res.ok) {
    throw new Error(data?.detail || data?.message || `Request failed: ${res.status}`);
  }
  return data;
}

export async function loadPipeline(provider = "groq") {
  const res = await fetch(`${API_BASE}/pipeline/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider }),
  });
  return parseResponse(res);
}

export async function resetPipeline(provider = "groq") {
  const res = await fetch(`${API_BASE}/pipeline/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider }),
  });
  return parseResponse(res);
}

export async function getPipelineStatus(provider = "groq") {
  const res = await fetch(`${API_BASE}/pipeline/status?provider=${encodeURIComponent(provider)}`);
  return parseResponse(res);
}