/**
 * api/callback.js — Recebe o code do OAuth e troca por access_token
 * Salva o token como variável de ambiente no Vercel via API
 */
export default async function handler(req, res) {
  const { code } = req.query;

  if (!code) {
    return res.status(400).json({ error: 'Code não recebido' });
  }

  try {
    // Trocar code por access_token
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
      throw new Error(`Erro ao trocar token: ${tokenRes.status} — ${err}`);
    }

    const tokenData = await tokenRes.json();

    // Salvar tokens como env vars no Vercel via API
    const vercelToken = process.env.VERCEL_TOKEN;
    const projectId   = process.env.VERCEL_PROJECT_ID;
    const teamId      = process.env.VERCEL_TEAM_ID || '';

    if (vercelToken && projectId) {
      const vars = [
        { key: 'ML_ACCESS_TOKEN',  value: tokenData.access_token },
        { key: 'ML_REFRESH_TOKEN', value: tokenData.refresh_token },
        { key: 'ML_USER_ID',       value: String(tokenData.user_id) },
      ];

      for (const v of vars) {
        await fetch(`https://api.vercel.com/v10/projects/${projectId}/env${teamId ? `?teamId=${teamId}` : ''}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${vercelToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            key:    v.key,
            value:  v.value,
            type:   'encrypted',
            target: ['production', 'preview'],
          }),
        });
      }
    }

    return res.status(200).json({ ok: true, user_id: tokenData.user_id });

  } catch (err) {
    console.error('Callback error:', err.message);
    return res.status(500).json({ error: err.message });
  }
}
