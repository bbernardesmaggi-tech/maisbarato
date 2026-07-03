# MaisBarato — Vitrine de Afiliados do Mercado Livre

Vitrine estática gerada automaticamente via API pública do Mercado Livre.
Rebuild todo dia às **03:00 UTC (00:00 de Brasília)** via cron do Vercel.

---

## Estrutura do projeto

```
maisbarato/
├── scripts/
│   └── build.py        ← Script principal: busca API ML e gera o HTML
├── api/
│   └── rebuild.py      ← Endpoint serverless acionado pelo cron
├── public/             ← Gerado automaticamente pelo build
│   ├── index.html      ← Vitrine estática
│   ├── products.json   ← Dados dos produtos em JSON
│   ├── sitemap.xml     ← Sitemap para o Google
│   ├── robots.txt      ← Instruções para crawlers
│   └── og-image.png    ← Imagem de preview para redes sociais (você cria)
├── vercel.json         ← Configuração de deploy e cron
└── README.md
```

---

## Deploy no Vercel (gratuito) — passo a passo

### 1. Criar conta e repositório

1. Crie uma conta gratuita em [github.com](https://github.com)
2. Crie um repositório público chamado `maisbarato`
3. Faça upload de todos os arquivos deste projeto

### 2. Conectar ao Vercel

1. Acesse [vercel.com](https://vercel.com) e crie uma conta (pode entrar com GitHub)
2. Clique em **"Add New Project"**
3. Selecione o repositório `maisbarato`
4. O Vercel detecta o `vercel.json` automaticamente
5. Clique em **"Deploy"**

### 3. Configurar variáveis de ambiente (opcional mas recomendado)

No painel do Vercel → Settings → Environment Variables:

| Variável | Valor | Descrição |
|---|---|---|
| `REBUILD_SECRET` | uma senha forte | Protege o endpoint /api/rebuild |
| `CRON_SECRET` | gerado pelo Vercel | Criado automaticamente |

### 4. Configurar domínio personalizado

No painel do Vercel → Settings → Domains:
- Adicione seu domínio (ex: `maisbarato.com.br`)
- Aponte o DNS conforme instruções do Vercel

### 5. Registrar no Google Search Console

1. Acesse [search.google.com/search-console](https://search.google.com/search-console)
2. Adicione sua propriedade (URL do site)
3. Em **Sitemaps**, adicione: `https://seu-dominio.com.br/sitemap.xml`
4. Aguarde indexação (pode levar de 3 a 14 dias)

---

## Rodar localmente

```bash
# Instalar dependências (nenhuma externa — só Python padrão)
python --version  # precisa de Python 3.8+

# Gerar o HTML estático
python scripts/build.py

# Ver resultado
open public/index.html
# ou
python -m http.server 8000 --directory public
# depois acesse http://localhost:8000
```

---

## Personalizar categorias

Edite `scripts/build.py`, seção `CATEGORIES`:

```python
CATEGORIES = [
    {"slug": "eletronicos", "label": "📱 Eletrônicos", "query": "mais vendidos eletrônicos"},
    # Adicione ou remova categorias aqui
    {"slug": "games",       "label": "🎮 Games",        "query": "video game console"},
]
```

---

## Trocar o domínio

Substitua `https://maisbarato.com.br` em:
- `scripts/build.py` → variável `BASE_URL`
- `public/sitemap.xml`
- `public/robots.txt`

---

## Como funciona o cron

```
vercel.json define:
  "schedule": "0 3 * * *"   ← todo dia às 03:00 UTC (00:00 Brasília)
  "path": "/api/rebuild"     ← chama este endpoint

O endpoint executa scripts/build.py:
  1. Busca produtos em 10 categorias via API do ML
  2. Gera public/index.html com os dados embutidos
  3. Gera public/products.json
  O Vercel serve os arquivos gerados automaticamente.
```

---

## Conformidade com os Termos do ML

✅ Usa apenas a API pública oficial (`api.mercadolibre.com`)  
✅ Links com parâmetros oficiais do programa (`LID`, `matt_tool`, `matt_word`)  
✅ Aviso obrigatório de publicidade (CONAR) em todas as páginas  
✅ Sem automação de cliques ou compras  
✅ Sem web scraping  
✅ Rel `sponsored` nos links de afiliado  

---

## Suporte

Tag de afiliado: `bebr9579545`  
Programa: [afiliados.mercadolivre.com.br](https://afiliados.mercadolivre.com.br)
