/**
 * api/callback.js — Troca o code ML por tokens e exibe na tela para salvar manualmente
 */
export default async function handler(req, res) {
  const { code } = req.query;
  if (!code) return res.status(400).json({ error: 'Code não recebido' });

  try {
    const tokenRes = await fetch('https://api.mercadolibre.com/oauth/token', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type:    'authorization_code',
        client_id:     process.env.ML_APP_ID,
        client_secret: process.env.ML_CLIENT_SECRET,
        code:          code,
        redirect_uri:  'https://www.maisbaratoone.com.br/api/callback',
      }),
    });

    if (!tokenRes.ok) {
      const err = await tokenRes.text();
      throw new Error(`Erro ${tokenRes.status}: ${err}`);
    }

    const data = await tokenRes.json();

    // Retornar HTML com os tokens para copiar manualmente
    const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Tokens ML</title>
<style>
  body{font-family:sans-serif;padding:2rem;background:#f5f5f5}
  .card{background:#fff;border-radius:12px;padding:2rem;max-width:700px;margin:0 auto;box-shadow:0 2px 12px rgba(0,0,0,.1)}
  h1{color:#00A650;margin-bottom:1rem}
  .field{margin-bottom:1.5rem}
  label{font-size:12px;font-weight:700;color:#666;display:block;margin-bottom:.4rem;text-transform:uppercase}
  .token{background:#f0f0f0;padding:.75rem 1rem;border-radius:8px;font-family:monospace;font-size:12px;word-break:break-all;cursor:pointer;border:2px solid transparent;transition:.15s}
  .token:hover{border-color:#3483FA}
  .btn{display:inline-block;background:#FFE600;color:#1A1A1A;font-weight:700;padding:12px 24px;border-radius:8px;text-decoration:none;font-size:14px;margin-top:1rem}
  .instructions{background:#fff3cd;border-radius:8px;padding:1rem;margin-top:1.5rem;font-size:13px;line-height:1.7}
</style>
</head>
<body>
<div class="card">
  <h1>✅ Autorização concluída!</h1>
  <p style="margin-bottom:1.5rem;color:#444">Copie os valores abaixo e salve nas variáveis de ambiente do Vercel:</p>
  
  <div class="field">
    <label>ML_ACCESS_TOKEN (clique para copiar)</label>
    <div class="token" onclick="copy(this, '${data.access_token}')">${data.access_token}</div>
  </div>
  
  <div class="field">
    <label>ML_REFRESH_TOKEN (clique para copiar)</label>
    <div class="token" onclick="copy(this, '${data.refresh_token}')">${data.refresh_token}</div>
  </div>

  <div class="field">
    <label>ML_USER_ID</label>
    <div class="token">${data.user_id}</div>
  </div>

  <div class="instructions">
    <strong>Como salvar no Vercel:</strong><br>
    1. Acesse Vercel → Environment Variables<br>
    2. Clique em <strong>"..."</strong> ao lado de <strong>ML_ACCESS_TOKEN</strong> → Edit → cole o valor → Save<br>
    3. Repita para <strong>ML_REFRESH_TOKEN</strong><br>
    4. Faça <strong>Redeploy</strong> no Vercel
  </div>
</div>
<script>
function copy(el, val) {
  navigator.clipboard.writeText(val).then(() => {
    el.style.borderColor = '#00A650';
    el.title = 'Copiado!';
    setTimeout(() => el.style.borderColor = 'transparent', 2000);
  });
}
</script>
</body>
</html>`;

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(html);

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
