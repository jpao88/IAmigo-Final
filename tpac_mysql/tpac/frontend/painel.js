const saudacao = document.getElementById("saudacao");
const mensagem = document.getElementById("mensagem");
const lista = document.getElementById("lista-tarefas");
const botaoSair = document.getElementById("botao-sair");

const usuario = obterUsuario();

if (!obterToken() || !usuario) {
  irParaLogin();
} else {
  saudacao.textContent = `Olá, ${usuario.nome}`;
  carregarTarefas();
}

async function carregarTarefas() {
  mensagem.textContent = "Carregando tarefas...";
  mensagem.className = "mensagem";

  try {
    const resposta = await requisicaoAutenticada(`/usuarios/${usuario.id}/tarefas`);

    if (!resposta) {
      return;
    }

    const corpo = await resposta.json();

    if (resposta.status === 403) {
      mostrarErro("Você não tem permissão para ver estas tarefas.");
      return;
    }

    if (!resposta.ok) {
      const texto = typeof corpo.detail === "string"
        ? corpo.detail
        : "Dados inválidos na requisição.";
      mostrarErro(texto);
      return;
    }

    mostrarTarefas(corpo.dados);
  } catch (erro) {
    console.error("Falha ao carregar tarefas:", erro);
    mostrarErro("Não foi possível conectar ao servidor. A API está rodando?");
  }
}

function mostrarTarefas(tarefas) {
  lista.innerHTML = "";

  if (tarefas.length === 0) {
    mensagem.textContent = "Você ainda não tem tarefas.";
    return;
  }

  mensagem.textContent = "";

  for (const tarefa of tarefas) {
    const item = document.createElement("li");
    const status = tarefa.concluida ? "✅ Concluída" : "⏳ Pendente";
    const prazo = tarefa.prazo
      ? tarefa.prazo.split("-").reverse().join("/")
      : "sem prazo";

    item.textContent = `${tarefa.titulo} · prioridade ${tarefa.prioridade} · ${prazo} · ${status}`;
    lista.appendChild(item);
  }
}

function mostrarErro(texto) {
  mensagem.textContent = texto;
  mensagem.className = "mensagem erro";
}

botaoSair.addEventListener("click", () => {
  limparSessao();
  irParaLogin();
});