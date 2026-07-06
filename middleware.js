/**
 * middleware.js — Vercel Edge Middleware
 * Protege as rotas administrativas e de API sensíveis com HTTP Basic Auth.
 * A vitrine pública (/, /eletronicos, /notebooks, etc.) NÃO é afetada.
 *
 * Configuração necessária no Vercel (Project → Settings → Environment Variables):
 *   ADMIN_USER = escolha um usuário
 *   ADMIN_PASS = escolha uma senha forte
 * (adicionar em Production e Preview, depois fazer Redeploy)
 */

export const config = {
  matcher: [
    '/admin.html',
    '/autorizar.html',
    '/api/callback',
    '/api/search',
    '/api/product',
  ],
};

export default function middleware(req) {
  const auth = req.headers.get('authorization');

  if (auth) {
    const [scheme, encoded] = auth.split(' ');
    if (scheme === 'Basic' && encoded) {
      const [user, pass] = atob(encoded).split(':');
      if (user === process.env.ADMIN_USER && pass === process.env.ADMIN_PASS) {
        return; // autenticado — segue normalmente para a rota solicitada
      }
    }
  }

  return new Response('Autenticação necessária', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="Área restrita MaisBarato"' },
  });
}
