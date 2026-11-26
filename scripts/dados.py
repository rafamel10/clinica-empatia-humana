# -*- coding: utf-8 -*-
"""Textos e dados do site da Empatia Humana.

Tudo o que aparece no site sai daqui (e dos posts em conteudo/blog/*.md).
Depois de editar, rode:  python scripts/gerar.py
"""

SITE = {
    # Endereço público. Se ligar um domínio próprio (ex.: https://empatiahumana.com.br), troque as duas linhas:
    "url": "https://empatiahumana.com.br",
    "base": "/",
    "nome": "Empatia Humana",
    "nome_completo": "Empatia Humana - Conceito em Estética Integrativa",
    "cidade": "Canaã dos Carajás",
    "uf": "PA",
    "endereco": "Rua Círio de Nazaré, 558, salas 1 e 2",
    "bairro": "Centro",
    "geo": (-6.5311727, -49.848366),
    "whatsapp": "559491182268",
    "telefone": "(94) 99118-2268",
    "instagram_clinica": "https://www.instagram.com/clinicaempatiahumana/",
    "instagram_dra": "https://www.instagram.com/biomedicaadelaine/",
    "facebook": "https://www.facebook.com/empatiahumana",
    "maps_cid": "https://www.google.com/maps?cid=6446281295361355134",
    "maps": "https://www.google.com/maps/place/Empatia+Humana+-Conceito+em+Est%C3%A9tica+Integrativa/@-6.5311727,-49.848366,15z/data=!4m6!3m5!1s0x92dd9d833f3e3747:0x5975caaf2c422d7e!8m2!3d-6.5311727!4d-49.848366!16s%2Fg%2F11qqnj7w_k",
    "maps_embed": "https://maps.google.com/maps?q=-6.5311727,-49.848366&z=16&output=embed",
    "nota_google": "5,0",
    "avaliacoes_google": 27,
    "cnpj": "20.199.921/0001-32",
    "razao": "JG Centro de Estética Integrativa LTDA",
    "regiao": ["Canaã dos Carajás", "Parauapebas", "Curionópolis", "Água Azul do Norte", "Marabá"],
    "horarios": [
        ("Segunda a sexta", "8h às 12h e 14h às 18h"),
        ("Sábado", "8h às 12h"),
        ("Domingo", "Fechado"),
    ],
    "data_atualizacao": "2026-11-25",
    "avaliacoes_conferidas_em": "novembro de 2026",
    # Código de verificação do Google Search Console (só o content da meta tag). Vazio: não entra.
    "google_verificacao": "",
    "bing_verificacao": "",
}

DRA = {
    "nome": "Dra. Adelaine Montel",
    "nome_completo": "Adelaine Barros Montel",
    "cargo": "Biomédica esteta e ozonioterapeuta",
    "registro": "CRBM 4ª Região nº 1437",
    "registro_curto": "CRBM 1437",
    "desde": "2011",
    "habilitacoes": [
        "Biomedicina Estética",
        "Patologia Clínica (Análises Clínicas)",
        "Práticas Integrativas e Complementares em Saúde (Ozonioterapia)",
    ],
    "formacao": [
        "Mais de 18 anos de formada",
        "Biomédica esteta",
        "Ozonioterapeuta, com habilitação registrada no CRBM",
        "Pós-graduada em Nutrição Ortomolecular (Hi-Nutrition)",
        "Graduada em Citologia (PUC Goiás)",
        "Formação em terapias injetáveis no tratamento da dor crônica",
        "Aprendeu de perto com o Dr. Lair Ribeiro, referência em saúde integrativa",
    ],
    "frase": "Saúde e beleza não são resultado de uma única escolha, mas da soma de bons hábitos, constância e cuidado diário.",
    "consulta_cfbm": "https://cfbm-br.implanta.net.br/visaonacional/publico/consulta-publica/index",
}

# Prova social -------------------------------------------------------------------

DEPOIMENTO_VIDEO = {
    "texto": "Muita dor, muita dor que eu sentia, muita inflamação. Hoje eu não estou sentindo mais dor nas minhas costas, igual eu sentia, nem dor na coluna, nem nas pernas.",
    "quem": "Paciente que tratou dores no corpo na clínica",
    "link": "https://www.instagram.com/stories/highlights/18144478291128729/",
}

WHATSAPP = [
    {"titulo": "Vai além de uma simples limpeza", "texto": "Minha limpeza de pele foi maravilhosa, vai além de uma simples limpeza, mas sim uma experiência maravilhosa de autocuidado", "hora": "14:25", "quem": "Marcela, limpeza de pele", "tratamento": "limpeza-de-pele"},
    {"titulo": "Estou encantada", "texto": "Olha o capricho da clínica Empatia Humana. Atendimento de excelência com muito carinho e atenção para seus pacientes. Estou encantada 😍", "hora": "", "quem": "Mávila, depois da consulta integrativa", "tratamento": "consulta-integrativa"},
    {"titulo": "Seu atendimento é excelente", "texto": "Como faz pra elogiar vc, tipo seu atendimento é excelente", "hora": "08:45", "quem": "Paciente da clínica", "tratamento": ""},
    {"titulo": "Uma noite de sono direta", "texto": "Eu amei o chá, tive uma noite de sono \"direta\" 😴❤️", "hora": "10:00", "quem": "Larissa, sobre o Mix Calmante", "tratamento": ""},
]

GOOGLE = [
    ("Gisele R.", "Atendimento. Recepção. Organização. Higiene do ambiente tudo ótimo"),
    ("Mayra L.", "O ambiente é super aconchegante, a atenção dada é maravilhosa 💖"),
    ("Juliane A.", "Ótimo atendimento, amei o resultado… incrível"),
    ("Marcos Z.", "Atendimento nota 10, procedimento que eu fiz fiquei muito satisfeito."),
    ("Aurora F.", "A segurança, o conhecimento e a dedicação, tudo leva a gente a confiar. Parabéns."),
    ("Daiane S.", "Espaço maravilhoso e aconchegante! Excelentes profissionais ❣️"),
    ("Lucivania T.", "Foi ótimo, é sempre bem recebida, um lugar de paz"),
    ("Fernandes S.", "Minha experiência foi ótima, tirou todas as minhas dúvidas, gostei muito"),
    ("Viviane C.", "Atendimento maravilhoso, super indico"),
    ("Nubia S.", "O local é muito aconchegante, a atendente é super educada"),
    ("Flaviana O.", "O óleo de girassol ozonizado já faz parte da minha vida. Uso e sempre recomendo para as amigas."),
    ("Maria da C.", "Abençoado 🙏 gratidão pelo acolhimento de todos da Empatia Humana."),
]

