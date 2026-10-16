# Rotina diária (03:00, horário de Belém)

1. Pesquisar novidades de concursos de TODAS as áreas (federais, estaduais, municipais, tribunais, fiscal, policial, educação, saúde, bancário etc.): editais abertos, bancas, prazos, retificações, isenções. Dar destaque especial aos concursos bancários, sem limitar a eles.
2. Atualizar `src/editais.json` (campo `atualizadoEm`) e, se houver fato relevante, adicionar artigo em `src/articles.py`.
3. Rodar `python3 src/build.py` (gera `site/`) e conferir que não há erro.
4. `git add -A && git commit && git push` na branch `main`. O cPanel publica sozinho (`.cpanel.yml`).
5. Enviar o resumo do dia ao Alan, pronto para colar no grupo do WhatsApp.

Regras: só alterar dados confirmados em fonte oficial; o que estiver incerto vai como "a confirmar" no resumo, sem publicar.
`site/` é a saída publicada: nunca editar à mão, sempre gerar pelo build.
