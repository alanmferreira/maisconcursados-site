# -*- coding: utf-8 -*-
"""Gera o site estático Mais Concursados.
Uso: python3 build.py            -> site/     (produção, CSS e JS em arquivos)
     python3 build.py preview    -> preview/  (CSS e JS embutidos, para a prévia)
"""
import os, sys, json, shutil, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from articles import ARTICLES

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)           # raiz do repositório
MODE = sys.argv[1] if len(sys.argv) > 1 else "prod"
OUT = os.path.join(BASE, "preview" if MODE == "preview" else "site")
SITE = "https://maisconcursados.com.br"
NAME = "Mais Concursados"
IG = "https://instagram.com/prof.alanmoraes"
import datetime
TODAY = os.environ.get("BUILD_DATE") or (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d")

import hashlib
css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
js = open(os.path.join(HERE, "app.js"), encoding="utf-8").read()
editais_raw = open(os.path.join(HERE, "editais.json"), encoding="utf-8").read()

CONFIG_JS = """/* Configuração do site Mais Concursados.
   Preencha os campos abaixo quando as ferramentas estiverem prontas. Campo vazio = recurso desligado. */
window.MC_CONFIG = {
  // Endereço que recebe os cadastros (formulário do Brevo, Mailchimp, RD Station, Formspree ou webhook).
  // O site envia um JSON com: email, whatsapp, interesse, origem, consentimento, data.
  leadsEndpoint: "",
  // Mailchimp (formulário incorporado): endereço "action" do formulário e nome do campo anti-robô (b_...).
  mailchimpAction: "https://maisconcursados.us13.list-manage.com/subscribe/post?u=8cefefc6b696b012af0395df7&id=596510e64a&f_id=008d00e9f0",
  mailchimpHoneypot: "b_8cefefc6b696b012af0395df7_596510e64a",
  // Link de convite do grupo ou da comunidade de WhatsApp. Quando preenchido, aparece o botão "Entrar no grupo".
  whatsappGroupUrl: "https://chat.whatsapp.com/E4UEBEedzbH2DpyvREZUoH?s=cl&p=a&mlu=4&ilr=4",
  // Link de pagamento ou de inscrição da turma Bancada BACEN (Herospark, Hotmart etc.). Vazio = botão leva à lista de espera.
  checkoutBancadaUrl: "",
  // E-mail de contato exibido na página Contato (opcional).
  contactEmail: "",
  // ID do Google Analytics 4, no formato G-XXXXXXXXXX (opcional).
  analyticsId: ""
};
"""
VER = hashlib.md5((css + js + CONFIG_JS).encode("utf-8")).hexdigest()[:8]

def esc(s): return html.escape(s, quote=True)

def tag_nav(active, root):
    items = [("index.html", "Início", "inicio"), ("editais.html", "Editais", "editais"), ("cursos.html", "Cursos", "cursos"), ("blog.html", "Blog", "blog"),
             ("sobre.html", "Sobre", "sobre")]
    out = []
    for href, label, key in items:
        cur = ' aria-current="page"' if active == key else ""
        out.append('<li><a href="%s%s"%s>%s</a></li>' % (root, href, cur, label))
    cur = ' aria-current="page"' if active == "mentorias" else ""
    out.append('<li><a class="cta" href="%smentorias.html"%s>Mentorias</a></li>' % (root, cur))
    return "".join(out)

def header(active, root):
    return ('<a class="skip" href="#conteudo">Ir para o conteúdo</a>'
            '<header class="top"><div class="wrap bar">'
            '<a class="logo" href="%sindex.html" aria-label="Mais Concursados, página inicial">'
            '<img class="logo-img lt" src="%sassets/logo-light.png" width="760" height="249" alt="Mais Concursados">'
            '<img class="logo-img dk" src="%sassets/logo-dark.png" width="760" height="249" alt="">'
            '</a><nav aria-label="Principal"><ul>%s</ul></nav></div></header>') % (root, root, root, tag_nav(active, root))

def footer(root):
    return ('<footer><div class="wrap">'
            '<div><h4>Mais Concursados</h4><p>Editais de concursos de todas as áreas, com destaque para os bancários, e estudo com método para quem quer a aprovação. Por Alan Moraes, bancário, professor e mentor para concursos.</p></div>'
            '<div><h4>Navegue</h4><ul><li><a href="%seditais.html">Editais</a></li><li><a href="%scursos.html">Cursos</a></li><li><a href="%sblog.html">Blog</a></li><li><a href="%smentorias.html">Mentorias</a></li></ul></div>'
            '<div><h4>Institucional</h4><ul><li><a href="%ssobre.html">Sobre o Alan</a></li><li><a href="%scontato.html">Contato</a></li><li><a href="%sprivacidade.html">Política de privacidade</a></li></ul></div>'
            '<p class="legal">© 2026 Mais Concursados · maisconcursados.com.br. As informações de editais vêm de portais de notícias e devem ser conferidas no edital oficial. O Mais Concursados não é banca organizadora nem órgão público.</p>'
            '</div></footer>') % ((root,) * 7)

def lead_form(origem, interesse_hidden=None, wpp=True, label_btn="Quero receber os alertas", fid="x"):
    hid = '<input type="hidden" name="interesse" value="%s">' % esc(interesse_hidden) if interesse_hidden else ""
    interesse_field = "" if interesse_hidden else ('<label for="%s-int">Concurso de interesse<input id="%s-int" name="interesse" type="text" placeholder="Ex.: Banco Central, tribunais, polícia, prefeituras"></label>' % (fid, fid))
    wpp_field = ('<label for="%s-wpp">WhatsApp (opcional)<input id="%s-wpp" name="whatsapp" type="tel" placeholder="(91) 90000-0000" autocomplete="tel"></label>' % (fid, fid)) if wpp else ""
    MC_TAGS = {"mentoria-bancada-bacen": "7215796,7215806", "mentoria-bb": "7215796,7215807"}  # Mentoria + etiqueta específica
    mc_attr = (' data-mc-tags="%s" data-no-redirect="1"' % MC_TAGS.get(origem, "7215796")) if interesse_hidden else ""
    return ('<form class="lead" data-origem="%s"' + mc_attr + ' novalidate>'
            '<label for="%s-email">E-mail<input id="%s-email" name="email" type="email" placeholder="voce@exemplo.com" autocomplete="email" required></label>'
            '%s%s%s'
            '<label class="consent" for="%s-ok"><input id="%s-ok" name="consent" type="checkbox"><span>Autorizo o Mais Concursados a enviar e-mails e mensagens sobre editais, conteúdos e mentorias, conforme a <a href="privacidade.html">Política de privacidade</a>.</span></label>'
            '<button type="submit">%s</button><p class="feedback" role="status" aria-live="polite"></p></form>'
            ) % (esc(origem), fid, fid, wpp_field, interesse_field, hid, fid, fid, label_btn)

def page(path, title, desc, body, active="", jsonld=None, og_type="website", needs_data=False, extra_head=""):
    depth = path.count("/")
    root = "../" * depth
    full_title = title if title == NAME else "%s | %s" % (title, NAME)
    canon = SITE + "/" + path
    head = ['<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<title>%s</title>' % esc(full_title),
            '<meta name="description" content="%s">' % esc(desc),
            '<link rel="canonical" href="%s">' % canon,
            '<meta name="theme-color" content="#092ca8">',
            '<meta property="og:type" content="%s">' % og_type,
            '<meta property="og:title" content="%s">' % esc(full_title),
            '<meta property="og:description" content="%s">' % esc(desc),
            '<meta property="og:url" content="%s">' % canon,
            '<meta property="og:locale" content="pt_BR">',
            '<link rel="icon" type="image/png" href="%sassets/favicon.png">' % root,
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Public+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">']
    if MODE == "preview":
        head.append("<style>\n%s\n</style>" % css)
    else:
        head.append('<link rel="stylesheet" href="%sassets/style.css?v=%s">' % (root, VER))
    if jsonld:
        head.append('<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=False))
    head.append(extra_head)

    data_tag = ('<script type="application/json" id="editais-data">%s</script>' % editais_raw.replace("</", "<\\/")) if needs_data else ""
    if MODE == "preview":
        scripts = "<script>\n%s\n</script>\n<script>\n%s\n</script>" % (CONFIG_JS, js)
    else:
        scripts = '<script src="%sassets/config.js?v=%s"></script>\n<script src="%sassets/app.js?v=%s" defer></script>' % (root, VER, root, VER)

    inner = "%s\n<main id=\"conteudo\" class=\"wrap\">%s</main>\n%s\n%s\n%s" % (header(active, root), body, footer(root), data_tag, scripts)
    if MODE == "preview" and path == "index.html":
        # a página de entrada recebe o esqueleto da plataforma; sem doctype, html, head ou body próprios
        return "\n".join(head) + "\n" + inner
    return "<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n%s\n</head>\n<body data-root=\"%s\">\n%s\n</body>\n</html>\n" % ("\n".join(head), root, inner)

def write(path, content, binary=False):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as f:
        f.write(content)

def post_card(a, feature=False, root=""):
    cls = "post feature" if feature else "post"
    return ('<a class="%s" href="%sblog/%s.html" data-cat="%s"><span class="mono tag">%s</span><h3>%s</h3><p>%s</p><div class="foot"><span class="mono">%d min de leitura</span></div></a>'
            % (cls, root, a["slug"], esc(a["cat"]), esc(a["cat"]), a["title"], esc(a["excerpt"]), a["min"]))

# ---------------------------------------------------------------- páginas
def home():
    posts = "".join(post_card(a, False) for a in ARTICLES)
    areas = [("bancario", "Bancário", "BB, Caixa, BACEN e bancos estaduais"), ("fiscal", "Fiscal", "Receitas, Sefaz e tribunais de contas"),
             ("tribunais", "Tribunais", "TRT, TRF, TJ e MP"), ("policial", "Policial", "Polícias civis, militares e federais"),
             ("educacao", "Educação", "Professores e técnicos de universidades")]
    areas_html = "".join('<a class="area" href="editais.html#%s"><strong>%s</strong><span>%s</span></a>' % a for a in areas)
    body = """
<section>
 <div class="hero">
  <div>
   <p class="mono">Editais, notícias e estudo</p>
   <h1 style="margin-top:14px">Saiba qual concurso abre e como estudar para <em>passar</em>.</h1>
   <p class="lead">Acompanhe editais abertos e previstos de concursos de todas as áreas, com destaque para os bancários, e estude com o método de um professor aprovado e convocado em mais de 10 concursos.</p>
   <div class="cta-row"><a class="btn" href="editais.html">Ver editais</a><a class="btn ghost" href="mentorias.html">Conhecer a mentoria</a></div>
  </div>
  <aside class="radar" aria-label="Radar de editais">
   <div class="radar-head"><h2>Radar da semana</h2><span class="mono">conferido em 13/10</span></div>
   <ul id="radar-list"><li><div class="meta">Carregando editais...</div></li></ul>
   <p class="note">Dados conferidos em 13/10/2026. Confirme sempre no edital oficial. <a href="editais.html">Ver todos</a></p>
  </aside>
 </div>
</section>

<section class="section">
 <div class="band">
  <div>
   <p class="mono">Mentoria · Bancada</p>
   <h2 style="margin-top:10px">Bancada BACEN: estude com o Alan até o edital</h2>
   <p>Turma fechada para quem quer passar no Banco Central, com grupo privado, encontros on-line e um roteiro de estudo pronto.</p>
   <div class="cta-row"><a class="btn light" href="mentorias.html">Ver como funciona</a></div>
  </div>
  <ul><li>Grupo privado de estudos</li><li>Encontros on-line</li><li>Cursos presenciais com transmissão</li><li>Curso completo do mercado incluso</li></ul>
 </div>
</section>

<section class="section">
 <div class="section-head"><h2>Escolha sua área</h2></div>
 <div class="areas">%AREAS%</div>
</section>

<section class="section">
 <div class="section-head"><h2>Últimos artigos</h2><a class="link" href="blog.html">Ver todos os artigos</a></div>
 <div class="posts">%POSTS%</div>
</section>

<section class="capture" id="alertas">
 <div>
  <h2>Receba o edital antes de todo mundo</h2>
  <p class="sub">Alertas de novos editais e um resumo semanal de estudo, no e-mail ou no WhatsApp. Você sai quando quiser.</p>
  <p class="wpp"><a class="btn light" data-config-link="whatsappGroupUrl" data-config-show="whatsappGroupUrl" href="#" hidden>Entrar no grupo do WhatsApp</a></p>
 </div>
 %FORM%
</section>
""".replace("%AREAS%", areas_html).replace("%POSTS%", posts).replace("%FORM%", lead_form("home", fid="h"))
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": SITE + "/",
          "logo": SITE + "/assets/logo-light.png", "sameAs": [IG]}
    return page("index.html", NAME, "Editais de concursos abertos e previstos, artigos de estudo e mentoria para concursos de todas as áreas, com destaque para os bancários, com Alan Moraes.",
                body, "inicio", ld, needs_data=True)

def editais():
    body = """
<section class="page-head">
 <p class="mono">Editais</p>
 <h1 style="margin-top:10px">Concursos abertos e previstos</h1>
 <p>Filtre por situação e área. Cada linha mostra banca, vagas, remuneração, prazo e as fontes consultadas.</p>
</section>
<p class="note" style="margin-top:20px">Dados conferidos em <span id="ed-updated">13/10/2026</span> no texto dos editais e em outras fontes. Confirme sempre no edital oficial da banca antes de se inscrever.</p>
<div class="filters">
 <div class="chips" id="f-status" role="group" aria-label="Situação"></div>
 <label class="search"><span class="mono" style="display:none">Buscar</span><input id="f-q" type="search" placeholder="Buscar órgão ou cargo" aria-label="Buscar órgão ou cargo" style="border:0;background:transparent;width:100%;outline-offset:4px"></label>
</div>
<div class="chips" id="f-area" role="group" aria-label="Área" style="margin-top:12px"></div>
<div class="table-wrap">
 <table>
  <thead><tr><th>Órgão / cargo</th><th>Situação</th><th>Banca</th><th>Vagas</th><th>Salário</th><th>Inscrições até / previsão</th><th>Fontes</th></tr></thead>
  <tbody id="ed-body"></tbody>
 </table>
 <div class="empty" id="ed-empty" hidden>Nenhum concurso encontrado com esses filtros.</div>
</div>
<section class="capture" id="alertas">
 <div><h2>Avisamos quando o edital sair</h2><p class="sub">Cadastre seu e-mail e diga o concurso que você acompanha.</p>
 <p class="wpp"><a class="btn light" data-config-link="whatsappGroupUrl" data-config-show="whatsappGroupUrl" href="#" hidden>Entrar no grupo do WhatsApp</a></p></div>
 %FORM%
</section>
""".replace("%FORM%", lead_form("editais", fid="e"))
    return page("editais.html", "Editais de concursos abertos e previstos", "Lista de concursos abertos e previstos com banca, vagas, salário, prazos e fontes. Concursos de todas as áreas, com destaque para bancários, fiscais, tribunais, policiais e educação.", body, "editais", needs_data=True)

def blog():
    cats = ["Todos"] + sorted({a["cat"] for a in ARTICLES})
    chips = "".join('<button type="button" class="chip" data-cat="%s" aria-pressed="%s">%s</button>' % (esc(c), "true" if c == "Todos" else "false", esc(c)) for c in cats)
    posts = "".join(post_card(a, a.get("feature", False)) for a in ARTICLES)
    body = """
<section class="page-head"><p class="mono">Blog</p><h1 style="margin-top:10px">Estude com estratégia</h1>
<p>Método, rotina e conteúdo para concursos de todas as áreas, com destaque para os bancários, escritos por quem já passou por isso.</p></section>
<div class="chips" id="b-cats" role="group" aria-label="Categoria" style="margin-top:24px">%CHIPS%</div>
<div class="posts" id="b-posts" style="margin-top:24px">%POSTS%</div>
<p class="empty" id="b-empty" hidden>Ainda não há artigos nesta categoria.</p>
""".replace("%CHIPS%", chips).replace("%POSTS%", posts)
    return page("blog.html", "Blog de estudo para concursos", "Artigos sobre método de estudo, cronograma e conteúdo para concursos de todas as áreas, com destaque para os bancários, por Alan Moraes.", body, "blog")

def article(a):
    others = [x for x in ARTICLES if x["slug"] != a["slug"]]
    more = "".join(post_card(x, False, "../").replace('href="../blog/', 'href="') for x in others)
    body = """
<article class="narrow">
 <header class="article-head">
  <span class="mono">%CAT% · %MIN% min de leitura</span>
  <h1>%TITLE%</h1>
  <p class="byline">Por Alan Moraes · %DATE%</p>
 </header>
 <div class="prose">%BODY%</div>
 <div class="callout">
  <h3>Quer estudar com acompanhamento?</h3>
  <p>A Bancada BACEN é uma turma fechada com grupo privado, encontros on-line e roteiro de estudo. Entre na lista de espera.</p>
  <a class="btn light" href="../mentorias.html">Conhecer a mentoria</a>
 </div>
 <aside class="author"><div class="avatar"><img src="../assets/alan-avatar.jpg" width="240" height="240" alt="Alan Moraes" loading="lazy"></div>
  <p><strong>Alan Moraes</strong> é bancário, professor e mentor para concursos. Foi aprovado e convocado em mais de 10 concursos, 6 deles bancários, e já ajudou mais de 400 alunos a virar concursados. <a href="../sobre.html">Conheça a história</a>.</p></aside>
</article>
<section class="section"><div class="section-head"><h2>Continue lendo</h2></div><div class="posts">%MORE%</div></section>
""".replace("%CAT%", esc(a["cat"])).replace("%MIN%", str(a["min"])).replace("%TITLE%", a["title"]) \
   .replace("%DATE%", "/".join(reversed(a["date"].split("-")))).replace("%BODY%", a["body"]).replace("%MORE%", more)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": html.unescape(a["title"]), "description": a["desc"],
          "datePublished": a["date"], "dateModified": a["date"],
          "author": {"@type": "Person", "name": "Alan Moraes", "url": SITE + "/sobre.html"},
          "publisher": {"@type": "Organization", "name": NAME, "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo-light.png"}},
          "mainEntityOfPage": SITE + "/blog/" + a["slug"] + ".html", "inLanguage": "pt-BR"}
    return page("blog/%s.html" % a["slug"], html.unescape(a["title"]), a["desc"], body, "blog", ld, og_type="article")