# Resumo de cada tratamento (aparece logo depois do topo da página e é o que buscadores com IA citam)
RESUMOS = {
    "vasinhos-e-varizes": "O PEIM (Procedimento Estético Injetável para Microvasos) trata vasinhos e microvarizes das pernas com aplicações de agulha fina dentro dos vasos, que vão sendo reabsorvidos nas semanas seguintes. É feito na clínica, sem cortes e sem internação, em sessões definidas na avaliação. Varizes grossas pedem avaliação de angiologista.",
    "ozonioterapia": "A ozonioterapia é uma terapia complementar que aplica uma mistura de oxigênio e ozônio medicinal, em dose controlada, para ajudar a controlar a inflamação e a dor. Na Empatia Humana é usada em dores crônicas da coluna, joelhos, ombros e outras articulações, por via local, auricular, com ventosa ou em soro. É autorizada no Brasil pela Lei nº 14.648/2023.",
    "lipo-ozonizada": "A lipo ozonizada é a aplicação de ozônio na gordura localizada com agulhas finas, em sessões, sem cortes e sem internação. É indicada para regiões como barriga, flancos e culote que respondem pouco à dieta e ao treino, e pode ser combinada com hidrolipoclasia e drenagem.",
    "consulta-integrativa": "A consulta de estética integrativa é uma consulta longa em que a biomédica analisa sua história, seus sintomas e seus exames laboratoriais e entrega por escrito o mapeamento do caso, com o plano de tratamento. É indicada para quem tem cansaço, inchaço, problemas de pele ou intestino com exames considerados normais.",
    "saude-intestinal": "O cuidado intestinal da Empatia Humana combina avaliação dos exames com o Programa Disbiose Zero (5 ou 10 sessões), enema de café, Desafio Detox de 7 dias, massagem visceral e ozônio retal, conforme o caso. O objetivo é reduzir inchaço e desconforto e regular o intestino.",
    "limpeza-de-pele": "A limpeza de pele profunda remove cravos, impurezas e células mortas e costuma ser repetida a cada um ou dois meses. Na Empatia Humana, o cuidado facial inclui também peelings (químico, de cristal e ozonizado), microagulhamento, skinbooster e tratamento de melasma.",
    "soroterapia": "A soroterapia é a reposição de vitaminas e minerais por via intramuscular ou em soro, incluindo o soro ozonizado, indicada a partir dos exames laboratoriais. É usada para cansaço persistente, queda de cabelo, unhas fracas e deficiências identificadas nos exames.",
}

# Página para quem vem de Parauapebas (SEO local da cidade vizinha)
PARAUAPEBAS = {
    "faq": [
        ("A clínica atende pacientes de Parauapebas?", "Sim. Muitas pacientes vêm de Parauapebas, Curionópolis e cidades vizinhas para os tratamentos da Empatia Humana, no Centro de Canaã dos Carajás."),
        ("Dá para fazer avaliação e tratamento no mesmo dia?", "Em muitos casos, sim. Quando você marca pelo WhatsApp, avise que vem de Parauapebas: a equipe organiza a agenda para aproveitar a viagem."),
        ("A clínica atende no sábado?", "Sim, aos sábados das 8h às 12h. De segunda a sexta, das 8h às 12h e das 14h às 18h."),
        ("Onde fica a clínica?", "Na Rua Círio de Nazaré, 558, salas 1 e 2, no Centro de Canaã dos Carajás. O link do Google Maps está nesta página."),
    ],
}

# Tratamentos ----------------------------------------------------------------------
# Cada um vira uma página em /tratamentos/<slug>/ (estrutura inspirada nas páginas de procedimento da draotorrino.com.br).

