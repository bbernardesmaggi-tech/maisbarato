/**
 * api/search.js — Vercel Serverless Function
 * Proxy para a API do Mercado Livre com autenticação OAuth2 (client_credentials).
 * Resolve o bloqueio de IPs de datacenter na API do ML.
 */

let cachedToken = null;
let tokenExpiry = 0;

async function getAccessToken() {
  if (cachedToken && Date.now() < tokenExpiry - 300000) {
    return cachedToken;
  }

  const response = await fetch('https://api.mercadolibre.com/oauth/token', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type:    'client_credentials',
      client_id:     process.env.ML_APP_ID,
      client_secret: process.env.ML_CLIENT_SECRET,
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Falha ao obter token: ${response.status} — ${err}`);
  }

  const data = await response.json();
  cachedToken = data.access_token;
  tokenExpiry = Date.now() + (data.expires_in * 1000);
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
    const token = await getAccessToken();
    const url = `https://api.mercadolibre.com/sites/MLB/search?q=${encodeURIComponent(q)}&limit=${limit}&sort=${sort}`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
        'User-Agent': 'MaisBaratoOne/1.0',
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
    console.error('Erro proxy ML:', err.message);
    return res.status(502).json({ error: 'Não foi possível buscar produtos', detail: err.message });
  }
}