def mentorias():
    feats = [("Grupo privado", "Um espaço fechado para a turma, com troca entre alunos e acompanhamento do Alan."),
             ("Encontros on-line", "Encontros regulares ao vivo para tirar dúvidas, alinhar o roteiro e manter o ritmo."),
             ("Cursos presenciais com transmissão", "Os cursos presenciais da turma também são transmitidos."),
             ("Curso completo do mercado incluso", "Você recebe um curso completo, sem precisar contratar à parte."),
             ("Aulas gravadas organizadas", "Aulas gravadas em uma plataforma própria, com materiais e funcionalidades explicados desde o início."),
             ("Roteiro de estudo semanal", "Um roteiro pronto, pensado para 10 a 15 horas de estudo por semana.")]
    feats_html = "".join('<div class="feat"><h3>%s</h3><p>%s</p></div>' % f for f in feats)
    faqs = [("Como eu entro na turma?", "Entre na lista de espera nesta página. Quando a turma abrir, você recebe as informações de inscrição antes de todo mundo."),
            ("Quanto custa e quando começa?", "Valores e datas são enviados para quem está na lista de espera, no momento da abertura da turma."),
            ("Preciso estudar quantas horas por semana?", "O roteiro foi pensado para 10 a 15 horas semanais. Se você tem menos tempo, vale conversar antes de entrar para ajustar a expectativa."),
            ("A mentoria garante aprovação?", "Não. Nenhuma mentoria pode garantir aprovação. A Bancada oferece método, rotina, acompanhamento e conteúdo; o resultado depende também da sua dedicação."),
            ("Já saiu o edital do BACEN?", "Acompanhe a situação na <a href=\"editais.html#bancario\">página de editais</a>, que reúne as informações mais recentes e as fontes."),
            ("Haverá turmas para outros concursos?", "Bancada é a marca das turmas do Alan. Novos concursos e novas turmas serão anunciados aqui e para quem está na lista.")]
    faq_html = "".join('<details class="faq"><summary>%s</summary><p>%s</p></details>' % f for f in faqs)
    body = """
<section class="page-head">
 <p class="mono">Mentoria · Bancada</p>
 <h1 style="margin-top:10px">Bancada BACEN: a turma fechada para passar no Banco Central</h1>
 <p class="lead">Grupo privado, encontros on-line e um roteiro de estudo montado por quem foi aprovado e convocado em mais de 10 concursos.</p>
 <div class="cta-row">
  <a class="btn" data-config-link="checkoutBancadaUrl" data-config-show="checkoutBancadaUrl" href="#" hidden>Quero entrar na Bancada</a>
  <a class="btn" data-config-hide="checkoutBancadaUrl" href="#lista">Entrar na lista de espera</a>
  <a class="btn ghost" href="#como-funciona">Ver como funciona</a>
 </div>
</section>

<section class="section"><div class="two">
 <div>
  <h2>Para quem é</h2>
  <p style="margin-top:12px;color:var(--muted)">Para quem quer o Banco Central e não quer estudar sozinho. Você ganha um grupo, um roteiro e alguém que acompanha a sua evolução até o edital e depois dele.</p>
  <ul style="margin:16px 0 0;padding-left:1.2em;display:grid;gap:8px">
   <li>Quem já estuda e perde tempo sem direção.</li>
   <li>Quem trabalha e precisa de rotina realista.</li>
   <li>Quem aprende melhor em grupo e com prazos.</li>
  </ul>
 </div>
 <div>
  <h2>Em resumo</h2>
  <div class="facts">
   <div class="fact"><span>Concurso-alvo</span><span>Banco Central do Brasil</span></div>
   <div class="fact"><span>Formato</span><span>Turma fechada</span></div>
   <div class="fact"><span>Encontros</span><span>On-line</span></div>
   <div class="fact"><span>Dedicação do roteiro</span><span>10 a 15 h por semana</span></div>
   <div class="fact"><span>Valores e início</span><span>Enviados à lista de espera</span></div>
  </div>
 </div>
</div></section>

<section class="section"><div class="section-head"><h2>O que você recebe</h2></div><div class="grid3">%FEATS%</div></section>

<section class="section" id="como-funciona"><div class="section-head"><h2>Como começa</h2></div>
 <ol class="steps">
  <li><div><strong>Aula 0: boas-vindas</strong><span>Você entende como a turma funciona e o que esperar das primeiras semanas.</span></div></li>
  <li><div><strong>Aulas de metodologia</strong><span>A forma de estudar da escola e da Bancada, antes de entrar na matéria.</span></div></li>
  <li><div><strong>Como usar a plataforma</strong><span>Onde achar as aulas, os materiais e as funcionalidades.</span></div></li>
  <li><div><strong>Rotina da turma</strong><span>Roteiro semanal, encontros on-line e grupo privado.</span></div></li>
 </ol>
</section>

<section class="section"><div class="two">
 <div><h2>Quem conduz</h2>
  <div class="author" style="margin-top:16px"><div class="avatar"><img src="assets/alan-avatar.jpg" width="240" height="240" alt="Alan Moraes" loading="lazy"></div><p><strong>Alan Moraes</strong><br>Bancário, professor e mentor para concursos</p></div>
  <p style="margin-top:12px;color:var(--muted)">Alan Moraes é bancário, professor e mentor para concursos. Foi aprovado e convocado em mais de 10 concursos, 6 deles bancários (2x Banpará, 1x Basa, 2x BB e 1x Caixa), e já ajudou mais de 400 alunos a virar concursados.</p>
  <p style="margin-top:12px"><a class="link" href="sobre.html">Ler a história completa</a></p></div>
 <div class="card-form" id="lista">
  <h2 style="font-size:1.5rem">Entrar na lista de espera</h2>
  <p style="margin:10px 0 18px;color:var(--muted)">Você recebe o aviso de abertura da turma antes de todo mundo.</p>
  %FORM%
  <p style="margin-top:14px"><a class="btn ghost" data-config-link="whatsappGroupUrl" data-config-show="whatsappGroupUrl" href="#" hidden>Entrar no grupo do WhatsApp</a></p>
 </div>
</div></section>

<section class="section"><div class="section-head"><h2>Perguntas frequentes</h2></div>%FAQ%</section>
""".replace("%FEATS%", feats_html).replace("%FAQ%", faq_html).replace("%FORM%", lead_form("mentoria-bancada-bacen", "Bancada BACEN", True, "Entrar na lista de espera", fid="m"))
    ld = {"@context": "https://schema.org", "@type": "Course", "name": "Bancada BACEN", "description": "Turma fechada de mentoria para o concurso do Banco Central, com grupo privado, encontros on-line e roteiro de estudo.",
          "provider": {"@type": "Person", "name": "Alan Moraes", "url": SITE + "/sobre.html"}}
    return page("mentorias.html", "Mentoria Bancada BACEN", "Turma fechada para o concurso do Banco Central com grupo privado, encontros on-line, roteiro de estudo e curso completo incluso. Entre na lista de espera.", body, "mentorias", ld)