TRATAMENTOS = [
    {
        "slug": "vasinhos-e-varizes",
        "nome": "Vasinhos e varizes",
        "menu": "Vasinhos e varizes (PEIM)",
        "icone": "perna",
        "card": "PEIM integrativo para vasinhos e microvarizes, sem cortes.",
        "destaque": "PEIM para vasinhos e microvarizes, sem cortes. Parcelamento em até 10x.",
        "seo_title": "Tratamento de vasinhos em Canaã dos Carajás | Empatia Humana",
        "meta": "Tratamento de vasinhos e microvarizes com PEIM em Canaã dos Carajás (PA). Avaliação das pernas com a biomédica Dra. Adelaine Montel. Parcelamento em até 10x.",
        "h1": "Tratamento de vasinhos e varizes em Canaã dos Carajás",
        "sub": "Suas pernas foram feitas para aparecer, não para ficar escondidas debaixo da calça.",
        "chips": ["Vasinhos vermelhos ou roxos", "Vergonha de usar short ou saia", "Pernas pesadas no fim do dia", "Vasinhos novos a cada verão"],
        "ident_titulo": "Usar short no calor de Canaã não deveria ser uma decisão difícil.",
        "ident": [
            "Talvez você já tenha escolhido a calça no lugar do vestido só por causa deles. Os vasinhos aparecem aos poucos, nas coxas, atrás dos joelhos, perto dos tornozelos. Um dia, viram o motivo de esconder as pernas.",
        ],
        "reframe": "Não precisa ser assim. Vasinhos e microvarizes têm tratamento, sem cortes, e ele começa por uma avaliação das suas pernas.",
        "oque_titulo": "O que o PEIM faz por você?",
        "oque_intro": "PEIM é o Procedimento Estético Injetável para Microvasos. Com uma agulha bem fina, a Dra. Adelaine aplica uma solução dentro dos vasinhos, que vão fechando e sendo reabsorvidos pelo corpo nas semanas seguintes. Na Empatia Humana ele é integrativo: a avaliação olha também para circulação e hábitos, para que novos vasinhos demorem mais a aparecer.",
        "beneficios": ["Pernas com aparência mais uniforme", "Liberdade para usar short, saia e biquíni", "Sem cortes e sem internação: você volta para casa no mesmo dia"],
        "como": [
            ("Avaliação das pernas", "A Dra. Adelaine examina os vasinhos, entende sua rotina e diz com clareza se o seu caso é para o PEIM."),
            ("Aplicação", "Picadas rápidas com agulha bem fina, direto nos vasinhos. A sessão é feita na clínica, sem anestesia geral."),
            ("Sessões", "O número de sessões e o intervalo entre elas são definidos na avaliação, conforme a quantidade de vasinhos."),
            ("Cuidados depois", "Evitar sol direto nas áreas tratadas por alguns dias e seguir as orientações de cuidado em casa."),
        ],
        "sinais": ["Quando os vasinhos já decidem a roupa que você vai usar.", "Quando aparecem vasinhos novos a cada verão.", "Quando você quer as pernas bonitas para uma viagem, uma festa ou para o dia a dia."],
        "ganho_titulo": "Pernas à mostra, sem pensar duas vezes.",
        "ganho": "O objetivo é simples: você voltar a escolher a roupa pelo que gosta, e não pelo que esconde.",
        "aviso": "Varizes grossas, dor forte ou inchaço importante nas pernas pedem avaliação de um angiologista. Na avaliação, a Dra. Adelaine orienta quando é o caso.",
        "inclui": ["PEIM integrativo", "Ozônio para microvasos", "Avaliação das pernas", "Parcelamento em até 10x"],
        "faq": [
            ("O PEIM dói?", "A agulha é bem fina. A maioria das pacientes sente uma ardência leve e rápida durante a aplicação, e segue o dia normalmente."),
            ("Quantas sessões vou precisar?", "Depende da quantidade e do tipo de vasinhos. A Dra. Adelaine define o número de sessões na avaliação, antes de você começar."),
            ("Quando os vasinhos somem?", "Eles vão clareando aos poucos nas semanas seguintes a cada sessão. O corpo leva um tempo para reabsorver o vaso tratado."),
            ("Os vasinhos voltam?", "O vasinho tratado tende a não voltar, mas novos podem surgir com o tempo. Por isso o tratamento integrativo também cuida dos hábitos que favorecem o aparecimento."),
            ("Dá para parcelar?", "Sim. O tratamento de vasinhos pode ser parcelado em até 10x. A equipe passa os valores pelo WhatsApp."),
        ],
        "foto": "avaliacao-pernas",
        "foto_alt": "Dra. Adelaine Montel examinando as pernas de uma paciente na maca",
        "interesse": "tratamento de vasinhos",
        "posts": ["vasinhos-nas-pernas-causas-e-tratamento"],
    },
    {
        "slug": "ozonioterapia",
        "nome": "Ozonioterapia para dor",
        "menu": "Ozonioterapia para dor",
        "icone": "ozonio",
        "card": "Terapia complementar para dores crônicas na coluna, joelhos e articulações.",
        "seo_title": "Ozonioterapia para dor em Canaã dos Carajás | Empatia Humana",
        "meta": "Ozonioterapia para dor na coluna, joelhos e articulações em Canaã dos Carajás (PA), com a biomédica e ozonioterapeuta Dra. Adelaine Montel. Agende.",
        "h1": "Ozonioterapia para dor em Canaã dos Carajás",
        "sub": "Dor não é parte da idade. E não precisa ser parte da sua rotina.",
        "chips": ["Dor na coluna e na lombar", "Joelho que dói na escada", "Ombro travado", "Dor que volta quando o remédio passa"],
        "ident_titulo": "Viver tomando remédio para dor não é viver bem.",
        "ident": [
            "Você acorda e a primeira coisa que sente é a lombar. Subir a escada virou cálculo. O analgésico resolve por umas horas, e a dor volta no fim do dia, todo dia.",
        ],
        "reframe": "A ozonioterapia é uma terapia complementar usada para ajudar a controlar a inflamação e a dor. Foi o que mudou a vida da própria Dra. Adelaine, e hoje é a especialidade da clínica.",
        "oque_titulo": "O que a ozonioterapia faz por você?",
        "oque_intro": "O ozônio medicinal é uma mistura de oxigênio e ozônio feita por um equipamento próprio e aplicada em doses controladas. Na dor, ele é aplicado perto da região que dói ou por outras vias, conforme o caso, para ajudar o corpo a reduzir a inflamação.",
        "beneficios": ["Menos dor para fazer o que você gosta", "Mais movimento e disposição no dia a dia", "Um tratamento complementar ao do seu médico, sem cirurgia"],
        "como": [
            ("Avaliação", "Onde dói, há quanto tempo, o que você já tentou e quais exames tem. A Dra. Adelaine diz se a ozonioterapia é indicada para você."),
            ("Aplicação", "Ozônio local (pequenas aplicações na região), auricular, com ventosa ou em soro, conforme o seu caso."),
            ("Sessões", "O protocolo e o número de sessões são definidos na avaliação e ajustados conforme a resposta do seu corpo."),
            ("Acompanhamento", "A cada sessão, a Dra. Adelaine acompanha a evolução da dor e ajusta o plano."),
        ],
        "sinais": ["Quando a dor já dura mais de três meses.", "Quando você já tentou remédio e fisioterapia e a dor voltou.", "Quando você quer um tratamento complementar, sem cirurgia."],
        "ganho_titulo": "Voltar a se mexer sem pensar na dor.",
        "ganho": "Levantar da cama, pegar o neto no colo, caminhar sem planejar cada passo. É isso que a ozonioterapia busca devolver.",
        "aviso": "A ozonioterapia é autorizada no Brasil como procedimento complementar pela Lei nº 14.648/2023 e não substitui o acompanhamento médico.",
        "inclui": ["Ozônio local", "Ozônio auricular", "Ozonioterapia com ventosa", "Soro ozonizado", "Óleo de girassol ozonizado"],
        "faq": [
            ("A ozonioterapia é segura?", "Feita por profissional habilitada, com equipamento regularizado e dose controlada, é um procedimento de baixo risco. O efeito mais comum é um desconforto leve e passageiro no local da aplicação."),
            ("A aplicação dói?", "No ozônio local há uma picada e uma sensação de pressão por alguns segundos. Nas outras vias, como a auricular e a com ventosa, o desconforto é menor."),
            ("Em quantas sessões começo a sentir diferença?", "Varia de pessoa para pessoa e do tipo de dor. O número de sessões é definido na avaliação, e a evolução é acompanhada a cada encontro."),
            ("Substitui o meu tratamento médico?", "Não. A ozonioterapia é complementar e pode caminhar junto com o acompanhamento do seu médico."),
            ("A ozonioterapia é regulamentada?", "Sim. A Lei nº 14.648/2023 autoriza a ozonioterapia como procedimento complementar, e a Dra. Adelaine tem a habilitação em Ozonioterapia registrada no CRBM."),
        ],
        "foto": "clinica-emblema",
        "foto_alt": "Dra. Adelaine Montel na clínica, em frente ao emblema da árvore da Empatia Humana",
        "interesse": "ozonioterapia para dor",
        "posts": ["ozonioterapia-o-que-e-para-que-serve"],
        "depoimento_video": True,
    },
    {
        "slug": "lipo-ozonizada",
        "nome": "Lipo ozonizada",
        "menu": "Lipo ozonizada (gordura localizada)",
        "icone": "cintura",
        "card": "Gordura localizada tratada direto na região, sem cortes.",
        "seo_title": "Lipo ozonizada em Canaã dos Carajás | Empatia Humana",
        "meta": "Lipo ozonizada para gordura localizada em Canaã dos Carajás (PA): sem cortes e sem internação, com avaliação da biomédica Dra. Adelaine Montel. Agende.",
        "h1": "Lipo ozonizada para gordura localizada em Canaã dos Carajás",
        "sub": "Para aquela gordura que não sai nem com dieta, nem com treino.",
        "chips": ["Barriga que não diminui", "Culote e flancos", "Calça apertando no mesmo lugar", "Treino em dia, medida igual"],
        "ident_titulo": "Você faz tudo certo. E ela continua lá.",
        "ident": [
            "Come melhor, treina, perde peso, e aquela região não muda. A barriga, os flancos, o culote. A roupa continua apertando no mesmo lugar e a foto de lado continua incomodando.",
        ],
        "reframe": "Não é falta de esforço. A gordura localizada responde pouco à dieta. A lipo ozonizada trata a região direto, sem cortes e sem internação.",
        "oque_titulo": "O que a lipo ozonizada faz por você?",
        "oque_intro": "É a aplicação de ozônio na gordura localizada, com agulhas finas, em sessões. O ozônio age nas células de gordura da região tratada, que o corpo vai eliminando aos poucos. Quando indicado, o plano combina hidrolipoclasia, drenagem e cuidados em casa.",
        "beneficios": ["Tratamento da região que mais incomoda", "Sem cortes, sem anestesia geral e sem internação", "Você volta para a rotina no mesmo dia"],
        "como": [
            ("Avaliação", "A Dra. Adelaine avalia a região, sua rotina e seus objetivos, e diz se a lipo ozonizada é indicada para você."),
            ("Aplicação", "Aplicações com agulhas finas na gordura localizada. A sessão é feita na clínica e leva pouco tempo."),
            ("Sessões", "O número de sessões e o intervalo entre elas são definidos na avaliação, conforme a região."),
            ("Cuidados", "Orientações de alimentação, hidratação e atividade física para potencializar o tratamento."),
        ],
        "sinais": ["Quando a dieta e o treino já não mudam aquela região.", "Quando a roupa aperta sempre no mesmo lugar.", "Quando você quer reduzir medidas sem cirurgia."],
        "ganho_titulo": "A roupa servindo do jeito que você quer.",
        "ganho": "Menos medida na região que incomoda e mais vontade de se olhar no espelho de lado.",
        "aviso": "Gestantes, lactantes e pessoas com deficiência de G6PD (favismo), entre outros casos, não fazem ozonioterapia. Por isso a avaliação vem sempre antes.",
        "inclui": ["Lipo ozonizada", "Hidrolipoclasia (lipo sem corte)", "Programa de redução de medidas", "Drenagem linfática"],
        "faq": [
            ("A lipo ozonizada dói?", "A sensação é de ardência e pressão durante as aplicações, por pouco tempo. Depois, a região pode ficar sensível por um ou dois dias."),
            ("Quantas sessões são necessárias?", "Depende da região e da quantidade de gordura. A Dra. Adelaine define o plano na avaliação."),
            ("Quando começo a ver diferença?", "A redução é gradual e aparece ao longo das sessões. Medir a região no começo ajuda a acompanhar a evolução."),
            ("Preciso fazer dieta?", "Não é uma dieta restritiva, mas os hábitos fazem diferença no resultado. Você recebe orientações para potencializar o tratamento."),
            ("Quem não pode fazer?", "Gestantes, lactantes e pessoas com deficiência de G6PD (favismo), entre outros casos. A avaliação confirma se você pode fazer."),
        ],
        "foto": "recepcao",
        "foto_alt": "Recepção da Clínica Empatia Humana em Canaã dos Carajás",
        "interesse": "lipo ozonizada",
        "posts": ["lipo-ozonizada-como-funciona"],
    },
    {
        "slug": "consulta-integrativa",
        "nome": "Consulta de estética integrativa",
        "menu": "Consulta de estética integrativa",
        "icone": "lupa",
        "card": "Seus exames lidos com detalhe e um plano por escrito para o seu caso.",
        "seo_title": "Consulta integrativa em Canaã dos Carajás | Empatia Humana",
        "meta": "Consulta de estética integrativa em Canaã dos Carajás (PA): análise detalhada dos seus exames e um plano por escrito com a biomédica Dra. Adelaine Montel.",
        "h1": "Consulta de estética integrativa em Canaã dos Carajás",
        "sub": "Seus exames estão normais. Mas você sabe que alguma coisa não está.",
        "chips": ["Cansaço que não passa", "Inchaço e intestino preso", "Pele e cabelo sem vida", "Exames \"normais\""],
        "ident_titulo": "Ouvir que está tudo bem não resolve o que você sente.",
        "ident": [
            "Você faz os exames, ouve que está tudo dentro da referência e volta para casa do mesmo jeito: cansada, inchada, com a pele piorando e sem entender o porquê.",
        ],
        "reframe": "Na estética integrativa, o que aparece na pele, no peso e na disposição é lido junto com o que acontece por dentro. É aí que muitos casos começam a fazer sentido.",
        "oque_titulo": "O que a consulta integrativa faz por você?",
        "oque_intro": "É uma consulta sem pressa. A Dra. Adelaine ouve sua história, analisa seus exames com o olhar de quem tem formação em análises clínicas e nutrição ortomolecular, e entrega por escrito o mapeamento do seu caso, com o plano proposto.",
        "beneficios": ["Entender o porquê, e não só tratar o sintoma", "Um plano por escrito, feito para o seu corpo", "Os tratamentos indicados na ordem certa"],
        "como": [
            ("Antes", "Separe seus exames recentes. Se faltar algum importante, a Dra. Adelaine pede."),
            ("Na consulta", "Sua história, sua rotina, seus sintomas e seus exames, lidos com calma."),
            ("O mapeamento", "Você recebe por escrito o estudo do seu caso, com o que foi encontrado."),
            ("O plano", "Tratamentos da clínica, cuidados em casa e, quando necessário, a orientação de procurar outro especialista."),
        ],
        "sinais": ["Quando os exames vêm normais, mas o corpo diz outra coisa.", "Quando você já tratou o sintoma várias vezes e ele volta.", "Quando quer um plano completo, e não um procedimento solto."],
        "ganho_titulo": "Sair da consulta entendendo o seu corpo.",
        "ganho": "Com o mapeamento em mãos, você sabe o que está acontecendo, o que fazer primeiro e por quê.",
        "aviso": "A consulta integrativa não substitui o acompanhamento médico. Quando necessário, a Dra. Adelaine orienta procurar o especialista.",
        "inclui": ["Análise detalhada de exames laboratoriais", "Mapeamento do caso por escrito", "Plano integrativo", "Orientações de alimentação e suplementação"],
        "faq": [
            ("Preciso levar exames?", "Se você tiver exames recentes, leve. Se faltar algum importante para o seu caso, a Dra. Adelaine pede na consulta."),
            ("O que eu recebo no fim?", "O mapeamento do seu caso por escrito, com o que foi encontrado e o plano proposto, na ordem em que faz sentido começar."),
            ("A consulta é com médico?", "Não. A consulta é com a biomédica Dra. Adelaine Montel, que tem formação em análises clínicas e nutrição ortomolecular. Ela não substitui o seu médico e orienta quando é preciso procurar um."),
            ("Já sai com algum tratamento marcado?", "Você sai com o plano. Os tratamentos são marcados com a equipe, no seu tempo."),
        ],
        "foto": "adelaine-consultorio",
        "foto_alt": "Dra. Adelaine Montel de jaleco branco no consultório",
        "interesse": "consulta de estética integrativa",
        "posts": ["estetica-integrativa-o-que-e"],
    },
    {
        "slug": "saude-intestinal",
        "nome": "Saúde intestinal e detox",
        "menu": "Saúde intestinal e detox",
        "icone": "intestino",
        "card": "Programa Disbiose Zero, enema de café e Desafio Detox.",
        "seo_title": "Saúde intestinal e detox em Canaã dos Carajás | Empatia Humana",
        "meta": "Barriga inchada, intestino preso e cansaço? Programa Disbiose Zero, enema de café e detox em Canaã dos Carajás (PA), com a Dra. Adelaine Montel.",
        "h1": "Saúde intestinal e detox em Canaã dos Carajás",
        "sub": "Barriga inchada todo dia não é normal. É um sinal.",
        "chips": ["Barriga inchada", "Intestino preso", "Gases e desconforto", "Cansaço e pele que piora"],
        "ident_titulo": "Você se acostumou a se sentir estufada.",
        "ident": [
            "A calça que fecha de manhã aperta à tarde. O intestino funciona quando quer. O cansaço não passa e a pele parece responder a tudo. Com o tempo, isso vira o seu normal.",
        ],
        "reframe": "Não é o seu normal. O intestino conversa com a pele, com o humor e com a disposição. Quando ele volta ao equilíbrio, o resto sente.",
        "oque_titulo": "O que o cuidado intestinal faz por você?",
        "oque_intro": "O cuidado começa pela avaliação e pelos seus exames. A partir deles, a Dra. Adelaine monta o protocolo: o Programa Disbiose Zero, em 5 ou 10 sessões, o enema de café, o Desafio Detox de 7 dias, a massagem visceral e outras terapias, combinadas com orientações para casa.",
        "beneficios": ["Menos inchaço e desconforto na barriga", "Intestino funcionando com regularidade", "Mais disposição, e uma pele que acompanha"],
        "como": [
            ("Avaliação", "Sua rotina, sua alimentação, seus sintomas e seus exames."),
            ("Protocolo", "Disbiose Zero, enema de café, detox ou massagem visceral, na combinação indicada para você."),
            ("Em casa", "Orientações simples de alimentação e hábitos para manter o resultado."),
            ("Acompanhamento", "Revisão do plano ao longo das sessões."),
        ],
        "sinais": ["Quando a barriga incha quase todos os dias.", "Quando o intestino só funciona com remédio ou chá.", "Quando cansaço e pele ruim aparecem junto com o desconforto."],
        "ganho_titulo": "Leveza do café da manhã até a hora de dormir.",
        "ganho": "Acordar e terminar o dia sem a barriga estufada, com energia e com o intestino no ritmo.",
        "aviso": "Sangue nas fezes, perda de peso sem motivo, febre ou dor forte pedem avaliação médica. A Dra. Adelaine orienta quando é o caso.",
        "inclui": ["Programa Disbiose Zero (5 ou 10 sessões)", "Enema de café", "Desafio Detox de 7 dias", "Massagem visceral", "Ozônio retal"],
        "faq": [
            ("O que é disbiose?", "É o desequilíbrio das bactérias do intestino. Ele pode aparecer como inchaço, gases, intestino preso ou solto, cansaço e piora da pele."),
            ("O enema de café dói?", "Não. É um procedimento feito com calma, em sala reservada, com orientação em cada etapa."),
            ("Quantas sessões tem o Disbiose Zero?", "O programa tem versões de 5 ou 10 sessões. A Dra. Adelaine indica a mais adequada na avaliação."),
            ("Vou precisar mudar a alimentação?", "Você recebe orientações simples e possíveis para a sua rotina. Elas ajudam a manter o que foi conquistado nas sessões."),
        ],
        "foto": "adelaine-vertical-540",
        "foto_alt": "Dra. Adelaine Montel sorrindo na Clínica Empatia Humana",
        "interesse": "saúde intestinal",
        "posts": ["disbiose-intestinal-sinais-e-cuidados"],
    },
    {
        "slug": "limpeza-de-pele",
        "nome": "Limpeza de pele e tratamentos faciais",
        "menu": "Limpeza de pele e rosto",
        "icone": "rosto",
        "card": "Limpeza profunda, peelings, microagulhamento e melasma.",
        "seo_title": "Limpeza de pele em Canaã dos Carajás | Empatia Humana",
        "meta": "Limpeza de pele profunda, peelings, microagulhamento e tratamento de melasma em Canaã dos Carajás (PA), com a biomédica esteta Dra. Adelaine Montel.",
        "h1": "Limpeza de pele e tratamentos faciais em Canaã dos Carajás",
        "sub": "Uma pele que você não precisa esconder com base.",
        "chips": ["Cravos e poros dilatados", "Oleosidade e espinhas", "Manchas e melasma", "Pele sem viço"],
        "ident_titulo": "Maquiagem não deveria ser obrigatória para sair de casa.",
        "ident": [
            "Os cravos voltam, a oleosidade aparece no meio da tarde, as manchas ficam mais escuras depois do sol. E a base virou a forma de não pensar nisso.",
        ],
        "reframe": "Pele bonita é pele cuidada com regularidade. A limpeza de pele costuma ser o primeiro passo, e o cuidado segue com o tratamento certo para o que incomoda você.",
        "oque_titulo": "O que os tratamentos faciais fazem por você?",
        "oque_intro": "A limpeza de pele profunda tira cravos e impurezas e prepara a pele para os ativos. A partir dela, a Dra. Adelaine indica peelings, microagulhamento, skinbooster ou o protocolo para melasma, conforme a sua pele.",
        "beneficios": ["Poros mais limpos e menos oleosidade", "Pele mais uniforme e com viço", "Um momento de autocuidado só seu"],
        "como": [
            ("Avaliação da pele", "Tipo de pele, o que incomoda e a sua rotina de cuidados."),
            ("Limpeza profunda", "Higienização, esfoliação, extração de cravos, máscara e hidratação."),
            ("Tratamento", "Peelings, microagulhamento, skinbooster ou protocolo de melasma, quando indicados."),
            ("Em casa", "Orientações de skincare e protetor solar para manter o resultado."),
        ],
        "sinais": ["Quando os cravos voltam rápido.", "Quando as manchas escurecem a cada verão.", "Quando a pele perdeu o brilho e a maquiagem não resolve mais."],
        "ganho_titulo": "Sair de casa de cara limpa, com segurança.",
        "ganho": "Uma pele mais uniforme, que você tem vontade de mostrar.",
        "aviso": "",
        "inclui": ["Limpeza de pele profunda", "Peeling químico, de cristal e ozonizado", "Microagulhamento", "Skinbooster", "Tratamento de melasma", "Retirada de acrocórdons e siringomas"],
        "faq": [
            ("De quanto em quanto tempo devo fazer limpeza de pele?", "Para a maioria das peles, a cada um ou dois meses. Peles mais oleosas costumam pedir intervalos menores. A indicação é feita na avaliação."),
            ("A pele fica vermelha depois?", "Pode ficar levemente avermelhada por algumas horas, principalmente onde houve extração. Em geral, no dia seguinte já está normal."),
            ("Posso fazer peeling no verão?", "Alguns peelings podem ser feitos o ano todo, com protetor solar rigoroso. A Dra. Adelaine indica o tipo certo para a época e para a sua pele."),
            ("Microagulhamento dói?", "É feito com anestésico tópico, o que deixa o procedimento bem tolerável."),
        ],
        "foto": "adelaine-retrato",
        "foto_alt": "Retrato da Dra. Adelaine Montel sorrindo",
        "interesse": "limpeza de pele",
        "posts": ["limpeza-de-pele-de-quanto-em-quanto-tempo"],
        "depoimento_whats": "limpeza-de-pele",
    },
    {
        "slug": "soroterapia",
        "nome": "Soroterapia e vitaminas",
        "menu": "Soroterapia e vitaminas",
        "icone": "gota",
        "card": "Reposição de vitaminas indicada a partir dos seus exames.",
        "seo_title": "Soroterapia em Canaã dos Carajás | Empatia Humana",
        "meta": "Soroterapia e vitaminas injetáveis em Canaã dos Carajás (PA), indicadas a partir dos seus exames pela biomédica Dra. Adelaine Montel. Agende sua avaliação.",
        "h1": "Soroterapia e vitaminas injetáveis em Canaã dos Carajás",
        "sub": "Para quando o cansaço já faz parte de quem você é.",
        "chips": ["Cansaço o dia inteiro", "Queda de cabelo", "Unhas fracas", "Imunidade baixa"],
        "ident_titulo": "Dormir não está resolvendo o seu cansaço.",
        "ident": [
            "Você acorda cansada, chega ao fim da tarde sem energia e sente que o corpo não acompanha a rotina. O cabelo cai mais, as unhas quebram, e qualquer gripe pega.",
        ],
        "reframe": "Às vezes falta o básico: vitaminas e minerais que o corpo não está absorvendo bem. A reposição certa começa pelos seus exames.",
        "oque_titulo": "O que a soroterapia faz por você?",
        "oque_intro": "A partir dos seus exames, a Dra. Adelaine indica a reposição de vitaminas e minerais por via injetável (intramuscular) ou em soro, incluindo o soro ozonizado, com a dose e a frequência certas para você.",
        "beneficios": ["Reposição indicada pelos seus exames", "Absorção pela via injetável", "Mais energia para a rotina"],
        "como": [
            ("Avaliação e exames", "A indicação parte dos seus exames e dos seus sintomas."),
            ("Aplicação", "Vitaminas intramusculares ou soro, feitos na clínica."),
            ("Frequência", "O número de aplicações é definido conforme o seu caso."),
            ("Reavaliação", "Novos exames mostram a evolução e ajustam o plano."),
        ],
        "sinais": ["Quando o cansaço não melhora com descanso.", "Quando os exames mostram vitaminas baixas.", "Quando cabelo, unhas e imunidade dão sinais ao mesmo tempo."],
        "ganho_titulo": "Energia para dar conta do seu dia.",
        "ganho": "Acordar descansada e chegar ao fim do dia com disposição.",
        "aviso": "",
        "inclui": ["Vitaminas injetáveis (IM)", "Soroterapia", "Soro ozonizado"],
        "faq": [
            ("Preciso de exames para fazer?", "Sim. A reposição é indicada a partir dos seus exames, para dar ao corpo o que realmente está faltando."),
            ("A aplicação dói?", "É uma picada, como a de qualquer injeção. O soro é feito com você sentada, de forma confortável."),
            ("Quantas aplicações vou precisar?", "Depende do que os exames mostram. A frequência é definida na avaliação e revista nos exames seguintes."),
        ],
        "foto": "adelaine-retrato",
        "foto_alt": "Dra. Adelaine Montel sorrindo na Clínica Empatia Humana",
        "interesse": "soroterapia e vitaminas",
        "posts": [],
    },
]

