# Dicionário de Terminologia Arquivística

Aplicativo desenvolvido pela **Câmara Técnica de Terminologia Arquivística**, para celular (Android e iPhone) e computador. Reúne:

- a **árvore de domínio** da Arquivologia (versão 0.2, 8 ramos, 161 nós);
- o **dicionário em construção** (162 verbetes com proposta de definição);
- o **diagnóstico da terminologia nas resoluções do Conarq** (60 resoluções, 2.085 ocorrências, 1.491 termos).

## Como usar

Abra **https://seanvogel-cloud.github.io/dicionario-terminologia-arquivistica/** no celular.

- **iPhone:** no Safari, toque em Compartilhar › *Adicionar à Tela de Início*.
- **Android:** no Chrome, toque no menu ⋮ › *Instalar app* (ou *Adicionar à tela inicial*).

Depois de instalado, o app abre em tela cheia e funciona sem internet.

## Origem dos dados

Planilhas `Selecao_termos_e_arvore_thiago.xlsx` e `Terminologia_Resolucoes_Conarq_Diagnostico-2.xlsx`.
Na aba *Árvore de domínio – ver 0.2*, o Excel havia convertido os códigos em datas (por exemplo, `1.1` virou 01/01/2026);
os códigos foram reconstruídos e conferidos com a versão 0.1 e com a aba *Dicionário x Conarq*.

## Arquivos

| Caminho | O que é |
|---|---|
| `index.html` | o app, com os dados principais embutidos |
| `data/ocorrencias.json` | as definições literais das resoluções (carregadas sob demanda) |
| `sw.js`, `manifest.webmanifest`, `icons/` | instalação na tela inicial e uso sem internet |
| `fonte/` | modelo do app e scripts usados para gerar o site a partir das planilhas |

Para regenerar o site:

1. `python3 fonte/extract.py <planilha de seleção e árvore>.xlsx <planilha de diagnóstico>.xlsx` (lê as planilhas e grava `fonte/dados.json`)
2. `python3 fonte/build_data.py` (gera `fonte/core.js` e `data/ocorrencias.json`)
3. `python3 fonte/build_site.py` (monta `index.html`, `sw.js` e `manifest.webmanifest`)

Os passos 1 e 2 só são necessários quando as planilhas mudam; para mudanças na aparência basta o passo 3.
