/**
 * api/search.js — Vercel Serverless Function
 * Proxy para a API do Mercado Livre, resolvendo o bloqueio de CORS.
 * Chamada: GET /api/search?q=smartphone&limit=12
 */

export default async function handler(req, res) {
  // CORS — permite chamadas do domínio próprio
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600'); // cache 5 min

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { q, limit = 12, sort = 'relevance' } = req.query;

  if (!q) {
    return res.status(400).json({ error: 'Parâmetro q é obrigatório' });
  }

  const url = `https://api.mercadolibre.com/sites/MLB/search?q=${encodeURIComponent(q)}&limit=${limit}&sort=${sort}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Referer': 'https://www.mercadolivre.com.br/',
      },
    });

    if (!response.ok) {
      throw new Error(`ML API retornou ${response.status}`);
    }

    const data = await response.json();

    // Retornar apenas os campos necessários (reduz tamanho da resposta)
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