OUTROS_SERVICOS = ["Massagem relaxante", "Drenagem linfática", "Massagem visceral", "Retirada de acrocórdons e siringomas", "Óleo de girassol ozonizado"]

# Quando procurar (atalhos da home, como o "Quando procurar um otorrino?")
SINTOMAS = [
    ("Vasinhos nas pernas", "vasinhos-e-varizes"),
    ("Dor na coluna", "ozonioterapia"),
    ("Dor no joelho", "ozonioterapia"),
    ("Gordura localizada", "lipo-ozonizada"),
    ("Barriga inchada", "saude-intestinal"),
    ("Intestino preso", "saude-intestinal"),
    ("Cravos e oleosidade", "limpeza-de-pele"),
    ("Manchas e melasma", "limpeza-de-pele"),
    ("Cansaço que não passa", "soroterapia"),
    ("Exames \"normais\"", "consulta-integrativa"),
]

# Dúvidas da home (quebra de objeções)
FAQ_HOME = [
    ("A avaliação é paga?", "A avaliação para procedimentos, como vasinhos, ozonioterapia, lipo ozonizada e pele, é sem custo. A consulta de estética integrativa, com análise detalhada dos exames e o mapeamento do caso por escrito, tem valor à parte. A equipe confirma tudo pelo WhatsApp."),
    ("Quanto custa?", "O valor do tratamento depende do seu caso, e a equipe passa pelo WhatsApp logo depois que você deixar seu contato. O tratamento de vasinhos pode ser parcelado em até 10x."),
    ("Dói?", "A maioria dos procedimentos é feita com agulhas finas e causa só um desconforto rápido. Em cada página de tratamento você encontra como é a sensação, contada sem rodeio."),
    ("Quem vai me atender?", "A própria Dra. Adelaine Montel, biomédica esteta e ozonioterapeuta, com inscrição ativa no CRBM 4ª Região (nº 1437) desde 2011."),
    ("É seguro?", "Os procedimentos são feitos por profissional habilitada, em ambiente de clínica, com material descartável e avaliação antes de qualquer indicação. Se o tratamento não for para você, ela diz."),
    ("Homens também são atendidos?", "Sim. Dor, vasinhos, gordura localizada, pele e intestino são tratados em homens e mulheres."),
    ("Atendem quem é de Parauapebas e da região?", "Sim. Muitas pacientes vêm de Parauapebas, Curionópolis e cidades vizinhas. A clínica fica no Centro de Canaã dos Carajás e atende com horário marcado, inclusive aos sábados de manhã."),
    ("Como confiro o registro da Dra. Adelaine?", "Na consulta pública do Conselho Federal de Biomedicina: busque por Adelaine Barros Montel e veja a inscrição nº 1437 no CRBM 4ª Região, ativa."),
]

