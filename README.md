# Empatia Humana — site da clínica

Site de uma página da **Empatia Humana, conceito em estética integrativa**, clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA). A responsável técnica é a Dra. Adelaine Barros Montel, biomédica esteta e ozonioterapeuta, CRBM 1437/PA.

Publicado pelo GitHub Pages: https://rafamel10.github.io/clinica-empatia-humana/

## Estrutura

```
index.html              página única (todo o conteúdo)
css/style.css           estilos, cores e tipografia
js/main.js              menu do celular
assets/img/             fotos, logo e ícones
.nojekyll               publica os arquivos como estão no GitHub Pages
```

Não tem etapa de build: o que está no repositório é o que vai ao ar. Qualquer push na `main` publica de novo em cerca de 1 minuto.

## Seções

1. Abertura: título, índice Dor / Varizes / Intestino e retrato da Dra. Adelaine
2. Tratamentos: ozonioterapia para dor, varizes e vasinhos (PEIM), saúde intestinal e outros serviços da clínica (microagulhamento, peelings, massagem)
3. Dra. Adelaine: trajetória e registro profissional
4. Como é o atendimento: as 3 etapas, do WhatsApp ao plano de tratamento
5. Cursos para profissionais
6. Relatos de pacientes: links para os destaques do Instagram
7. Como chegar: endereço, canais e mapa

## De onde vieram as informações

- Perfis do Instagram [@clinicaempatiahumana](https://www.instagram.com/clinicaempatiahumana/) e [@biomedicaadelaine](https://www.instagram.com/biomedicaadelaine/): bio, destaques, posts e fotos
- Link da bio (bio.site/empatiahumana): WhatsApp, link do Google Maps, formulário da Masterclass e o retrato da Dra. Adelaine
- Cadastro público do CNPJ 20.199.921/0001-32: razão social e endereço

As fotos foram tiradas dos posts do Instagram (até 640 px) e recortadas para não mostrar os textos das artes.

## Como editar

- **WhatsApp**: o número `559491182268` aparece em todos os links `wa.me` do `index.html`. Para trocar, faça localizar e substituir.
- **Textos**: estão todos no `index.html`, na ordem em que aparecem na página.
- **Cores e fontes**: variáveis no topo do `css/style.css` (`--mata`, `--ocre`, `--nevoa`…). As fontes são Newsreader (títulos) e Albert Sans (texto), pelo Google Fonts.
- **Fotos**: substitua os arquivos em `assets/img/` mantendo os mesmos nomes, ou atualize o `src` e as medidas (`width`/`height`) no HTML.

## Para confirmar com a clínica

- Horário de funcionamento (hoje o site diz "Atendimento com horário marcado")
- Se o endereço do cadastro do CNPJ (Rua Círio de Nazaré, 558, salas 1 e 2, Centro) é o atual
- Se o formulário da Masterclass de Ozonioterapia ainda está aceitando inscrições
- Fotos originais em alta resolução, principalmente do espaço da clínica
- Domínio próprio (ex.: empatiahumana.com.br), se quiserem usar um no lugar do endereço do GitHub
