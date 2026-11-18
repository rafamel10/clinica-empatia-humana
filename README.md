# Empatia Humana — site da clínica

Página de captação da **Empatia Humana, conceito em estética integrativa**, clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA). Responsável técnica: Dra. Adelaine Barros Montel, biomédica, inscrição nº 1437 no CRBM 4ª Região.

Publicado pelo GitHub Pages: https://rafamel10.github.io/clinica-empatia-humana/

A página foi feita para receber tráfego pago. A estrutura segue a da LP da Black Voll: formulário no topo, prova social em sequência e um botão de agendamento depois de cada bloco.

## Estrutura

```
index.html                    página principal com o quiz de agendamento
obrigado.html                 página depois do envio (dispara o evento de Lead)
politica-de-privacidade.html  política de privacidade (LGPD)
css/style.css                 estilos, cores e tipografia
js/config.js                  planilha, WhatsApp e fotos de antes e depois (o único arquivo de configuração)
js/main.js                    quiz, formulário final, abas, versões por campanha e eventos
google-apps-script/Codigo.gs  script que grava os leads na planilha
assets/img/                   fotos, logo e ícones
.nojekyll                     publica os arquivos como estão no GitHub Pages
```

Não tem etapa de build: o que está no repositório é o que vai ao ar. Cada push na `main` publica de novo em cerca de 1 minuto.

## Seções da página

1. **Abertura**: logo, título, nota 5,0 do Google, três pontos de confiança e o **quiz de agendamento** em 4 passos
2. **"Esta avaliação é para você se..."**: as situações que trazem a pessoa à clínica, com um mosaico de fotos (recepção, avaliação, consultório, fachada)
3. **Números**: +18 anos de formação, nota 5,0 no Google, inscrição no CRBM desde 2011
4. **Depoimentos**: trecho do depoimento em vídeo, três prints do WhatsApp que a clínica publicou nos destaques e 8 avaliações do Google. No celular, os relatos viram um carrossel de arrastar
5. **Tratamentos em abas**: vasinhos e varizes, dor, gordura localizada, pele e rosto, intestino e detox
6. **Quem vai cuidar de você**: história, formação e o quadro com o registro conferido no CFBM
7. **Como funciona a avaliação**: 4 passos
8. **Antes e depois**: fica escondida até ter fotos (veja abaixo)
9. **Dúvidas frequentes**
10. **Cursos para profissionais**
11. **Onde fica**: endereço, horários e mapa
12. **Chamada final** com um formulário curto

## O quiz de agendamento

São 4 passos, com barra de progresso:

1. O que você quer tratar (ou "sou profissional e quero fazer um curso")
2. Há quanto tempo isso incomoda (para quem escolheu curso: qual é a área)
3. Melhor horário (manhã, tarde ou sábado)
4. Nome e WhatsApp

No celular, tocar numa opção já passa para a próxima pergunta. No teclado, a pessoa usa o botão Continuar. Sem JavaScript, as perguntas aparecem todas de uma vez.

Os botões dos tratamentos ("Quero avaliar minhas pernas" etc.) levam ao quiz com o tratamento já escolhido, direto no passo 2.

Depois do envio, a pessoa vai para o `obrigado.html`, que chama pelo nome e tem um botão de WhatsApp com a mensagem pronta (nome, tratamento e melhor horário).

## Planilha de leads

1. Crie uma planilha nova no Google Sheets, de preferência na conta da clínica.
2. Menu **Extensões > Apps Script**. Apague o que estiver lá e cole o conteúdo de `google-apps-script/Codigo.gs`. Salve.
3. **Implantar > Nova implantação**, tipo **App da Web**. Executar como: **Eu**. Quem pode acessar: **Qualquer pessoa**. Implante e autorize.
4. Copie o endereço que termina em `/exec` e cole em `planilhaUrl`, no `js/config.js`. Faça commit e push.
5. Teste: abrir o endereço `/exec` no navegador mostra `{"ok":true,"status":"no ar"}`. Depois envie um pedido pelo site e veja a linha aparecer.

Colunas: data e hora, nome, WhatsApp, link para abrir a conversa, interesse, há quanto tempo (ou a área, para cursos), melhor horário, qual formulário (quiz ou final), as UTMs, se veio de clique de anúncio (fbclid ou gclid), a página e de onde a pessoa veio.

