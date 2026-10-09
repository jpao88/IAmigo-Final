const API_URL = "http://127.0.0.1:8000";

// Calculado a partir da localização deste arquivo, para funcionar também
// em páginas de subpastas (ex.: nova-tarefa/).
const PAGINA_LOGIN = new URL("index.html", document.currentScript.src).href;

function obterToken() {
  return sessionStorage.getItem("token");
}

function obterUsuario() {
  const texto = sessionStorage.getItem("usuario");
  return texto ? JSON.parse(texto) : null;
}

function limparSessao() {
  sessionStorage.removeItem("token");
  sessionStorage.removeItem("usuario");
}

function irParaLogin() {
  window.location.href = PAGINA_LOGIN;
}

async function requisicaoAutenticada(caminho, opcoes = {}) {
  const resposta = await fetch(`${API_URL}${caminho}`, {
    ...opcoes,
    headers: {
      ...(opcoes.headers || {}),
      Authorization: `Bearer ${obterToken()}`
    }
  });

  if (resposta.status === 401) {
    limparSessao();
    irParaLogin();
    return null;
  }

  return resposta;
}
