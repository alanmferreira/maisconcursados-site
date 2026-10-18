# -*- coding: utf-8 -*-
"""Gera a arte de Stories (1080x1920) do resumo diário.
Uso: python3 src/story.py [story.json]   (padrão: story.json na raiz)
Entrada (JSON):
{ "data": "17/10", "titulo": "Giro dos Concursos",
  "itens": [ {"tag": "ENCERRA HOJE", "tom": "warn|good|info", "titulo": "Seduc-CE (Professor)", "detalhe": "Inscrições até 23h59"} ] }   (1 a 4 itens)
Saída: stories/AAAA-MM-DD.png e stories/ultimo.png
"""
import os, sys, json, html, base64, datetime
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "story.json")
d = json.load(open(src, encoding="utf-8"))
itens = d["itens"][:4]
b64 = lambda p: base64.b64encode(open(os.path.join(BASE, "assets", p), "rb").read()).decode()
logo = b64("logo-dark.png")
TONS = {"warn": ("#f0b060", "#3a2a12"), "good": ("#46c593", "#12352b"), "info": ("#6f8cff", "#18265a")}

cards = ""
for it in itens:
    c, bg = TONS.get(it.get("tom", "info"), TONS["info"])
    cards += """<div class="card" style="border-color:%s55"><span class="tag" style="color:%s;background:%s">%s</span>
    <h2>%s</h2><p>%s</p></div>""" % (c, c, bg, html.escape(it.get("tag", "")), html.escape(it["titulo"]), html.escape(it.get("detalhe", "")))

n = len(itens)
size = {1: 88, 2: 76, 3: 64, 4: 54}[n]
page = """<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1920px;background:radial-gradient(900px 700px at 85% 8%,#1a2a6c 0%,transparent 70%),#0a0e1c;color:#e8ecf8;font-family:Inter,'Segoe UI',sans-serif;position:relative;overflow:hidden}
.wrap{position:absolute;left:72px;right:72px;top:250px;bottom:260px;display:flex;flex-direction:column}
.kicker{font-family:'DejaVu Sans Mono',monospace;font-size:28px;letter-spacing:.14em;text-transform:uppercase;color:#98a2c0}
h1{font-size:92px;line-height:1.02;font-weight:800;letter-spacing:-.02em;margin:18px 0 8px}
h1 span{color:#6f8cff}
.date{font-size:40px;color:#98a2c0;font-weight:600;margin-bottom:40px}
.cards{display:flex;flex-direction:column;gap:26px;flex:1}
.card{flex:1;display:flex;flex-direction:column;justify-content:center;background:#111833;border:2px solid;border-radius:32px;padding:34px 38px}
.tag{align-self:flex-start;display:inline-block;font-family:'DejaVu Sans Mono',monospace;font-size:24px;letter-spacing:.08em;font-weight:700;padding:6px 16px;border-radius:999px;margin-bottom:16px}
.card h2{font-size:@H2@px;line-height:1.1;font-weight:800;letter-spacing:-.01em}
.card p{font-size:@P@px;color:#b4bddb;margin-top:12px;line-height:1.3}
.foot{position:absolute;left:72px;right:72px;bottom:90px;display:flex;align-items:center;justify-content:space-between}
.foot img{height:70px}
.foot .site{font-size:34px;font-weight:700;text-align:right}
.foot .site small{display:block;font-size:26px;color:#98a2c0;font-weight:500;margin-top:4px}
</style></head><body>
<div class="wrap"><div class="kicker">Mais Concursados</div>
<h1>@T@</h1><div class="date">@D@</div><div class="cards">@C@</div></div>
<div class="foot"><img src="data:image/png;base64,@L@"><div class="site">maisconcursados.com.br<small>@prof.alanmoraes</small></div></div>
</body></html>"""
for k, v in {"@H2@": str(size), "@P@": str(int(size * .55)), "@T@": html.escape(d.get("titulo", "Giro dos Concursos")).replace("Concursos", "<span>Concursos</span>"), "@D@": html.escape(d["data"]), "@C@": cards, "@L@": logo}.items():
    page = page.replace(k, v)

os.makedirs(os.path.join(BASE, "stories"), exist_ok=True)
hoje = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)).strftime("%Y-%m-%d")
out = os.path.join(BASE, "stories", hoje + ".png")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--no-sandbox"]) if os.path.exists("/opt/pw-browsers/chromium") else p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(page, wait_until="load")
    pg.screenshot(path=out)
    b.close()
import shutil; shutil.copy(out, os.path.join(BASE, "stories", "ultimo.png"))
print("ok", out)