COURSES = [
 {"cat": "Mentoria · Banco Central", "title": "Bancada BACEN", "teacher": "Alan Moraes",
  "desc": "Eu estudo para Auditor do BACEN e você estuda comigo: trilha de 20 semanas, meta diária, check-in, aulas por matéria, simulados com correção comentada e encontros.",
  "waitlist": "mentorias.html#lista", "checkout": "https://pay.herospark.com/bancada-bacen-546000"},
 {"cat": "Curso · Conhecimentos bancários", "title": "Arrebenta com essa Prova! Conhecimentos Bancários", "teacher": "Alan Moraes",
  "desc": "Teoria completa de Sistema Financeiro Nacional, mercados, produtos bancários e legislação bancária, em linguagem direta e com a experiência de quem trabalha no mercado.",
  "price": "R$ 49,90", "old": "R$ 100,00", "inst": "pagamento em 1x",
  "url": "https://pay.herospark.com/arrebenta-com-essa-prova-conhecimentos-bancarios-com-professor-alan-moraes-435477"},
 {"cat": "Mentoria · Banco do Brasil", "title": "Programa de Mentoria Você Bancário: Banco do Brasil", "teacher": "Alan Moraes",
  "desc": "Mentoria de três meses com encontro individual, encontros semanais em grupo, cronograma, banco de questões e acompanhamento emocional.",
  "waitlist": "#lista-bb", "checkout": "https://pay.herospark.com/mentoria-bb-2025-oferta-sem-gg-406086"},
 {"cat": "Curso · Informática", "title": "Informática para Concursos: domine todos os tópicos", "teacher": "Gilson Fernandes",
  "desc": "Hardware, Windows, Word, Excel, LibreOffice, Linux, redes e segurança da informação, com explicações técnicas e questões reais de concursos.",
  "price": "R$ 19,90", "old": "R$ 39,90", "inst": "ou 11x de R$ 2,20",
  "url": "https://pay.herospark.com/informatica-para-concursos-com-gilson-fernandes-394940"},
 {"cat": "Curso · Inglês", "title": "Meus Melhores! Questões de Inglês Cesgranrio", "teacher": "Gil Mattos",
  "desc": "40 aulas com questões reais da Cesgranrio: compreensão de textos, vocabulário bancário, morfologia, pronomes, conjunções e verbos modais.",
  "price": "R$ 19,90", "old": "", "inst": "ou 12x de R$ 2,05",
  "url": "https://pay.herospark.com/meus-melhores-questoes-de-ingles-cesgranrio-com-professor-gil-mattos-524765"},
 {"cat": "Curso · Vendas e negociação", "title": "Vamos Lá, Jogador(a)! Questões de Vendas e Negociação", "teacher": "Ana Furtado",
  "desc": "Estratégia empresarial, segmentação, experiência do cliente, técnicas de vendas, marketing digital e canais remotos, sempre conectados a questões de prova.",
  "price": "R$ 29,90", "old": "", "inst": "ou 12x de R$ 3,10",
  "url": "https://pay.herospark.com/vamos-la-jogador-a-questoes-de-vendas-e-negociacao-com-ana-furtado-523305"},
]

