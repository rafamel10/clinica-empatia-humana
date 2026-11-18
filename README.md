# Empatia Humana — site da clínica

Página de captação da **Empatia Humana, conceito em estética integrativa**, clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA). A responsável técnica é a Dra. Adelaine Barros Montel, biomédica esteta e ozonioterapeuta, CRBM 1437/PA.

Publicado pelo GitHub Pages: https://rafamel10.github.io/clinica-empatia-humana/

A página foi feita para receber tráfego pago. O formulário de agendamento fica no topo, e todos os botões da página levam até ele.

## Estrutura

```
index.html                    página principal com o formulário
obrigado.html                 página depois do envio (dispara o evento de Lead)
politica-de-privacidade.html  política de privacidade (LGPD)
css/style.css                 estilos, cores e tipografia
js/config.js                  endereço da planilha e WhatsApp (o único arquivo de configuração)
js/main.js                    formulário, versões por campanha, menu e eventos
google-apps-script/Codigo.gs  script que grava os leads na planilha
assets/img/                   fotos, logo e ícones
.nojekyll                     publica os arquivos como estão no GitHub Pages
```

Não tem etapa de build: o que está no repositório é o que vai ao ar. Cada push na `main` publica de novo em cerca de 1 minuto.

## Como o formulário funciona

1. A pessoa preenche nome, WhatsApp e o que quer tratar.
2. O site manda os dados para a planilha (se `planilhaUrl` estiver preenchido) e abre o `obrigado.html`.
3. O obrigado dispara `Lead` no Pixel do Meta e `generate_lead` no Google, se esses códigos estiverem instalados.
4. No obrigado tem um botão de WhatsApp com a mensagem pronta, com o nome e o tratamento escolhido.

Se a planilha não estiver configurada, o formulário continua funcionando e leva a pessoa ao WhatsApp, mas o lead não fica gravado.

Cliques nos links diretos de WhatsApp contam como `Contact` no Pixel.

## Planilha de leads

1. Crie uma planilha nova no Google Sheets, de preferência na conta da clínica.
2. Menu **Extensões > Apps Script**. Apague o que estiver lá e cole o conteúdo de `google-apps-script/Codigo.gs`. Salve.
3. **Implantar > Nova implantação**, tipo **App da Web**. Executar como: **Eu**. Quem pode acessar: **Qualquer pessoa**. Implante e autorize.
4. Copie o endereço que termina em `/exec` e cole em `planilhaUrl`, no `js/config.js`. Faça commit e push.
5. Teste: abrir o endereço `/exec` no navegador mostra `{"ok":true,"status":"no ar"}`. Depois envie um pedido pelo site e veja a linha aparecer.

Colunas gravadas: data e hora, nome, WhatsApp, link para abrir a conversa, interesse, as UTMs, se veio de clique de anúncio (fbclid ou gclid), a página e de onde a pessoa veio.

## Pixel, Google e Tintim

Cole o código no `<head>` do `index.html` **e** do `obrigado.html`, no lugar do comentário "Pixel do Meta, tag do Google ou script do Tintim". O site já chama `fbq('track', 'Lead')` e `gtag('event', 'generate_lead')` no obrigado. Para otimizar campanhas, use o evento Lead como conversão.

## Links para os anúncios

Cada campanha pode abrir a página com o título e o tratamento já escolhidos no formulário:

| Campanha | Link |
|---|---|
| Vasinhos e varizes | `https://rafamel10.github.io/clinica-empatia-humana/?tratamento=varizes` |
| Dor (ozonioterapia) | `…/?tratamento=dor` |
| Gordura localizada | `…/?tratamento=medidas` |
| Pele e rosto | `…/?tratamento=pele` |
| Intestino e detox | `…/?tratamento=intestino` |
| Cursos | `…/?tratamento=cursos` |

Acrescente as UTMs no mesmo link, por exemplo `?tratamento=varizes&utm_source=meta&utm_medium=pago&utm_campaign=varizes-nov`. Elas vão para a planilha e passam para o obrigado.

Os textos de cada versão ficam em `js/main.js`, no bloco `VERSOES`.

## Seções da página

1. Abertura com título, selos, formulário com foto da Dra. Adelaine e índice dos tratamentos
2. Faixa dourada com os tratamentos passando
3. "Você se reconhece": as situações que levam a pessoa a procurar a clínica
4. Por que escolher a Empatia Humana: 4 diferenciais
5. Tratamentos: vasinhos em destaque, cartões de dor, gordura localizada e pele, intestino em destaque
6. Quem vai cuidar de você: credenciais, trajetória e linha do tempo da Dra. Adelaine
7. A clínica: galeria de fotos (toque para ampliar), vídeos e chamada para o Instagram
8. Como funciona: as 3 etapas
9. Dúvidas frequentes
10. Cursos para profissionais
11. Chamada final, endereço e mapa

Efeitos: elementos que aparecem ao rolar, barra de progresso no topo, topo que fica compacto, zoom lento na foto do formulário, brilho no botão principal, anel girando no retrato, botão flutuante de WhatsApp. Tudo é desligado para quem ativa "reduzir movimento" no celular ou computador.

## Fotos e vídeos

As fotos novas vêm do ensaio "Adelaine - ensaio" do Google Drive, reduzidas para cerca de 50 KB cada em `assets/img/*.webp`.

Para colocar vídeos (Reels do Instagram, YouTube ou .mp4), cole os links em `videos` no `js/config.js`. Enquanto a lista estiver vazia, a parte de vídeos fica escondida.

## Como editar

- **WhatsApp**: o número aparece nos links `wa.me` do HTML e em `js/config.js`. Para trocar, faça localizar e substituir em todos os arquivos.
- **Textos**: estão no `index.html`, na ordem em que aparecem na página.
- **Cores e fontes**: variáveis no topo do `css/style.css` (`--mata`, `--ouro`, `--areia`…). Fontes: Newsreader (títulos) e Albert Sans (texto), pelo Google Fonts.
- **Fotos**: substitua os arquivos em `assets/img/` mantendo os nomes, ou atualize o `src` e as medidas (`width`/`height`) no HTML.

## Para confirmar com a clínica antes de subir os anúncios

- Se a avaliação para procedimentos é mesmo gratuita (está na resposta "A avaliação tem custo?")
- Se o tratamento de vasinhos parcela em até 10x
- Se a massagem e a drenagem são feitas também em casa
- Horário de funcionamento
- Se a Dra. Adelaine ainda é professora universitária e citologista (veio dos materiais de 2021)
- Links de Reels ou vídeos para a seção de vídeos
- Depoimentos reais de pacientes, com autorização, para colocar na página
- Fotos originais em alta resolução, principalmente do espaço da clínica
- Domínio próprio (ex.: empatiahumana.com.br), se quiserem usar no lugar do endereço do GitHub