# Entram no fim do FAQ de toda página de tratamento
FAQ_TRATAMENTO_COMUM = [
    ("Quanto custa?", "Depende do seu caso e do plano definido na avaliação. A equipe passa os valores pelo WhatsApp logo depois que você deixar seu contato, e vários tratamentos podem ser parcelados."),
    ("Atendem quem é de Parauapebas e da região?", "Sim. Muitas pacientes vêm de Parauapebas, Curionópolis e cidades vizinhas. A clínica fica no Centro de Canaã dos Carajás e atende com horário marcado, inclusive aos sábados de manhã."),
]

CURSOS = [
    {
        "nome": "Interpretação de Exames Laboratoriais",
        "texto": "Para biomédicos, enfermeiros, farmacêuticos, nutricionistas, médicos e estudantes da saúde. Estudo de casos reais, material didático e certificado.",
    },
    {
        "nome": "Ozonioterapia na Dor Crônica",
        "texto": "Masterclass com protocolos de ozônio para dor crônica, associados à desparasitação e à detoxificação.",
        "link": "https://docs.google.com/forms/d/e/1FAIpQLSdvhjEHF39O0No7VtuDPsRw9sGWVJ1twP9jyYrRoTB4givw0w/viewform",
    },
    {
        "nome": "Limpeza de Pele",
        "texto": "Curso prático para quem quer oferecer limpeza de pele com técnica, biossegurança e confiança.",
    },
]