def cursos():
    cards = ""
    for c in COURSES:
        who = '<p class="by">Com %s</p>' % esc(c["teacher"]) if c["teacher"] else ""
        if c.get("waitlist"):
            buy = ('<div class="buy"><p class="price"><small>Turma em preparação. Entre na lista de espera e receba o aviso da abertura.</small></p>'
                   '<a class="btn" href="%s">Entrar na lista de espera</a></div>') % esc(c["waitlist"])
        else:
            old = '<s>%s</s> ' % esc(c["old"]) if c["old"] else ""
            buy = ('<div class="buy"><p class="price"><span class="old">%s</span><strong>%s</strong> <small>%s</small></p>'
                   '<a class="btn" href="%s" rel="noopener">Quero este curso</a></div>') % (old, esc(c["price"]), esc(c["inst"]), esc(c["url"]))
        cards += '<article class="course"><p class="mono">%s</p><h2>%s</h2>%s<p>%s</p>%s</article>' % (
                  esc(c["cat"]), esc(c["title"]), who, esc(c["desc"]), buy)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Cursos Mais Concursados",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["title"], "url": c.get("url") or SITE + "/cursos.html"} for i, c in enumerate(COURSES)]}
    body = """
<section class="page-head">
 <p class="mono">Cursos</p>
 <h1 style="margin-top:10px">Cursos e mentorias para concursos</h1>
 <p>Conteúdo para estudar com método, com aulas gravadas, questões e acompanhamento. A compra é feita em ambiente seguro da HeroSpark e o acesso é liberado depois do pagamento.</p>
</section>
<div class="courses">%CARDS%</div>
<p class="note" style="margin-top:24px">Valores conferidos em 13/10/2026. O valor final e as condições de pagamento aparecem no checkout. Nenhum curso garante aprovação: o resultado depende também da sua dedicação.</p>
<section class="capture" id="lista-bb">
 <div><h2>Lista de espera: Mentoria Você Bancário (Banco do Brasil)</h2><p class="sub">Deixe seu e-mail e seu WhatsApp para ser avisado quando a próxima turma abrir.</p></div>
 %FORMBB%
</section>
<section class="capture" id="alertas">
 <div><h2>Quer saber de novos cursos?</h2><p class="sub">Cadastre seu e-mail para receber avisos de editais e lançamentos.</p></div>
 %FORM%
</section>
""".replace("%CARDS%", cards).replace("%FORMBB%", lead_form("mentoria-bb", "Mentoria Você Bancário (BB)", True, "Entrar na lista de espera", fid="b")).replace("%FORM%", lead_form("cursos", fid="c"))
    return page("cursos.html", "Cursos e mentorias para concursos", "Cursos e mentorias para concursos de todas as áreas, com destaque para os bancários: Conhecimentos Bancários, Informática, Inglês, Vendas e a Bancada BACEN.", body, "cursos", ld)


