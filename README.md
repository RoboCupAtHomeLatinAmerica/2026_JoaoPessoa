# Competição Brasileira de Robótica (CBR) / RoboCup@home Brazil Open  

[https://robocupathomelatinamerica.github.io/2026_JoaoPessoa/](https://robocupathomelatinamerica.github.io/2026_JoaoPessoa/)


## Como manter o site

Site estático (GitHub Pages). Para ver localmente: `python3 -m http.server 8000` e abrir http://localhost:8000.

| O que mudar | Onde |
|---|---|
| Datas, cidade, chairs, OC, links, datas importantes, fotos da Home, URL dos resultados | `data/event.json` |
| Equipes (nome, capitão, instituição, TDP, pôster, robô, foto) | `csv/teams.csv` |
| Nomes de pessoas / objetos | `csv/people.csv`, `Photos/objects/index.csv` |
| Texto do CfP e demais seções | `index.html` |

Comandos (após `npm install`):

- `npm run thumbs` — gera miniaturas WebP em `Photos/thumbs/` (rode ao adicionar fotos de objetos/robôs/Home).
- `npm run build:css` — recompila `css/site.css` (rode ao mudar classes Tailwind no `index.html` ou em `scripts/`). O arquivo compilado é versionado porque o GitHub Pages não executa build.

As abas têm endereço próprio: `#home`, `#cfp`, `#teams`, `#schedule`, `#tasks` (e `#results`, que só aparece quando `results.url` está preenchido em `data/event.json`). A pontuação não fica neste site.
