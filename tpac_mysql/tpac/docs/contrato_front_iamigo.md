# Contrato da API para o front-end — IAmigo

Endpoints usados pelo fluxo **Login → painel de tarefas**.

## Convenções gerais

| Item | Valor |
|---|---|
| URL base (desenvolvimento) | `http://127.0.0.1:8000` |
| Formato | JSON (`Content-Type: application/json`) |
| Sucesso | `{"dados": ...}` |
| Erro | `{"detail": "mensagem"}` |
| Autenticação | Header `Authorization: Bearer <access_token>` |
| Duração do token | 60 minutos (`expires_in`, em segundos) |
| Origens permitidas (CORS) | `http://127.0.0.1:5500`, `http://localhost:5500`, `http://127.0.0.1:5173`, `http://localhost:5173` |

**Regra para o front:** decidir a ação pelo **status HTTP** e usar `detail` apenas para mostrar a mensagem.

| Status | Significado | O que o front faz |
|---|---|---|
| `200` | Sucesso | Usa `dados` |
| `401` | Sem token, token inválido ou expirado | Limpa a sessão e volta ao login (**exceto** no próprio login: mostra o erro no formulário) |
| `403` | Autenticado, mas sem permissão | Mostra aviso de falta de permissão, **sem** encerrar a sessão |
| `404` | Recurso não encontrado | Mostra a mensagem |
| `422` | Dados inválidos | Mostra a mensagem junto ao formulário |
| `500` | Falha técnica no servidor | Mostra a mensagem genérica de `detail` |
| Sem resposta | API desligada ou erro de rede | Mostra "Não foi possível conectar ao servidor." |

---

## 1. Login

| Campo | Valor |
|---|---|
| **Nome** | Login |
| **Método** | `POST` |
| **Caminho** | `/auth/login` |
| **Precisa token?** | Não |
| **Quem pode usar?** | Qualquer pessoa (rota pública) |

**Body de entrada**

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `nome` | texto | Sim | Nome do perfil (identificador de login) |
| `senha` | texto | Sim | Senha do usuário |

```json
{ "nome": "Matheus", "senha": "matheus123" }
```

**Resposta de sucesso — `200`**

```json
{
  "dados": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "usuario": {
      "id": 6,
      "nome": "Matheus",
      "estilo_instrucao": "direto",
      "criado_em": "2026-09-22T21:50:02"
    }
  }
}
```

O front deve guardar:
- `dados.access_token` → usado no header `Authorization` das próximas requisições;
- `dados.usuario.id` → usado para montar a URL das tarefas;
- `dados.usuario.nome` → usado para a saudação.

A resposta **nunca** inclui senha nem hash de senha.

**Erros possíveis**

| Status | `detail` | Quando |
|---|---|---|
| `401` | `"Nome ou senha inválidos."` | Senha incorreta, nome inexistente ou usuário sem senha cadastrada |
| `422` | Lista de erros de validação | Falta `nome` ou `senha` no body (ver Pendências) |
| `500` | `"Não foi possível concluir a operação."` | Falha técnica no servidor |

```json
{ "detail": "Nome ou senha inválidos." }
```

---

## 2. Listar tarefas do usuário

| Campo | Valor |
|---|---|
| **Nome** | Listar tarefas do usuário |
| **Método** | `GET` |
| **Caminho** | `/usuarios/{usuario_id}/tarefas` |
| **Precisa token?** | Sim |
| **Quem pode usar?** | O próprio usuário (dono das tarefas) |

**Parâmetro de caminho**

| Campo | Tipo | Descrição |
|---|---|---|
| `usuario_id` | número | O `dados.usuario.id` recebido no login |

**Body de entrada:** nenhum.

**Header obrigatório**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Resposta de sucesso — `200`**

```json
{
  "dados": [
    {
      "id": 4,
      "usuario_id": 6,
      "tipo": "tarefas_diarias",
      "titulo": "Arrumar a Casa",
      "descricao": null,
      "prioridade": "media",
      "prazo": null,
      "concluida": false,
      "criado_em": "2026-09-24T19:11:17"
    }
  ]
}
```

| Campo | Valores possíveis |
|---|---|
| `tipo` | `tarefas_diarias`, `tarefas_educacionais` |
| `prioridade` | `baixa`, `media`, `alta` |
| `prazo` | Data `AAAA-MM-DD` ou `null` |
| `concluida` | `true` ou `false` |

Se o usuário não tiver tarefas, a resposta é `{"dados": []}`. Isso **não** é erro: o front mostra "Você ainda não tem tarefas."

**Erros possíveis**

| Status | `detail` | Quando |
|---|---|---|
| `401` | `"Token de acesso ausente."` | O header `Authorization` não foi enviado |
| `401` | `"Token inválido ou expirado."` | Token alterado, expirado ou de uma conta excluída |
| `403` | `"Você não tem permissão para esta ação."` | O `usuario_id` da URL não é o do token (outro usuário, inclusive admin, ou um `id` que não existe) |

```json
{ "detail": "Token inválido ou expirado." }
```

---

## Pendências conhecidas

| Pendência | Situação atual | Impacto no front | Ajuste previsto |
|---|---|---|---|
| Validação do FastAPI em formato de lista | Campos ausentes ou com tipo inválido retornam `{"detail": [ ... ]}`; as regras de negócio retornam `{"detail": "texto"}` | `login.js` verifica se `detail` é texto | Handler único em `api_app.py` para devolver sempre texto, atualizando `login.js` junto |