def sobre():
    body = """
<article class="narrow">
 <header class="article-head"><span class="mono">Sobre</span><h1>Alan Moraes</h1>
 <p class="byline">Bancário, professor e mentor para concursos</p></header>
 <figure class="portrait"><img src="assets/alan.jpg" width="640" height="800" alt="Alan Moraes, bancário, professor e mentor para concursos"></figure>
 <div class="prose">
  <p>Sou Alan Moraes, bancário, professor e mentor para concursos. Fui aprovado e convocado em mais de 10 concursos, 6 deles bancários: 2 vezes no Banpará, 1 no Basa, 2 no Banco do Brasil e 1 na Caixa.</p>
  <p>Já ajudei a transformar mais de 400 alunos em concursados. O Mais Concursados nasceu para reunir em um lugar só o que eu gostaria de ter tido quando comecei: editais organizados, método de estudo claro e orientação de quem já passou pelo processo.</p>
  <h2>Em números</h2>
  <div class="grid3" style="margin-top:12px">
   <div class="feat"><h3>10+</h3><p>concursos com aprovação e convocação</p></div>
   <div class="feat"><h3>6</h3><p>deles bancários: Banpará (2x), Basa, BB (2x) e Caixa</p></div>
   <div class="feat"><h3>400+</h3><p>alunos transformados em concursados</p></div>
  </div>
  <h2>O que você encontra aqui</h2>
  <ul>
   <li>Um painel de editais abertos e previstos, com as fontes de cada informação.</li>
   <li>Artigos sobre método, rotina e conteúdo para concursos de todas as áreas, com destaque para os bancários.</li>
   <li>A mentoria Bancada, turmas fechadas para quem quer estudar com acompanhamento.</li>
  </ul>
  <p>Você também me encontra no Instagram, em <a href="%IG%" target="_blank" rel="noopener">@prof.alanmoraes</a>.</p>
 </div>
 <div class="callout"><h3>Quer estudar comigo?</h3><p>Conheça a turma Bancada BACEN e entre na lista de espera.</p><a class="btn light" href="mentorias.html">Ver a mentoria</a></div>
</article>
""".replace("%IG%", IG)
    ld = {"@context": "https://schema.org", "@type": "Person", "name": "Alan Moraes", "jobTitle": "Professor e mentor para concursos", "url": SITE + "/sobre.html", "sameAs": [IG]}
    return page("sobre.html", "Sobre Alan Moraes", "Alan Moraes é bancário, professor e mentor para concursos, aprovado e convocado em mais de 10 concursos, 6 deles bancários.", body, "sobre", ld, og_type="profile")

