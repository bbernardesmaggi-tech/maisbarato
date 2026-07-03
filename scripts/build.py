"""
build.py — MaisBarato
Busca produtos via API pública do Mercado Livre e gera o HTML estático.
Rode manualmente ou via cron/Vercel cron job.
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Configuração ─────────────────────────────────────────
AFFILIATE_TAG   = "bebr9579545"
SITE_ID         = "MLB"          # Brasil
PRODUCTS_PER_CAT = 12            # produtos por categoria
OUTPUT_HTML     = Path(__file__).parent.parent / "public" / "index.html"
OUTPUT_JSON     = Path(__file__).parent.parent / "public" / "products.json"
BASE_URL        = "https://maisbarato.com.br"

CATEGORIES = [
    {"slug": "eletronicos",  "label": "📱 Eletrônicos",  "query": "mais vendidos eletrônicos"},
    {"slug": "computadores", "label": "💻 Computadores",  "query": "notebook laptop"},
    {"slug": "audio",        "label": "🎧 Áudio",         "query": "fone de ouvido headphone bluetooth"},
    {"slug": "smartwatch",   "label": "⌚ Smartwatch",    "query": "smartwatch relogio inteligente"},
    {"slug": "casa",         "label": "🏠 Casa",          "query": "casa inteligente smart home"},
    {"slug": "cameras",      "label": "📷 Câmeras",       "query": "câmera fotográfica"},
    {"slug": "beleza",       "label": "🌸 Beleza",        "query": "perfume masculino feminino"},
    {"slug": "tenis",        "label": "👟 Tênis",         "query": "tênis esportivo masculino"},
    {"slug": "livros",       "label": "📚 Livros",        "query": "livro mais vendido"},
    {"slug": "brinquedos",   "label": "🧸 Brinquedos",   "query": "brinquedo infantil"},
]
# ─────────────────────────────────────────────────────────


def fetch_products(query: str, limit: int = 12) -> list:
    """Consulta a API pública do Mercado Livre."""
    encoded = urllib.parse.quote(query)
    url = f"https://api.mercadolibre.com/sites/{SITE_ID}/search?q={encoded}&limit={limit}&sort=relevance"
    req = urllib.request.Request(url, headers={"User-Agent": "MaisBarato-Builder/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("results", [])
    except Exception as e:
        print(f"  ⚠️  Erro ao buscar '{query}': {e}")
        return []


def build_affiliate_url(permalink: str) -> str:
    """Adiciona os parâmetros oficiais do programa de afiliados."""
    parsed = urllib.parse.urlparse(permalink)
    params = urllib.parse.parse_qs(parsed.query)
    params["LID"]       = [AFFILIATE_TAG]
    params["matt_tool"] = ["afiliation"]
    params["matt_word"] = [AFFILIATE_TAG]
    new_query = urllib.parse.urlencode({k: v[0] for k, v in params.items()})
    return parsed._replace(query=new_query).geturl()


def fmt_brl(value: float) -> str:
    """Formata valor em Real Brasileiro."""
    return f"R$\u00a0{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def discount_pct(price: float, original: float) -> int:
    if original and original > price:
        return round((1 - price / original) * 100)
    return 0


def render_product_card(p: dict) -> str:
    """Gera o HTML de um card de produto."""
    title   = p.get("title", "")
    price   = p.get("price", 0)
    orig    = p.get("original_price") or 0
    thumb   = (p.get("thumbnail") or "").replace("I.jpg", "O.jpg")
    url     = build_affiliate_url(p.get("permalink", "#"))
    disc    = discount_pct(price, orig)
    free_sh = (p.get("shipping") or {}).get("free_shipping", False)
    installment = ""
    if price >= 100:
        val = price / 12
        installment = f'<p class="installments">12x de {fmt_brl(val)} sem juros*</p>'

    badge_ship = '<span class="badge-ship">FRETE GRÁTIS</span>' if free_sh else ""
    badge_disc = f'<span class="badge-disc">-{disc}%</span>' if disc >= 5 else ""
    old_price  = f'<s class="old-price">{fmt_brl(orig)}</s>' if disc >= 5 else ""

    # Schema.org Product para SEO
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "image": thumb,
        "offers": {
            "@type": "Offer",
            "priceCurrency": "BRL",
            "price": str(price),
            "availability": "https://schema.org/InStock",
            "url": url
        }
    }, ensure_ascii=False)

    return f"""
    <article class="card" itemscope itemtype="https://schema.org/Product">
      <script type="application/ld+json">{schema}</script>
      <a href="{url}" target="_blank" rel="noopener sponsored" class="card-link" aria-label="Ver {title} no Mercado Livre">
        <div class="card-img">
          {badge_ship}
          <img src="{thumb}" alt="{title}" loading="lazy" width="200" height="200" itemprop="image">
        </div>
        <div class="card-body">
          <p class="card-title" itemprop="name">{title}</p>
          <div class="price-area" itemprop="offers" itemscope itemtype="https://schema.org/Offer">
            {old_price}
            <div class="price-row">
              <strong class="price" itemprop="price" content="{price}">{fmt_brl(price)}</strong>
              {badge_disc}
            </div>
            {installment}
          </div>
        </div>
      </a>
      <button class="btn-copy" onclick="copyLink('{url}', this)" aria-label="Copiar link de afiliado">
        📋 Copiar link
      </button>
    </article>"""


def render_category_section(cat: dict, products: list) -> str:
    """Gera a seção HTML de uma categoria."""
    if not products:
        return ""
    cards = "\n".join(render_product_card(p) for p in products)
    return f"""
  <section class="cat-section" id="{cat['slug']}" aria-label="{cat['label']}">
    <h2 class="cat-title">{cat['label']}</h2>
    <div class="product-grid">{cards}</div>
  </section>"""


def render_html(categories_data: list, built_at: str) -> str:
    """Gera o HTML completo da vitrine."""
    nav_items = "".join(
        f'<a href="#{c["slug"]}" class="nav-cat">{c["label"]}</a>'
        for c in CATEGORIES
    )
    sections = "\n".join(
        render_category_section(c, products)
        for c, products in categories_data
    )
    total = sum(len(p) for _, p in categories_data)

    return f"""<!DOCTYPE html>
