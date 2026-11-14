/**
 * @OnlyCurrentDoc
 * (Limita o acesso do script a esta planilha. Sem esta linha, o Google pediria acesso a todas as suas planilhas.)
 */

/**
 * Empatia Humana: recebe os pedidos de avaliação do site e grava na planilha.
 *
 * Como instalar (uma vez só):
 * 1. Crie uma planilha nova no Google Sheets (de preferência na conta da clínica).
 * 2. Menu Extensões > Apps Script. Apague o que estiver lá e cole este arquivo inteiro. Salve.
 * 3. Implantar > Nova implantação > tipo "App da Web".
 *    Executar como: Eu. Quem pode acessar: Qualquer pessoa. Clique em Implantar e autorize.
 * 4. Copie o endereço que termina em /exec e coloque em planilhaUrl, no js/config.js.
 *
 * A planilha continua privada: o endereço só aceita adicionar linhas, ninguém consegue ler os dados por ele.
 */

var ABA = 'Leads';
var FUSO = 'America/Belem';
var CABECALHO = [
  'Data e hora', 'Nome', 'WhatsApp', 'Abrir conversa', 'Interesse',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
  'Clique de anúncio', 'Página', 'Veio de'
];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');

    // Campo isca: robôs preenchem, pessoas não veem
    if (d.site) return resposta({ ok: true });

    var nome = texto(d.nome, 80);
    var whats = String(d.whatsapp || '').replace(/\D/g, '');
    if (nome.length < 2 || whats.length < 12 || whats.length > 13 || whats.indexOf('55') !== 0) {
      return resposta({ ok: false, erro: 'dados inválidos' });
    }

    aba().appendRow([
      Utilities.formatDate(new Date(), FUSO, 'dd/MM/yyyy HH:mm:ss'),
      nome,
      "'" + whats,
      'https://wa.me/' + whats,
      texto(d.interesse, 60),
      texto(d.utm_source, 100),
      texto(d.utm_medium, 100),
      texto(d.utm_campaign, 150),
      texto(d.utm_content, 150),
      texto(d.utm_term, 150),
      texto(d.clique, 10),
      texto(d.pagina, 300),
      texto(d.origem, 300)
    ]);
    return resposta({ ok: true });
  } catch (err) {
    console.error(err); // aparece em Execuções, no editor do Apps Script
    return resposta({ ok: false, erro: 'não foi possível gravar' });
  } finally {
    lock.releaseLock();
  }
}

// Abrir o endereço /exec no navegador mostra se está no ar
function doGet() {
  return resposta({ ok: true, status: 'no ar' });
}

function aba() {
  var planilha = SpreadsheetApp.getActiveSpreadsheet();
  // Usa a aba "Leads"; se ela não existir, usa a primeira aba da planilha
  var a = planilha.getSheetByName(ABA) || planilha.getSheets()[0];
  if (a.getLastRow() === 0) {
    a.appendRow(CABECALHO);
    a.setFrozenRows(1);
    a.getRange(1, 1, 1, CABECALHO.length).setFontWeight('bold');
  }
  return a;
}

// Corta o tamanho e impede que um texto vire fórmula na planilha
function texto(valor, max) {
  var s = String(valor == null ? '' : valor).replace(/\s+/g, ' ').trim().slice(0, max);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function resposta(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
