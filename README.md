# Empatia Humana — site da clínica

Site institucional com captação da **Clínica Empatia Humana, conceito em estética integrativa**, em Canaã dos Carajás (PA). Responsável técnica: Dra. Adelaine Barros Montel, biomédica, inscrição nº 1437 no CRBM 4ª Região.

Publicado pelo GitHub Pages: https://rafamel10.github.io/clinica-empatia-humana/

Estrutura inspirada na draotorrino.com.br: home institucional, **uma página por tratamento** (para anúncio e para busca local), página da doutora e **blog** para SEO local e para buscadores com IA (Google AI Overviews, ChatGPT, Perplexity).

Conversão: um único objetivo em todas as páginas. A pessoa deixa **nome, WhatsApp e e-mail**, o lead vai para a planilha e ela cai direto na conversa do WhatsApp da clínica, com a mensagem pronta (nome, tratamento da página e código da campanha).

## Como o site é feito

As páginas são **geradas por script**. Nunca edite os HTML à mão: edite os textos e rode o gerador.

```
scripts/dados.py        TODOS os textos: clínica, Dra. Adelaine, tratamentos, depoimentos, avaliações, FAQ, cursos
scripts/gerar.py        modelos das páginas, dados estruturados, sitemap, robots, llms.txt, feed do blog
scripts/imagens.py      gera as fotos .webp e a imagem de prévia (og-empatia.jpg)
conteudo/blog/*.md      posts do blog (um arquivo por post)
css/site.css            visual
js/config.js            planilha, WhatsApp, e-mail obrigatório, GTM, Pixel, modo de cookies
js/medicao.js           consentimento, GTM e Pixel
js/site.js              formulário, janela de agendamento, menu, barra fixa, eventos
google-apps-script/     script que grava os leads na planilha
```

Para publicar uma mudança:

```
python scripts/gerar.py          # gera as páginas
python scripts/imagens.py        # só se trocou alguma foto
git add -A && git commit -m "..." && git push
```

O GitHub Pages publica em cerca de 1 minuto. Se mudou CSS ou JS, aumente `VERSAO` no topo do `gerar.py` antes de gerar (limpa o cache do navegador).

## Páginas

| Endereço | O que é |
|---|---|
| `/` | Home: formulário no topo, "Quando procurar", tratamentos, números, Dra. Adelaine, o que é estética integrativa, depoimentos, dúvidas, blog, cursos, contato |
| `/tratamentos/` | Todos os tratamentos |
| `/tratamentos/vasinhos-e-varizes/` | PEIM |
| `/tratamentos/ozonioterapia/` | Ozonioterapia para dor |
| `/tratamentos/lipo-ozonizada/` | Gordura localizada |
| `/tratamentos/consulta-integrativa/` | Consulta de estética integrativa |
| `/tratamentos/saude-intestinal/` | Disbiose Zero, enema de café, detox |
| `/tratamentos/limpeza-de-pele/` | Limpeza de pele, peelings, melasma |
| `/tratamentos/soroterapia/` | Soroterapia e vitaminas |
| `/dra-adelaine-montel/` | Trajetória, formação e registro no CFBM |
| `/cursos/` | Cursos para profissionais |
| `/blog/` e `/blog/<post>/` | Blog |

Cada página de tratamento segue a mesma ordem: título com cidade e frase emocional, sinais (chips) e formulário; identificação ("você se reconhece") e a virada; o que o tratamento faz por você; passo a passo; quando procurar; prova social; FAQ; posts relacionados; outros tratamentos; faixa final.

### Links para anúncios

Mande cada anúncio para a página do tratamento, com UTMs:

```
https://rafamel10.github.io/clinica-empatia-humana/tratamentos/vasinhos-e-varizes/?utm_source=meta&utm_medium=pago&utm_campaign=vasinhos-nov&utm_content=v1
```

O código `meta-vasinhos-nov-v1` vai no fim da mensagem do WhatsApp e na planilha.

## Blog

Cada post é um arquivo em `conteudo/blog/<endereco-do-post>.md`:

```
---
titulo: Ozonioterapia: o que é, para que serve e como é feita
descricao: (140 a 158 caracteres, aparece no Google)
categoria: Ozonioterapia
tratamento: ozonioterapia        (endereço da página de tratamento ligada ao post)
data: 2026-11-25
tempo_leitura: 7                 (opcional)
resumo: (resposta rápida em 2 ou 3 frases: é o que a IA e o Google citam)
rascunho: sim                    (opcional: não publica)
---

Abertura...

## Subtítulo em forma de pergunta?

Texto, listas com "- ", **negrito**, [links](/tratamentos/ozonioterapia/).

## Perguntas frequentes

### Pergunta?

Resposta.
```

O gerador monta sozinho: caixa de "Resposta rápida", índice, botão do tratamento no meio do texto, FAQ com dados estruturados, caixa da autora, posts relacionados, sitemap, feed e `llms.txt`.

Regras que ajudam a ranquear: título com a pergunta que a pessoa pesquisa; resposta direta logo no começo; subtítulos em forma de pergunta; citar Canaã dos Carajás e a região com naturalidade; 2 a 4 links para tratamentos e outros posts; FAQ no fim. Publicar com constância (1 a 2 posts por semana) pesa mais que posts enormes.

## SEO local e IA

- Dados estruturados em todas as páginas: `MedicalClinic` + `HealthAndBeautyBusiness` (endereço, horário, área atendida, nota do Google), `Person` da Dra. Adelaine com o registro no CRBM, `Service`/`MedicalProcedure` em cada tratamento, `FAQPage`, `BlogPosting`, `BreadcrumbList`.
- `sitemap.xml`, `robots.txt` (libera os robôs de IA) e `llms.txt` (resumo da clínica para IAs) são gerados a cada `gerar.py`.
- Nome, endereço e telefone iguais em todo o site. Mantenha iguais no Google Meu Negócio, Instagram e Facebook.

## Planilha de leads

1. Crie uma planilha nova no Google Sheets, de preferência na conta da clínica.
2. **Extensões > Apps Script**. Apague o que estiver lá e cole o conteúdo de `google-apps-script/Codigo.gs`. Salve.
3. **Implantar > Nova implantação**, tipo **App da Web**. Executar como: **Eu**. Quem pode acessar: **Qualquer pessoa**. Implante e autorize.
4. Copie o endereço que termina em `/exec` e cole em `planilhaUrl`, no `js/config.js`. Rode `gerar.py` e publique.
5. Teste: abrir o `/exec` no navegador mostra `{"ok":true,"status":"no ar"}`. Depois envie um lead pelo site e veja a linha.

Colunas: data e hora, nome, WhatsApp, e-mail, link para abrir a conversa, interesse, página do tratamento, formulário, **status** (começa como "Novo": a equipe atualiza para medir custo por agendamento), UTMs, clique de anúncio, primeira origem, página, de onde veio, ID do lead.

## Pixel, GTM e eventos

Cole os IDs em `js/config.js` (`gtmId`, `pixelId`). O modo de cookies padrão é `"aviso"`: as ferramentas carregam e a pessoa pode recusar. Troque para `"consentimento"` para só carregar depois do "Aceitar".

| Evento (dataLayer) | Quando | Pixel |
|---|---|---|
| `inicio_formulario` | primeiro toque num formulário | |
| `abriu_formulario` | clique num botão que abre a janela de agendamento | |
| `lead` | envio válido, com `lead_id` | `Lead` com `eventID` = `lead_id` |
| `clique_whatsapp` | ida para o WhatsApp | `Contact` (links diretos) |
| `abriu_duvida` | primeira pergunta aberta | |
| `rolagem_50` | metade da página | |
| `cookies_aceitos` / `cookies_recusados` | escolha no aviso | consentimento |

Nome, telefone e e-mail nunca vão para o dataLayer nem para o Pixel.

## Domínio próprio

Quando tiver o domínio (ex.: empatiahumana.com.br): troque `url` e `base` em `SITE` no `scripts/dados.py` (`base` vira `"/"`), crie o arquivo `CNAME` com o domínio, rode `gerar.py`, publique e configure o DNS (A do domínio para os 4 IPs do GitHub Pages e `www` como CNAME de `rafamel10.github.io`).

## Pendências

- `planilhaUrl` (sem ela o lead não fica gravado) e IDs do GTM/Pixel
- Fotos profissionais da clínica e dos procedimentos (hoje são as do Instagram e do Google)
- Depoimentos novos por escrito, com autorização
- Domínio próprio