<html lang="pt-BR" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- SEO PRIMÁRIO -->
<title>MaisBarato — Melhores Ofertas do Mercado Livre Hoje</title>
<meta name="description" content="Encontre as melhores ofertas e produtos mais vendidos do Mercado Livre com frete grátis e parcelamento. {total} produtos selecionados, atualizado diariamente.">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="theme-color" content="#FFE600">
<link rel="canonical" href="{BASE_URL}/">

<!-- OPEN GRAPH -->
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="MaisBarato">
<meta property="og:title" content="MaisBarato — Melhores Ofertas do Mercado Livre Hoje">
<meta property="og:description" content="{total} produtos selecionados com frete grátis, parcelamento e os menores preços. Atualizado diariamente.">
<meta property="og:url" content="{BASE_URL}/">
<meta property="og:image" content="{BASE_URL}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">

<!-- TWITTER CARD -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="MaisBarato — Melhores Ofertas do Mercado Livre">
<meta name="twitter:description" content="{total} produtos com frete grátis e menores preços. Atualizado diariamente.">
<meta name="twitter:image" content="{BASE_URL}/og-image.png">

<!-- SCHEMA.ORG WebSite + SearchAction -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "MaisBarato",
  "url": "{BASE_URL}/",
  "description": "Vitrine de ofertas do Mercado Livre com os melhores preços e frete grátis.",
  "inLanguage": "pt-BR",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": {{"@type": "EntryPoint", "urlTemplate": "{BASE_URL}/?q={{search_term_string}}"}},
    "query-input": "required name=search_term_string"
  }}
}}
</script>

<link rel="preconnect" href="https://http2.mlstatic.com">
<link rel="dns-prefetch" href="https://http2.mlstatic.com">

<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --yellow:#FFE600;--blue:#3483FA;--blue-d:#2968C8;
  --green:#00A650;--green-l:#E8F8EF;
  --bg:#F5F5F5;--surface:#fff;--text:#1A1A1A;
  --muted:#888;--border:#E0E0E0;--radius:12px;
  --shadow:0 2px 8px rgba(0,0,0,.08);
  --shadow-h:0 6px 20px rgba(0,0,0,.13);
}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.5}}

