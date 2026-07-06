/**
 * api/product.js — Busca dados de um produto ML pelo ID ou URL
 * Usa o ML_ACCESS_TOKEN do usuário (tem acesso à API de items)
 * Chamada: GET /api/product?url=MLB123 ou ?url=https://produto.mercadolivre...
 */

const TAG = 'bebr9579545';

function extractItemId(input) {
  const patterns = [
    /\bMLB-?(\d+)\b/i,
    /\/p\/MLB(\d+)/i,
    /item_id=MLB(\d+)/i,
  ];
  for (const p of patterns) {
    const m = input.match(p);
    if (m) return `MLB${m[1]}`;
  }
  return null;
}

function buildAffUrl(permalink) {
  try {
    const url = new URL(permalink);
    url.searchParams.set('LID', TAG);
    url.searchParams.set('matt_tool', 'afiliation');
    url.searchParams.set('matt_word', TAG);
    return url.toString();
  } catch(e) { return permalink; }
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { url } = req.query;
  if (!url) return res.status(400).json({ error: 'Parâmetro url é obrigatório' });

  // Extrair ID do produto
  let itemId = extractItemId(url);

  // Se não achou ID, tentar resolver URL curta via redirect
  if (!itemId) {
    try {
      const r = await fetch(url, {
        method: 'HEAD',
        redirect: 'follow',
        headers: { 'User-Agent': 'Mozilla/5.0' },
      });
      itemId = extractItemId(r.url);
      if (!itemId) {
        // Tentar GET para pegar o conteúdo
        const r2 = await fetch(url, {
          redirect: 'follow',
          headers: { 'User-Agent': 'Mozilla/5.0' },
        });
        itemId = extractItemId(r2.url);
      }
    } catch(e) {}
  }

  if (!itemId) {
    return res.status(400).json({ error: 'Não foi possível identificar o produto. Use o link completo do ML com MLB no ID.' });
  }

  // Buscar dados via API com token de usuário
  const token = process.env.ML_ACCESS_TOKEN;
  if (!token) return res.status(500).json({ error: 'Token ML não configurado' });

  try {
    const apiRes = await fetch(`https://api.mercadolibre.com/items/${itemId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    });

    if (!apiRes.ok) {
      throw new Error(`API ML retornou ${apiRes.status}`);
    }

    const data = await apiRes.json();

    return res.status(200).json({
      id:             data.id,
      title:          data.title,
      price:          data.price,
      original_price: data.original_price,
      thumbnail:      (data.thumbnail || '').replace('I.jpg', 'O.jpg'),
      permalink:      buildAffUrl(data.permalink),
      free_shipping:  (data.shipping || {}).free_shipping || false,
    });

  } catch(err) {
    console.error('Erro product API:', err.message);
    return res.status(502).json({ error: err.message });
  }
}