def contato():
    body = """
<article class="narrow">
 <header class="article-head"><span class="mono">Contato</span><h1>Fale com a gente</h1></header>
 <div class="prose">
  <p>O canal mais rápido para falar com o Alan é o Instagram. Chame no direct em <a href="%IG%" target="_blank" rel="noopener">@prof.alanmoraes</a>.</p>
  <p data-config-show="contactEmail" hidden>Por e-mail: <strong id="contact-email"></strong></p>
  <p>Para receber avisos de editais e de abertura de turmas, use o formulário de alertas da <a href="index.html#alertas">página inicial</a>.</p>
  <p>Encontrou um erro em algum edital? Avise pelo Instagram, com o link da fonte oficial, e corrigimos.</p>
 </div>
</article>
""".replace("%IG%", IG)
    return page("contato.html", "Contato", "Fale com o Alan Moraes pelo Instagram @prof.alanmoraes ou receba alertas de editais por e-mail.", body, "")

def grupo():
    body = """
<article class="narrow" style="text-align:center">
 <header class="article-head"><span class="mono">Cadastro recebido</span><h1>Falta só um passo: entre no grupo</h1></header>
 <div class="prose">
  <p>Obrigado! Seu cadastro foi enviado. Agora entre no grupo do WhatsApp do Mais Concursados para receber os avisos de editais primeiro.</p>
  <p style="margin-top:28px"><a class="btn" data-config-link="whatsappGroupUrl" data-config-show="whatsappGroupUrl" href="#" hidden style="font-size:1.1rem;padding:16px 28px">Entrar no grupo do WhatsApp</a></p>
  <p class="note">Também enviamos uma mensagem de confirmação para o seu e-mail. Clique no link dela para ativar os alertas por e-mail (veja a caixa de spam se não encontrar).</p>
  <p><a href="index.html">Voltar para o início</a></p>
 </div>
</article>
"""
    return page("entrar-no-grupo.html", "Entre no grupo do WhatsApp", "Entre no grupo do WhatsApp do Mais Concursados e receba os alertas de editais.", body, "", extra_head='<meta name="robots" content="noindex, follow">')