# ====================================================================================
# Site v4 (identidade visual da marca): textos da home de vendas e das páginas institucionais
# ====================================================================================

SLOGAN = "Tratando de dentro para fora"

# A avaliação para procedimentos (vasinhos, ozonioterapia, lipo ozonizada e pele) é sem custo?
# True: aparece no topo da home, nas faixas e nas dúvidas. False: some de todos esses lugares.
AVALIACAO_SEM_CUSTO = True

# Hero da home (briefing, seção 5). Está em uso a versão 1, a mais bem avaliada em clareza, visão da paciente e regras.
HERO = {
    "headline": "Estética e saúde que começam <em>ouvindo você</em>.",
    "sub": "Pele, medidas, vasinhos e saúde integrativa com ozonioterapia, em Canaã dos Carajás. Nossas biomédicas avaliam você antes de indicar o tratamento.",
    "cta": "Agendar minha avaliação",
    "cta2": "Conhecer os tratamentos",
    "microprova": ["Avaliação gratuita", "Biomédicas ozonioterapeutas", "+400 pacientes atendidas"],
    "nota": "A avaliação gratuita leva cerca de 30 minutos e serve para indicar o procedimento. A Consulta Estética Integrativa, de 2 horas, tem valor à parte.",
    "whatsapp_msg": "Olá! Vim pelo site e quero agendar minha avaliação gratuita. Queria conversar sobre o meu caso.",
}
# Versão 2 (para teste A/B: tire o comentário das linhas abaixo)
# HERO["headline"] = "Estética que cuida de você <em>por inteiro</em>."
# HERO["sub"] = "Pele, medidas, vasinhos e saúde integrativa com ozonioterapia, no mesmo lugar. Com biomédicas que ouvem você, em Canaã dos Carajás."
# Versão 3
# HERO["headline"] = "Pele e corpo cuidados <em>de dentro para fora</em>."
# HERO["sub"] = "Por fora, pele, medidas e vasinhos; por dentro, saúde integrativa com ozonioterapia. Estética com biomédicas que ouvem você, em Canaã dos Carajás."

