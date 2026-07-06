/**
 * api/login.js — Verifica usuário/senha e cria o cookie de sessão.
 * Chamado pelo formulário em /login.html.
 */
export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  const { user, pass } = req.body || {};

  if (user === process.env.ADMIN_USER && pass === process.env.ADMIN_PASS) {
    const maxAge = 60 * 60 * 8; // sessão válida por 8 horas
    res.setHeader(
      'Set-Cookie',
      `mb_session=${process.env.SESSION_SECRET}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${maxAge}`
    );
    return res.status(200).json({ ok: true });
  }

  return res.status(401).json({ ok: false, error: 'Usuário ou senha inválidos' });
}
