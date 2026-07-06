/**
 * api/logout.js — Apaga o cookie de sessão, encerrando o login.
 * Chamado pelo botão "Sair" em admin.html e autorizar.html.
 */
export default function handler(req, res) {
  res.setHeader(
    'Set-Cookie',
    'mb_session=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0'
  );
  return res.status(200).json({ ok: true });
}
