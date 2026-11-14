// Menu do celular: abre e fecha a lista de seções.
(function () {
  var botao = document.querySelector('.nav__botao');
  var lista = document.getElementById('nav-lista');
  if (!botao || !lista) return;

  function fechar() {
    botao.setAttribute('aria-expanded', 'false');
    botao.textContent = 'Menu';
  }

  botao.addEventListener('click', function () {
    var aberto = botao.getAttribute('aria-expanded') === 'true';
    botao.setAttribute('aria-expanded', String(!aberto));
    botao.textContent = aberto ? 'Menu' : 'Fechar';
  });

  lista.addEventListener('click', function (evento) {
    if (evento.target.closest('a')) fechar();
  });

  document.addEventListener('keydown', function (evento) {
    if (evento.key === 'Escape' && botao.getAttribute('aria-expanded') === 'true') {
      fechar();
      botao.focus();
    }
  });
})();
