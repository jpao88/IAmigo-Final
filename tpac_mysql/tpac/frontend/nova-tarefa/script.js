const formulario = document.querySelector('#formulario');
const mensagem = document.querySelector('#mensagem');
const botao = formulario.querySelector('button[type="submit"]');
const titulo = document.querySelector('#titulo');
const tipo = document.querySelector('#tipo');

function mostrarMensagem(texto, classe) {
  mensagem.textContent = texto;
  mensagem.className = classe ? `mensagem ${classe}` : 'mensagem';
}

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();

  titulo.removeAttribute('aria-invalid');
  tipo.removeAttribute('aria-invalid');

  if (titulo.value.trim() === '') {
    mostrarMensagem('Não foi possível criar a tarefa. Preencha o título e o tipo.', 'erro');
    titulo.setAttribute('aria-invalid', 'true');
    titulo.focus();
    return;
  }

  if (tipo.value === '') {
    mostrarMensagem('Não foi possível criar a tarefa. Preencha o título e o tipo.', 'erro');
    tipo.setAttribute('aria-invalid', 'true');
    tipo.focus();
    return;
  }

  const usuario = obterUsuario();

  if (!obterToken() || !usuario) {
    mostrarMensagem('Faça login para criar tarefas.', 'erro');
    return;
  }

  const dados = {
    titulo: titulo.value.trim(),
    tipo: tipo.value
  };

  const textoOriginal = botao.textContent;
  botao.disabled = true;
  botao.textContent = 'Enviando...';
  mostrarMensagem('Aguarde.');

  try {
    const resposta = await requisicaoAutenticada(`/usuarios/${usuario.id}/tarefas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    if (!resposta) {
      return;
    }

    const resultado = await resposta.json().catch(() => ({}));

    if (!resposta.ok) {
      const texto = typeof resultado.detail === 'string'
        ? resultado.detail
        : 'Não foi possível criar a tarefa. Preencha o título e o tipo.';
      mostrarMensagem(texto, 'erro');
      return;
    }

    mostrarMensagem('Tarefa criada com sucesso.', 'sucesso');
    formulario.reset();
  } catch (erro) {
    console.error('Falha ao criar tarefa:', erro);
    mostrarMensagem('Não foi possível conectar à API.', 'erro');
  } finally {
    botao.disabled = false;
    botao.textContent = textoOriginal;
  }
});
