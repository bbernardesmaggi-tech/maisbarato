# MaisBarato — Vitrine de Afiliados do Mercado Livre

Vitrine de produtos do Mercado Livre gerada dinamicamente via API pública oficial.
Busca realizada por proxy serverless no Vercel — sem bloqueio de CORS, produtos reais com imagens e links corretos.

---

## Estrutura do projeto

```
maisbarato/
├── api/
│   ├── search.js       ← Proxy serverless: busca produtos na API do ML (sem CORS)   
│   └── rebuild.py      ← Endpoint de rebuild (legado, não utilizado ativamente)
├── public/
│   ├── index.html      ← Vitrine principal com abas, busca e cards de produto
│   ├── og-image.png    ← Imagem de preview para WhatsApp, Telegram e redes sociais
│   ├── sitemap.xml     ← Sitemap para indexação no Google Search Console
│   └── robots.txt      ← Instruções para crawlers
├── vercel.json         ← Configuração de deploy, serverless functions e headers
└── README.md           ← Este arquivo
```

---

## Como funciona

### Fluxo de dados

```
Usuário acessa maisbaratoone.com.br
  → index.html carrega no browser
    → JS chama /api/search?q=smartphone
      → search.js (Vercel Serverless Function) chama api.mercadolibre.com
        → retorna produtos reais (imagens, preços, links)
      → vitrine exibe os cards com links de afiliado
```

### Por que proxy serverless?

A API do Mercado Livre bloqueia chamadas diretas de browsers em domínios externos (CORS)
e também bloqueia IPs de datacenters genéricos. A Serverless Function do Vercel resolve
ambos os problemas: a chamada parte do servidor com headers corretos, e o domínio próprio
(`maisbaratoone.com.br`) evita o bloqueio de origem.

---

## Funcionalidades

- **10 categorias** em abas: Eletrônicos, Computadores, Áudio, Smartwatch, Casa, Câmeras, Beleza, Tênis, Livros, Brinquedos
- **Busca em tempo real**: pesquisa qualquer produto e exibe resultados na vitrine
- **Ordenação**: por relevância, menor preço, maior preço ou maior desconto
- **Cards de produto** com imagem real, preço, desconto, frete grátis e parcelamento
- **Link de afiliado** com tag `bebr9579545` embutida automaticamente em todos os links
- **Copiar link de afiliado** com um clique (para divulgar no WhatsApp/Telegram)
- **SEO completo**: meta tags, Open Graph, Twitter Card, Schema.org WebSite + SearchAction
- **Aviso de publicidade** obrigatório (CONAR) em destaque na página
- **Responsive**: funciona em desktop e mobile

---

## Configuração de domínio

### Domínio: `maisbaratoone.com.br`
Registrado no **Registro.br**, apontado para o Vercel com os seguintes registros DNS:

| Tipo | Nome | Valor |
|---|---|---|
| A | @ | 216.198.79.1 |
| CNAME | www | 20c4a5e3e7198a89.vercel-dns-017.com. |

### URLs do projeto
- **Produção:** https://www.maisbaratoone.com.br
- **Vercel (fallback):** https://maisbarato-one.vercel.app

---

## Deploy no Vercel

### Configuração atual (`vercel.json`)
- `outputDirectory: public` — serve os arquivos estáticos da pasta `public/`
- `functions: api/search.js` — registra o proxy como Serverless Function Node.js 20
- Headers de segurança e cache configurados

### Redeploy automático
Qualquer push na branch `main` do GitHub dispara um novo deploy automático no Vercel.

### Variáveis de ambiente
Nenhuma variável de ambiente necessária na configuração atual.
Caso queira adicionar App Token do ML no futuro:
- `ML_CLIENT_ID` — Client ID do app em developers.mercadolivre.com.br
- `ML_CLIENT_SECRET` — Client Secret do app

---

## Afiliado

- **Tag de afiliado:** `bebr9579545`
- **Programa:** [afiliados.mercadolivre.com.br](https://afiliados.mercadolivre.com.br)
- **Parâmetros usados nos links:**
  - `LID=bebr9579545`
  - `matt_tool=afiliation`
  - `matt_word=bebr9579545`

---

## SEO

### Google Search Console
1. Acesse [search.google.com/search-console](https://search.google.com/search-console)
2. Adicione a propriedade `https://www.maisbaratoone.com.br`
3. Em **Sitemaps**, adicione: `https://www.maisbaratoone.com.br/sitemap.xml`

### Schema.org implementado
- `WebSite` com `SearchAction` (ativa campo de busca nos resultados do Google)
- `Organization`

---

## Conformidade com os Termos do ML

✅ Usa apenas a API pública oficial (`api.mercadolibre.com`) — sem scraping  
✅ Links com parâmetros oficiais do programa (`LID`, `matt_tool`, `matt_word`)  
✅ Aviso obrigatório de publicidade (CONAR/CDC) em todas as páginas  
✅ Hashtags `#publi` e `#ad` exibidas em destaque  
✅ Sem automação de cliques ou compras  
✅ Sem encurtamento ou modificação dos links especiais  
✅ Atributo `rel="sponsored"` em todos os links de afiliado  
✅ Sem uso de marcas, logotipos ou nomes do ML no domínio ou conteúdo promocional  
✅ Sem anúncios pagos em buscadores (Google Ads, etc.)  

---

## Histórico de versões

| Versão | Descrição |
|---|---|
| v1.0 | Vitrine estática com busca via API direta no browser |
| v1.1 | SEO completo: meta tags, Open Graph, Schema.org, sitemap, robots.txt |
| v1.2 | og-image.png gerada (1200×630px) com identidade visual ML |
| v2.0 | Proxy serverless (`api/search.js`) — busca real com imagens e links corretos |
| v2.1 | Abas por categoria, ordenação, busca na vitrine, domínio `maisbaratoone.com.br` |
