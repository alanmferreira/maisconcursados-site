(function () {
  "use strict";
  var CFG = window.MC_CONFIG || {};
  var ROOT = document.body.getAttribute("data-root") || "";

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function fmtDate(d) { if (!d) return ""; var p = d.split("-"); return p[2] + "/" + p[1] + "/" + p[0]; }
  function today() { var n = new Date(); return new Date(n.getFullYear(), n.getMonth(), n.getDate()); }
  function daysLeft(d) { var p = d.split("-"); return Math.round((new Date(+p[0], +p[1] - 1, +p[2]) - today()) / 86400000); }

  /* ---------- configuração (links, WhatsApp, checkout) ---------- */
  document.querySelectorAll("[data-config-link]").forEach(function (a) {
    var v = CFG[a.getAttribute("data-config-link")];
    if (v) { a.setAttribute("href", v); a.setAttribute("rel", "noopener"); if (/^https?:/.test(v)) a.setAttribute("target", "_blank"); }
  });
  document.querySelectorAll("[data-config-show]").forEach(function (el) { el.hidden = !CFG[el.getAttribute("data-config-show")]; });
  document.querySelectorAll("[data-config-hide]").forEach(function (el) { el.hidden = !!CFG[el.getAttribute("data-config-hide")]; });

  var ce = document.getElementById("contact-email");
  if (ce && CFG.contactEmail) ce.textContent = CFG.contactEmail;

  if (CFG.analyticsId &&/^G-[A-Z0-9]+$/.test(CFG.analyticsId)) {
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + CFG.analyticsId;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date()); window.gtag("config", CFG.analyticsId);
  }

  /* ---------- formulários de captação ---------- */
  document.querySelectorAll("form.lead").forEach(function (form) {
    var fb = form.querySelector(".feedback");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = (form.elements.email.value || "").trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { fb.textContent = "Digite um e-mail válido, como nome@exemplo.com."; form.elements.email.focus(); return; }
      if (form.elements.consent && !form.elements.consent.checked) { fb.textContent = "Marque a autorização para receber os contatos."; return; }
      var payload = {
        email: email,
        whatsapp: form.elements.whatsapp ? form.elements.whatsapp.value.trim() : "",
        interesse: form.elements.interesse ? form.elements.interesse.value.trim() : "",
        origem: form.getAttribute("data-origem") || location.pathname,
        consentimento: true,
        data: new Date().toISOString()
      };
      if (CFG.mailchimpAction) {
        fb.textContent = "Enviando...";
        var tid = "mc-target-" + Date.now();
        var ifr = document.createElement("iframe");
        ifr.name = tid; ifr.style.display = "none"; ifr.setAttribute("aria-hidden", "true"); ifr.tabIndex = -1;
        var f = document.createElement("form");
        f.method = "POST"; f.action = CFG.mailchimpAction; f.target = tid; f.style.display = "none";
        function add(n, v) { var i = document.createElement("input"); i.type = "hidden"; i.name = n; i.value = v; f.appendChild(i); }
        add("EMAIL", payload.email);
        if (payload.whatsapp) add("PHONE", payload.whatsapp);
        if (form.getAttribute("data-mc-tags")) add("tags", form.getAttribute("data-mc-tags"));
        if (CFG.mailchimpHoneypot) add(CFG.mailchimpHoneypot, "");
        var loaded = false;
        ifr.addEventListener("load", function () {
          if (!loaded) return;
          form.reset();
          if (CFG.whatsappGroupUrl && !form.hasAttribute("data-no-redirect")) {
            fb.textContent = "Cadastro enviado! Abrindo a página do grupo do WhatsApp...";
            setTimeout(function () { location.href = ROOT + "entrar-no-grupo.html"; }, 600);
            return;
          }
          fb.textContent = form.hasAttribute("data-no-redirect") ? "Pronto! Enviamos uma mensagem de confirmação para o seu e-mail. Confirme para entrar na lista de espera (veja também o spam)." : "Quase lá! Enviamos uma mensagem de confirmação para o seu e-mail. Confirme para entrar na lista (veja também o spam).";
          if (!CFG.whatsappGroupUrl || form.hasAttribute("data-no-redirect")) setTimeout(function () { ifr.remove(); f.remove(); }, 15000);
        });
        document.body.appendChild(ifr); document.body.appendChild(f);
        loaded = true; f.submit();
        return;
      }
      if (!CFG.leadsEndpoint) { fb.textContent = "O cadastro ainda não está ativo neste site. Fale com o Alan pelo Instagram @prof.alanmoraes."; return; }
      fb.textContent = "Enviando...";
      fetch(CFG.leadsEndpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); fb.textContent = "Pronto! Você está na lista."; form.reset(); })
        .catch(function () { fb.textContent = "Não foi possível enviar agora. Tente novamente em instantes."; });
    });
  });

  /* ---------- dados dos editais ---------- */
  function loadEditais(cb) {
    function fallback() {
      var el = document.getElementById("editais-data");
      try { cb(JSON.parse(el.textContent)); } catch (e) { cb({ editais: [] }); }
    }
    if (!window.fetch) return fallback();
    fetch(ROOT + "data/editais.json", { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(cb).catch(fallback);
  }

  function enrich(list) {
    return list.map(function (e) {
      var o = {}; for (var k in e) o[k] = e[k];
      if (e.status !== "previsto" && e.inscricoesAte) {
        var d = daysLeft(e.inscricoesAte);
        o.dias = d;
        o.st = d < 0 ? "encerrado" : (d <= 7 ? "encerrando" : "aberto");
      } else { o.st = e.status; }
      return o;
    });
  }

  var AREAS = { bancario: "Bancário", fiscal: "Fiscal", tribunais: "Tribunais", policial: "Policial", educacao: "Educação", saude: "Saúde", outros: "Outras áreas" };
  var STLABEL = { aberto: "Aberto", encerrando: "Encerrando", previsto: "Previsto" };

  function vagas(e) { return e.vagasTexto || (e.vagas != null ? Number(e.vagas).toLocaleString("pt-BR") : "A definir"); }

  /* radar da home */
  var radar = document.getElementById("radar-list");
  if (radar) {
    loadEditais(function (data) {
      var all = enrich(data.editais).filter(function (e) { return e.st !== "encerrado"; });
      var abertos = all.filter(function (e) { return e.st === "aberto" || e.st === "encerrando"; }).sort(function (a, b) { return a.dias - b.dias; });
      var open = abertos.slice(0, 1);
      abertos.filter(function (e) { return e.destaque && open.indexOf(e) < 0; }).slice(0, 2).forEach(function (e) { open.push(e); });
      abertos.forEach(function (e) { if (open.length < 3 && open.indexOf(e) < 0) open.push(e); });
      var prev = all.filter(function (e) { return e.st === "previsto" && e.destaque; }).slice(0, 4 - open.length);
      var items = open.concat(prev);
      radar.innerHTML = items.map(function (e) {
        var right = e.st === "previsto"
          ? '<div class="days"><span class="pill previsto">Previsto</span></div>'
          : '<div class="days">' + e.dias + '<small>' + (e.dias === 1 ? "dia" : "dias") + '</small></div>';
        return '<li><div><div class="org">' + esc(e.org) + '</div><div class="meta">' + esc(e.cargo) + " · " + esc(vagas(e)) + (/^[\d.]+$/.test(vagas(e)) ? " vagas" : "") + '</div></div>' + right + '</li>';
      }).join("") || '<li><div class="meta">Nenhum edital cadastrado no momento.</div></li>';
    });
  }

  /* página de editais */
  var body = document.getElementById("ed-body");
  if (body) {
    var fStatus = "todos", fArea = "todas", fQ = "", ALL = [];
    var hash = (location.hash || "").replace("#", "");
    if (AREAS[hash]) fArea = hash;
    var STATUS = [["todos", "Todos"], ["aberto", "Abertos"], ["encerrando", "Encerrando"], ["previsto", "Previstos"]];

    var chipsSt = document.getElementById("f-status");
    var chipsAr = document.getElementById("f-area");
    function chips() {
      chipsSt.innerHTML = STATUS.map(function (s) { return '<button type="button" class="chip" data-st="' + s[0] + '" aria-pressed="' + (s[0] === fStatus) + '">' + s[1] + '</button>'; }).join("");
      var keys = ["todas"].concat(Object.keys(AREAS));
      chipsAr.innerHTML = keys.map(function (k) { return '<button type="button" class="chip" data-ar="' + k + '" aria-pressed="' + (k === fArea) + '">' + (k === "todas" ? "Todas as áreas" : AREAS[k]) + '</button>'; }).join("");
    }
    function render() {
      var q = fQ.trim().toLowerCase();
      var list = ALL.filter(function (e) {
        if (e.st === "encerrado") return false;
        var okS = fStatus === "todos" || e.st === fStatus || (fStatus === "aberto" && e.st === "encerrando");
        var okA = fArea === "todas" || e.area === fArea;
        var okQ = !q || (e.org + " " + e.cargo).toLowerCase().indexOf(q) >= 0;
        return okS && okA && okQ;
      }).sort(function (a, b) {
        var ra = a.st === "previsto" ? 1 : 0, rb = b.st === "previsto" ? 1 : 0;
        if (ra !== rb) return ra - rb;
        if (ra === 0) return a.dias - b.dias;
        return (b.destaque ? 1 : 0) - (a.destaque ? 1 : 0);
      });
      body.innerHTML = list.map(function (e) {
        var prazo = e.st === "previsto" ? (e.previsao || "A definir") : fmtDate(e.inscricoesAte) + '<div class="obs">' + e.dias + (e.dias === 1 ? " dia" : " dias") + ' restantes</div>';
        var src = (e.fontes || []).map(function (f) { return '<a href="' + esc(f.url) + '" target="_blank" rel="noopener">' + esc(f.nome) + '</a>'; }).join("");
        var val = e.validado ? '<span class="pill aberto" title="Conferido em ' + fmtDate(e.conferidoEm || data_updated) + '">Conferido</span>' : '<span class="pill avalidar">A validar</span>';
        return '<tr><td><div class="org">' + esc(e.org) + '</div><div class="cargo">' + esc(e.cargo) + " · " + esc(AREAS[e.area] || "") + '</div>' + (e.obs ? '<div class="obs">' + esc(e.obs) + '</div>' : "") + '</td>' +
          '<td><span class="pill ' + e.st + '">' + STLABEL[e.st] + '</span></td><td>' + esc(e.banca || "A definir") + '</td>' +
          '<td class="num">' + esc(vagas(e)) + '</td><td class="num">' + esc(e.salario || "A confirmar") + '</td><td class="num">' + prazo + '</td>' +
          '<td><div class="src">' + val + src + '</div></td></tr>';
      }).join("");
      document.getElementById("ed-empty").hidden = list.length > 0;
      var upd = document.getElementById("ed-updated");
      if (upd) upd.textContent = fmtDate(data_updated);
    }
    var data_updated = "";
    loadEditais(function (data) { ALL = enrich(data.editais); data_updated = data.atualizadoEm || ""; chips(); render(); });
    chipsSt.addEventListener("click", function (e) { var b = e.target.closest("[data-st]"); if (!b) return; fStatus = b.getAttribute("data-st"); chips(); render(); });
    chipsAr.addEventListener("click", function (e) { var b = e.target.closest("[data-ar]"); if (!b) return; fArea = b.getAttribute("data-ar"); chips(); render(); });
    document.getElementById("f-q").addEventListener("input", function (e) { fQ = e.target.value; render(); });
  }

  /* filtro de categorias do blog */
  var bc = document.getElementById("b-cats");
  if (bc) {
    bc.addEventListener("click", function (e) {
      var b = e.target.closest("[data-cat]"); if (!b) return;
      var cat = b.getAttribute("data-cat");
      bc.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", String(c === b)); });
      var shown = 0;
      document.querySelectorAll("#b-posts .post").forEach(function (p) {
        var ok = cat === "Todos" || p.getAttribute("data-cat") === cat;
        p.hidden = !ok; if (ok) shown++;
      });
      document.getElementById("b-empty").hidden = shown > 0;
    });
  }
})();
