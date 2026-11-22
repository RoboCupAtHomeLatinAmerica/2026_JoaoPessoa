# Tarefas — RoboCup@Home Brazil Open 2026 (João Pessoa, 23 a 29/11)

Lista interna de pendências do site e da organização. Marque com `[x]` ao concluir.

## Antes da competição

### Fotos
Hoje as 4 fotos da Home estão como placeholder ("Photo coming soon"). Para cada uma: em `data/event.json` (`photos`), remover `"placeholder": true` e informar `src` e `thumb`; depois rodar `python3 tools/make_thumbs.py`.
- [ ] **Robots**: `Photos/robots.jpg` e `Photos/thumbs/robots.webp` (foto da edição anterior) já estão no JSON; trocar pela desta edição ou só remover o `placeholder`.
- [ ] **Teams**: `Photos/teams.jpg` e `Photos/thumbs/teams.webp` (edição anterior) já estão no JSON; trocar pela desta edição ou só remover o `placeholder`.
- [ ] **Welcome drinks**: foto nova (ainda não existe arquivo).
- [ ] **Arena**: foto nova (ainda não existe arquivo).
- [ ] Opcional: trocar `Photos/og-image.jpg` (hoje um recorte de `teams.jpg`) por uma foto desta edição, 1200×630.

### Conteúdo do site
- [x] `csv/teams.csv` preenchido com as 9 equipes, a partir da planilha de complemento dos TDPs (capitão, instituição, robô, foto, site e vídeo).
- [ ] **TDP e Pôster** de todas as equipes estão vazios em `csv/teams.csv` (a tabela mostra "Coming soon"): preencher com os arquivos de 2026 (`TDPs/<equipe>.pdf`, `Posters/<equipe>.pdf`) quando chegarem. Os de 2025 continuam nas pastas, sem uso. Sem uso: `TDPs/mimoso.pdf` e as fotos `athena`, `Mecha_Electra`, `UD-H1`, `MIMOSO`.
- [x] Revisar `csv/people.csv` (nomes de pessoas) para esta edição.
- [ ] Conferir as datas do CfP em `data/event.json`: "Late Registration" em 29/11 é o último dia do evento e "Poster submission" em 23/11 é o primeiro. Confirmar se estão certas.
- [ ] Confirmar quem atende as equipes no local: o rodapé mostra o grupo do WhatsApp e o e-mail dos dois chairs (`data/event.json` → `chairs`). Trocar por um e-mail/telefone de plantão se houver.
- [ ] Conferir links: Olimpo, regulamento 2026.2, grupo do WhatsApp, template do TDP, formulário do robô.
- [ ] Conferir a agenda do Google Calendar (aba Schedule): agenda pública, fuso e horários da semana 23–29/11.
- [ ] Definir a URL do sistema de pontuação e colocar em `data/event.json` → `results.url` (a aba **Results** só aparece quando houver URL; o placar não fica mais neste site).

### Publicação
- [ ] Fazer o commit e o push das mudanças do site (o CSS compilado `css/site.css` precisa ir junto).
- [ ] Abrir https://robocupathomelatinamerica.github.io/2026_JoaoPessoa/ no celular e no computador e passar pelas abas.
- [ ] Testar a pré-visualização do link (WhatsApp/Telegram) com a nova `og-image.jpg`.
- [ ] Avisar as equipes que o site está atualizado.

### Logística da organização
- [ ] Confirmar equipes inscritas e pagamento (prazo regular 15/11; tardio até 29/11).
- [ ] Confirmar a lista de objetos e o material impresso das tarefas.
- [ ] Confirmar com o sistema de pontuação as equipes e as ligas (A/B).

## Durante a competição
- [ ] Manter a aba **Schedule** (Google Calendar) atualizada todos os dias.
- [ ] Avisar mudanças de horário no grupo do WhatsApp e na agenda.
- [ ] Publicar o link do sistema de pontuação (`results.url`) no primeiro dia.
- [ ] Subir as fotos reais do evento (arena, welcome drinks, equipes) e atualizar `data/event.json`.
- [ ] Se a lista de objetos mudar: ajustar nomes, categorias e recortes em `tools/import_objects.py` e rodar `python3 tools/import_objects.py <pasta_das_fotos> && python3 tools/make_thumbs.py` (a lista atual, com 27 fotos, já está publicada).
- [ ] Atualizar `csv/teams.csv` se houver inscrição tardia ou troca de robô.
- [ ] Guardar cópia dos resultados e das fotos ao fim de cada dia.

## Depois da competição
- [ ] Conferir a aba **Results** com o resultado final.
- [ ] Publicar a galeria final de fotos.
- [ ] Agradecer às equipes e arquivar o site (tag/branch do repositório).

---
Como manter o site: ver o fim do `README.md`.
- [ ] `data/team-details.json` vem da planilha de complemento dos TDPs (resposta mais recente de cada equipe, sem os valores "None"/"N/A"). Se alguém reenviar o formulário, regerar o arquivo (os valores são só texto, em inglês ou português como foram preenchidos).