# Faixas em movimento logo abaixo do topo da home
FAIXA_1 = ["Ozonioterapia", "Vasinhos e varizes", "Lipo ozonizada", "Limpeza de pele", "Saúde intestinal", "Soroterapia", "Consulta integrativa"]
FAIXA_2 = ["De dentro para fora", "Vasinhos em até 10x", "Nota 5,0 no Google", "Segunda a sábado", "Centro de Canaã", "Dra. Adelaine Montel"]

# "Para quem é": cada linha leva à página do tratamento
IDENTIFICACAO = [
    ("Os vasinhos já decidem a roupa que você vai usar", "vasinhos-e-varizes"),
    ("A dor na coluna ou no joelho volta quando o remédio passa", "ozonioterapia"),
    ("A gordura localizada não sai nem com dieta e treino", "lipo-ozonizada"),
    ("A barriga incha todo dia e o cansaço não passa", "saude-intestinal"),
    ("Os exames estão normais, mas você não se sente bem", "consulta-integrativa"),
    ("Cravos e manchas voltam, e a base virou obrigação", "limpeza-de-pele"),
]

# Do primeiro contato ao plano
PASSOS = [
    ("Você chama no WhatsApp", "Toque em agendar e envie a mensagem que já vai pronta. A equipe combina o melhor horário."),
    ("Avaliação gratuita, sem pressa", "A biomédica ouve sua história, examina e, se você tiver, olha seus exames."),
    ("Plano sob medida", "Você sai sabendo qual tratamento é indicado, quantas sessões e como se cuidar em casa."),
    ("Sessões e acompanhamento", "Horário marcado, e a evolução revista a cada encontro."),
]