def privacidade():
    body = """
<article class="narrow">
 <header class="article-head"><span class="mono">Atualizada em 06/10/2026</span><h1>Política de privacidade</h1></header>
 <div class="prose">
  <p>Esta política explica como o site maisconcursados.com.br trata dados pessoais, de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).</p>
  <h2>Quem é o responsável</h2>
  <p>O responsável pelo tratamento dos dados é o Mais Concursados, representado por Alan Moraes. O contato é feito pelo Instagram <a href="%IG%" target="_blank" rel="noopener">@prof.alanmoraes</a>.</p>
  <h2>Quais dados coletamos</h2>
  <ul>
   <li>E-mail, número de WhatsApp (opcional) e concurso de interesse, quando você preenche um formulário.</li>
   <li>Dados de navegação, como páginas visitadas e tipo de dispositivo, se uma ferramenta de estatísticas estiver ativa.</li>
  </ul>
  <h2>Para que usamos</h2>
  <ul>
   <li>Enviar alertas de editais, conteúdos de estudo e avisos sobre mentorias e cursos.</li>
   <li>Avisar sobre a abertura de turmas para quem entrou em uma lista de espera.</li>
   <li>Entender o uso do site para melhorá-lo.</li>
  </ul>
  <h2>Base legal</h2>
  <p>O tratamento dos dados enviados por formulário se baseia no seu consentimento, dado ao marcar a caixa de autorização. Você pode retirar o consentimento a qualquer momento.</p>
  <h2>Com quem compartilhamos</h2>
  <p>Os dados podem ser processados por serviços que usamos para enviar e-mails e mensagens, hospedar o site e medir acessos. Não vendemos seus dados.</p>
  <h2>Por quanto tempo guardamos</h2>
  <p>Mantemos seus dados enquanto você estiver na lista ou até pedir a exclusão.</p>
  <h2>Seus direitos</h2>
  <p>Você pode pedir acesso, correção, exclusão, portabilidade e informações sobre o tratamento dos seus dados, e cancelar o recebimento de mensagens a qualquer momento. Faça o pedido pelo Instagram indicado acima.</p>
  <h2>Cookies</h2>
  <p>O site pode usar cookies de ferramentas de estatística. Você pode bloquear cookies nas configurações do navegador.</p>
  <h2>Alterações</h2>
  <p>Podemos atualizar esta política. A data de atualização fica no topo da página.</p>
 </div>
</article>
""".replace("%IG%", IG)
    return page("privacidade.html", "Política de privacidade", "Como o Mais Concursados coleta, usa e protege dados pessoais, conforme a LGPD.", body, "")

