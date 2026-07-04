/**
 * api/search.js — Vercel Serverless Function
 * Proxy para a API do ML com token de usuário (authorization_code).
 * Token pessoal bypassa o bloqueio de IP de datacenter.
 */

let cachedToken = null;
let tokenExpiry = 0;

async function refreshToken() {
  const refreshToken = process.env.ML_REFRESH_TOKEN;
  if (!refreshToken) throw new Error('ML_REFRESH_TOKEN não configurado. Acesse /autorizar para autenticar.');

  const res = await fetch('https://api.mercadolibre.com/oauth/token', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type:    'refresh_token',
      client_id:     process.env.ML_APP_ID,
      client_secret: process.env.ML_CLIENT_SECRET,
      refresh_token: refreshToken,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Falha ao renovar token: ${res.status} — ${err}`);
  }

  const data = await res.json();
  cachedToken = data.access_token;
  tokenExpiry = Date.now() + (data.expires_in * 1000);

  // Atualizar refresh token no Vercel se mudou
  if (data.refresh_token && data.refresh_token !== refreshToken) {
    const vercelToken = process.env.VERCEL_TOKEN;
    const projectId   = process.env.VERCEL_PROJECT_ID;
    if (vercelToken && projectId) {
      await fetch(`https://api.vercel.com/v10/projects/${projectId}/env`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${vercelToken}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'ML_REFRESH_TOKEN', value: data.refresh_token, type: 'encrypted', target: ['production','preview'] }),
      });
    }
  }

  return cachedToken;
}

async function getToken() {
  // Usar access token do env se válido
  if (process.env.ML_ACCESS_TOKEN && !cachedToken) {
    cachedToken = process.env.ML_ACCESS_TOKEN;
    tokenExpiry = Date.now() + (5 * 3600 * 1000); // assumir 5h
  }
  // Renovar se expirado
  if (!cachedToken || Date.now() > tokenExpiry - 300000) {
    return await refreshToken();
  }
  return cachedToken;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const { q, limit = 12, sort = 'relevance' } = req.query;
  if (!q) return res.status(400).json({ error: 'Parâmetro q é obrigatório' });

  try {
    const token = await getToken();
    const url = `https://api.mercadolibre.com/sites/MLB/search?q=${encodeURIComponent(q)}&limit=${limit}&sort=${sort}`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    });

    if (!response.ok) throw new Error(`ML API retornou ${response.status}`);

    const data = await response.json();
    const results = (data.results || []).map(p => ({
      id:             p.id,
      title:          p.title,
      price:          p.price,
      original_price: p.original_price,
      thumbnail:      p.thumbnail,
      permalink:      p.permalink,
      free_shipping:  (p.shipping || {}).free_shipping || false,
    }));

    return res.status(200).json({ results, total: data.paging?.total || 0 });

  } catch (err) {
    console.error('Erro search ML:', err.message);
    return res.status(502).json({ error: err.message });
  }
}