# Cartões de credencial da Dra. Adelaine: (ícone, título, texto)
CREDENCIAIS = [
    ("escudo", "CRBM 1437", "Inscrição ativa no CRBM 4ª Região (Pará)"),
    ("folha", "+18 anos de formada", "Biomédica esteta e ozonioterapeuta"),
    ("lupa", "Nutrição Ortomolecular", "Pós-graduada, com formação em análises clínicas"),
]

# Fotos do espaço: (arquivo, descrição, legenda)
ESPACO = [
    ("recepcao", "Recepção da Clínica Empatia Humana, com prateleiras de produtos e sofá", "Recepção", ""),
    ("fachada", "Fachada da clínica com o letreiro Empatia Humana", "Nossa fachada", "larga"),
    ("adelaine-consultorio", "Dra. Adelaine Montel de jaleco branco no consultório", "No consultório", ""),
]

# Página "A clínica"
CLINICA = {
    "desde": "2014",  # início de atividade no cadastro público do CNPJ
    "conceito": [
        "Empatia Humana é uma clínica de estética integrativa: aqui, a aparência é tratada junto com o que acontece por dentro do corpo. Antes de indicar um procedimento, a Dra. Adelaine quer entender a sua história, a sua rotina e, quando faz sentido, os seus exames.",
        "É por isso que o nosso lema é tratar de dentro para fora. O vasinho, a dor, a gordura localizada, a mancha e o inchaço são o que aparece. O cuidado começa pelo que está por trás.",
        "E o nome da clínica resume o jeito de atender: com empatia. Sem pressa, sem protocolo pronto e com explicação de cada etapa.",
    ],
    "valores": [
        ("Escuta antes do procedimento", "Toda paciente passa por avaliação. Se o tratamento não for para você, a gente diz."),
        ("O corpo inteiro", "Pele, circulação, intestino, vitaminas e hábitos entram na mesma conversa."),
        ("Formação e registro", "Atendimento com biomédica inscrita no CRBM, com habilitação em estética e ozonioterapia."),
        ("Acolhimento", "Ambiente tranquilo e atendimento com horário marcado, como as pacientes contam nas avaliações do Google."),
    ],
    "faq": [
        ("O que é a Empatia Humana?", "É uma clínica de estética integrativa e ozonioterapia no Centro de Canaã dos Carajás (PA), sob responsabilidade técnica da biomédica Dra. Adelaine Barros Montel, CRBM 4ª Região nº 1437."),
        ("Quais tratamentos a clínica oferece?", "Ozonioterapia para dor, tratamento de vasinhos e microvarizes (PEIM), lipo ozonizada, consulta de estética integrativa, saúde intestinal e detox, limpeza de pele e tratamentos faciais, soroterapia e vitaminas, além de massagem e drenagem linfática."),
        ("Onde fica e qual o horário?", "Na Rua Círio de Nazaré, 558, salas 1 e 2, Centro. Atende de segunda a sexta, das 8h às 12h e das 14h às 18h, e aos sábados das 8h às 12h, com horário marcado."),
    ],
}