Se já tinha instalado a versão anterior do script, cole o novo código e faça **Implantar > Gerenciar implantações > Editar > Nova versão**. Numa planilha nova, o cabeçalho sai certo sozinho.

## Pixel, Google e Tintim

Cole o código no `<head>` do `index.html` **e** do `obrigado.html`, no lugar do comentário "Pixel do Meta, tag do Google ou script do Tintim".

Eventos que o site já dispara:

| Evento | Quando |
|---|---|
| `Lead` (Meta) / `generate_lead` (Google) | Na página de obrigado, uma vez por envio |
| `Contact` (Meta) / `contact` (Google) | Clique em qualquer link direto de WhatsApp |
| `QuizPasso` (personalizado) | A cada passo do quiz, com o número do passo |
| `AbaTratamento` (personalizado) | Clique numa aba de tratamento |

Use o `Lead` como conversão das campanhas. O `QuizPasso` mostra em que pergunta as pessoas desistem.

## Links para os anúncios

Cada campanha abre a página com o título trocado, o tratamento já escolhido no quiz (que começa no passo 2) e a aba certa aberta:

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

## Antes e depois

A seção já está pronta e só aparece quando houver fotos em `resultados`, no `js/config.js`:

```js
resultados: [
  { antes: "assets/img/resultados/peim-1-antes.jpg", depois: "assets/img/resultados/peim-1-depois.jpg",
    tratamento: "PEIM integrativo", legenda: "4 sessões" },
],
```

Pelo Código de Ética da Biomedicina (Resolução CFBM nº 330/2020, art. 10, IV, e art. 11, c), a foto de paciente só pode ser publicada com termo de consentimento (TCLE) assinado para esse fim e com o aviso de que a imagem não garante resultado. O aviso já aparece embaixo da seção.

## De onde vieram as informações

- **Google (perfil da clínica)**: nota 5,0, 27 avaliações, horário de funcionamento, fotos da recepção e o retrato vertical da Dra. Adelaine
- **Instagram @clinicaempatiahumana**: destaque "Depoimentos" (prints do WhatsApp e depoimento em vídeo) e a foto da fachada
- **Instagram @biomedicaadelaine**: destaque "Quem sou?" (formação e história) e "Casos clínicos" (como é a consulta integrativa)
- **Consulta pública do CFBM** (cfbm-br.implanta.net.br): inscrição nº 1437 no CRBM 4ª Região, ativa, requerida em 22/03/2011, com as habilitações Biomedicina Estética, Patologia Clínica e Práticas Integrativas (Ozonioterapia). Também tem a inscrição nº 18758 no CRBM 3ª Região
- **Cadastro do CNPJ 20.199.921/0001-32**: razão social e endereço

## Como editar

- **WhatsApp**: o número aparece nos links `wa.me` do HTML e em `js/config.js`. Para trocar, faça localizar e substituir em todos os arquivos.
- **Textos**: estão no `index.html`, na ordem em que aparecem na página.
- **Depoimentos e avaliações**: blocos `conversa` e `avaliacao` no `index.html`. Para incluir um novo, copie um bloco e troque o texto.
- **Cores e fontes**: variáveis no topo do `css/style.css` (`--mata`, `--ouro`, `--areia`…). Fontes: Newsreader (títulos), Albert Sans (texto) e Allura (frase manuscrita do final), pelo Google Fonts.

## Para confirmar com a clínica antes de subir os anúncios

- Se a Dra. Adelaine concorda em contar no site o diagnóstico de lúpus (está no destaque "Quem sou?" dela)
- O título "especialista em terapias injetáveis": o CFBM não mostra especialidade registrada, por isso o site diz "formação em"
- Autorização dos pacientes cujos relatos aparecem (Marcela, Mávila e a paciente do vídeo). A clínica já publicou os prints, mas vale ter o ok por escrito
- Fotos de antes e depois com TCLE assinado
- Fotos originais em alta resolução do espaço e dos atendimentos
- Domínio próprio (ex.: empatiahumana.com.br), se quiserem usar no lugar do endereço do GitHub
