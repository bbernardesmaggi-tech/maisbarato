/**
 * middleware.js — Vercel Edge Middleware
 * Protege as rotas administrativas e de API sensíveis via cookie de sessão.
 * A vitrine pública (/, /eletronicos, /notebooks, etc.) NÃO é afetada.
 *
 * Variáveis de ambiente necessárias (Vercel → Settings → Environment Variables):
 *   ADMIN_USER     = usuário de login (o mesmo já configurado)
 *   ADMIN_PASS     = senha de login (a mesma já configurada)
 *   SESSION_SECRET = uma string aleatória longa (gere uma nova, não reutilize exemplos)
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

const COOKIE_NAME = 'mb_session';

function getCookie(cookieHeader, name) {
  if (!cookieHeader) return null;
  const match = cookieHeader.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

export default function middleware(req) {
  const token = getCookie(req.headers.get('cookie'), COOKIE_NAME);

  if (token && token === process.env.SESSION_SECRET) {
    return; // sessão válida — segue normalmente
  }

  const url = new URL(req.url);

  // Chamadas de API recebem 401 em JSON, não redirecionamento
  if (url.pathname.startsWith('/api/')) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Páginas HTML são redirecionadas para o login, preservando o destino original
  const loginUrl = new URL('/login.html', req.url);
  loginUrl.searchParams.set('redirect', url.pathname);
  return Response.redirect(loginUrl, 302);
}