/* HEADER */
header{{background:var(--yellow);position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.12)}}
.hdr{{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:1rem;height:60px;padding:0 1.5rem}}
.logo{{font-size:20px;font-weight:700;letter-spacing:-.5px;white-space:nowrap}}
.logo span{{color:var(--blue)}}
.search-wrap{{flex:1;display:flex;background:#fff;border-radius:8px;overflow:hidden;border:2px solid transparent;transition:border .15s;max-width:560px}}
.search-wrap:focus-within{{border-color:var(--blue)}}
.search-wrap input{{flex:1;border:none;outline:none;padding:.45rem .75rem;font-size:14px}}
.search-wrap button{{background:var(--blue);border:none;color:#fff;padding:0 1rem;cursor:pointer;font-size:15px;transition:background .15s}}
.search-wrap button:hover{{background:var(--blue-d)}}
.aff-pill{{background:var(--blue);color:#fff;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;white-space:nowrap}}

/* NAV CATEGORIAS */
.cat-nav{{background:#fff;border-bottom:1px solid var(--border);overflow-x:auto;-webkit-overflow-scrolling:touch}}
.cat-nav-inner{{max-width:1200px;margin:0 auto;display:flex;gap:4px;padding:.6rem 1.5rem;white-space:nowrap}}
.nav-cat{{font-size:13px;font-weight:500;color:var(--text);padding:5px 12px;border-radius:20px;text-decoration:none;transition:all .15s;flex-shrink:0}}
.nav-cat:hover{{background:var(--blue);color:#fff}}

/* AVISO DE PUBLICIDADE */
.pub-notice{{background:#fff3cd;border-bottom:1px solid #ffc107;padding:.5rem 1.5rem;font-size:12px;color:#5a4000;text-align:center}}

/* MAIN */
.main{{max-width:1200px;margin:0 auto;padding:1.5rem}}

/* BUSCA INLINE (filtro JS) */
.search-info{{font-size:13px;color:var(--muted);margin-bottom:1rem;display:none}}

/* SEÇÕES */
.cat-section{{margin-bottom:2.5rem}}
.cat-title{{font-size:18px;font-weight:600;margin-bottom:1rem;padding-bottom:.5rem;border-bottom:2px solid var(--yellow)}}

/* GRID */
.product-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem}}

/* CARD */
.card{{background:var(--surface);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .18s,transform .18s}}
.card:hover{{box-shadow:var(--shadow-h);transform:translateY(-3px)}}
.card-link{{text-decoration:none;color:inherit;display:flex;flex-direction:column;flex:1}}
.card-img{{position:relative;aspect-ratio:1;background:#f8f8f8;overflow:hidden}}
.card-img img{{width:100%;height:100%;object-fit:contain;padding:12px;transition:transform .2s}}
.card:hover .card-img img{{transform:scale(1.05)}}
.badge-ship{{position:absolute;top:8px;left:8px;background:var(--green);color:#fff;font-size:10px;font-weight:700;padding:3px 7px;border-radius:4px}}
.card-body{{padding:.85rem;display:flex;flex-direction:column;gap:6px;flex:1}}
.card-title{{font-size:13px;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:36px}}
.old-price{{font-size:11px;color:var(--muted);text-decoration:line-through}}
.price-row{{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap}}
.price{{font-size:19px;font-weight:700;letter-spacing:-.5px}}
.badge-disc{{font-size:11px;font-weight:700;color:var(--green);background:var(--green-l);padding:2px 6px;border-radius:4px}}
.installments{{font-size:11px;color:var(--green);font-weight:500}}
.btn-copy{{width:100%;background:transparent;border:1.5px solid var(--green);color:var(--green);border-radius:8px;padding:8px;font-size:12px;font-weight:600;cursor:pointer;margin:.75rem .75rem .75rem;width:calc(100% - 1.5rem);transition:all .15s}}
.btn-copy:hover{{background:var(--green-l)}}

/* DISCLAIMER */
.disclaimer{{margin-top:2rem;padding:1rem 1.25rem;background:#fff;border-radius:10px;border:1px solid var(--border);font-size:12px;color:var(--muted);line-height:1.6}}
.disclaimer strong{{color:#4A4A4A}}

/* FOOTER */
footer{{text-align:center;padding:2rem 1rem;font-size:12px;color:var(--muted);border-top:1px solid var(--border);margin-top:1rem}}
.built-at{{font-size:11px;color:var(--muted);margin-top:.25rem}}

/* TOAST */
.toast{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:#1A1A1A;color:#fff;padding:10px 20px;border-radius:20px;font-size:13px;opacity:0;transition:all .25s;z-index:9999;white-space:nowrap;pointer-events:none}}
.toast.show{{opacity:1;transform:translateX(-50%) translateY(0)}}

@media(max-width:600px){{
  .aff-pill{{display:none}}
  .product-grid{{grid-template-columns:repeat(2,1fr);gap:.75rem}}
  .price{{font-size:15px}}
  .main{{padding:1rem}}
}}
</style>
</head>
<body>

<header>
  <div class="hdr">
    <div class="logo" aria-label="MaisBarato">Mais<span>Barato</span></div>
    <div class="search-wrap">
      <input type="text" id="searchInput" placeholder="Filtrar produtos na página..." aria-label="Filtrar produtos">
      <button onclick="filterProducts()" aria-label="Buscar">&#128269;</button>
    </div>
    <div class="aff-pill">🤝 Afiliado ML</div>
  </div>
</header>

<nav class="cat-nav" aria-label="Categorias">
  <div class="cat-nav-inner">
    {nav_items}
  </div>
</nav>

<div class="pub-notice" role="note">
  ⚠️ <strong>Conteúdo publicitário</strong> — Esta página contém links de afiliado do Mercado Livre. Ao comprar, recebo uma comissão sem custo adicional para você. <strong>#publi #ad</strong>
</div>

<main class="main" id="main">
  <p class="search-info" id="searchInfo" aria-live="polite"></p>
  {sections}

  <div class="disclaimer">
    <strong>Aviso obrigatório (CONAR/CDC):</strong> Esta página contém links de afiliado do Programa de Afiliados e Criadores do Mercado Livre. Ao clicar e efetuar uma compra, posso receber uma comissão a título de direito de imagem, sem qualquer custo adicional para você. Todos os produtos são vendidos e entregues pelo <strong>Mercado Livre</strong>. Preços e disponibilidade podem mudar — confirme sempre antes de comprar. Última atualização: {built_at}.
  </div>
</main>

<footer>
  <div>MaisBarato · Vitrine de afiliados do Mercado Livre</div>
  <div class="built-at">Atualizado automaticamente em {built_at}</div>
</footer>

<div class="toast" id="toast" role="status" aria-live="polite"></div>

<script>
function copyLink(url, btn) {{
  navigator.clipboard.writeText(url).then(() => {{
    showToast('✅ Link de afiliado copiado!');
    const orig = btn.textContent;
    btn.textContent = '✅ Copiado!';
    setTimeout(() => btn.textContent = orig, 2000);
  }}).catch(() => {{ prompt('Copie o link:', url); }});
}}

function filterProducts() {{
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const cards = document.querySelectorAll('.card');
  const info = document.getElementById('searchInfo');
  let visible = 0;
  cards.forEach(c => {{
    const title = c.querySelector('.card-title').textContent.toLowerCase();
    const show = !q || title.includes(q);
    c.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  document.querySelectorAll('.cat-section').forEach(sec => {{
    const anyVisible = [...sec.querySelectorAll('.card')].some(c => c.style.display !== 'none');
    sec.style.display = anyVisible ? '' : 'none';
  }});
  if (q) {{
    info.style.display = 'block';
    info.textContent = visible + ' produto(s) encontrado(s) para "' + q + '"';
  }} else {{
    info.style.display = 'none';
  }}
}}

document.getElementById('searchInput').addEventListener('keydown', e => {{
  if (e.key === 'Enter') filterProducts();
}});

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}}
</script>
</body>
</html>"""


def main():
    print(f"\n🔨 MaisBarato — Build estático")
    print(f"   {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    categories_data = []
    all_products_json = {}

    for cat in CATEGORIES:
        print(f"  🔍 Buscando: {cat['label']} ({cat['query']})")
        products = fetch_products(cat["query"], PRODUCTS_PER_CAT)
        print(f"     ✅ {len(products)} produtos encontrados")
        categories_data.append((cat, products))
        all_products_json[cat["slug"]] = [
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "price": p.get("price"),
                "original_price": p.get("original_price"),
                "thumbnail": p.get("thumbnail"),
                "permalink": build_affiliate_url(p.get("permalink", "")),
                "free_shipping": (p.get("shipping") or {}).get("free_shipping", False),
            }
            for p in products
        ]
        time.sleep(0.5)  # respeitar rate limit da API

    built_at = datetime.now(timezone.utc).strftime("%d/%m/%Y às %H:%M UTC")
    html = render_html(categories_data, built_at)

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    OUTPUT_JSON.write_text(
        json.dumps(all_products_json, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    total = sum(len(p) for _, p in categories_data)
    print(f"\n✅ Build concluído!")
    print(f"   📄 {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size // 1024} KB)")
    print(f"   📦 {OUTPUT_JSON} ({OUTPUT_JSON.stat().st_size // 1024} KB)")
    print(f"   🛍️  {total} produtos de {len(CATEGORIES)} categorias\n")


if __name__ == "__main__":
    main()