def notfound():
    body = """<section class="narrow" style="text-align:center;padding-block:48px"><p class="mono">Erro 404</p><h1 style="margin-top:10px;font-size:2.4rem">Página não encontrada</h1>
<p class="lead" style="margin-inline:auto">O endereço pode ter mudado. Volte para o início ou veja os editais.</p>
<div class="cta-row" style="justify-content:center"><a class="btn" href="/index.html">Ir para o início</a><a class="btn ghost" href="/editais.html">Ver editais</a></div></section>"""
    return page("404.html", "Página não encontrada", "Página não encontrada.", body, "")

# ---------------------------------------------------------------- saída
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

pages = [("index.html", home()), ("editais.html", editais()), ("blog.html", blog()), ("mentorias.html", mentorias()), ("cursos.html", cursos()),
         ("sobre.html", sobre()), ("contato.html", contato()), ("privacidade.html", privacidade()), ("entrar-no-grupo.html", grupo())]
for a in ARTICLES:
    pages.append(("blog/%s.html" % a["slug"], article(a)))
if MODE != "preview":
    pages.append(("404.html", notfound()))
for p, c in pages:
    write(p, c)

os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
for f in ("logo-light.png", "logo-dark.png", "favicon.png", "alan.jpg", "alan-avatar.jpg"):
    shutil.copy(os.path.join(BASE, "assets", f), os.path.join(OUT, "assets", f))
write("data/editais.json", editais_raw)
stat = os.path.join(BASE, "static")
if MODE != "preview" and os.path.isdir(stat):
    for f in os.listdir(stat):
        shutil.copy(os.path.join(stat, f), os.path.join(OUT, f))

if MODE != "preview":
    write("assets/style.css", css)
    write("assets/app.js", js)
    write("assets/config.js", CONFIG_JS)
    urls = ["index.html", "editais.html", "cursos.html", "blog.html", "mentorias.html", "sobre.html", "contato.html", "privacidade.html"] + ["blog/%s.html" % a["slug"] for a in ARTICLES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        "  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>\n" % (SITE, u, TODAY) for u in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE)
    write(".htaccess", """# Mais Concursados - HostGator (Apache)
# Força HTTPS (ative o SSL gratuito no cPanel antes de publicar)
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

ErrorDocument 404 /404.html

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType application/json "access plus 1 hour"
  ExpiresByType text/html "access plus 0 seconds"
</IfModule>
AddDefaultCharset UTF-8
<IfModule mod_headers.c>
  <FilesMatch "\.html$">
    Header set Cache-Control "no-cache, must-revalidate"
  </FilesMatch>
</IfModule>
""")
print("ok", OUT, len(pages), "paginas")
