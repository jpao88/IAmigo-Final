# Aula 09 — Autorização no IAmigo

## 1. Perfis

| Papel | Quem é | Como é atribuído |
|---|---|---|
| `usuario` | Qualquer pessoa que usa o IAmigo | Automático: valor padrão da coluna `papel` |
| `admin` | Quem mantém o sistema e gerencia contas | Somente por SQL (`UPDATE usuarios SET papel = 'admin' ...`). Nenhuma rota da API permite alterar o papel. |

**Decisões tomadas:**
- O `admin` gerencia **contas** (listar, ver, editar e excluir usuários), mas **não** acessa tarefas, passos nem IA de outros usuários, para proteger dados pessoais.
- O cadastro (`POST /usuarios`) continua **público** por enquanto.
- Não existe um terceiro papel: nenhum caso de uso do sistema o justifica.

**Legenda da matriz:**
- **Anônimo:** sem token.
- **Dono:** usuário autenticado cujo `id` é igual ao `{usuario_id}` da URL.
- **Outro:** usuário autenticado com papel `usuario` que não é o dono.
- **Admin:** usuário autenticado com papel `admin`.
- **Hoje:** ✅ implementado e testado · 🟠 parcial · ❌ ainda pública.

## 2. Matriz de permissões (perfis × ações)

### Autenticação e sistema

| Rota / ação | Permitido | Negado | Motivo | Status negado | Hoje |
|---|---|---|---|---|---|
| `POST /auth/login` | Pública | — | Sem login não há como obter token. | — | ✅ |
| `GET /` | Pública | — | Só confirma que a API está no ar; não expõe dados. | — | ✅ |
| `/docs`, `/openapi.json` | Pública em desenvolvimento | Decidir ao publicar | Mostra o mapa completo da API. | — | ✅ |

### Usuários

| Rota / ação | Permitido | Negado | Motivo | Status negado | Hoje |
|---|---|---|---|---|---|
| `POST /usuarios` | Pública | — | Cadastro aberto. O body não aceita `papel`, então ninguém se cadastra como admin. | — | ✅ |
| `GET /usuarios` | Admin | Anônimo, Outro, Dono | Expõe os nomes de todas as contas e facilita adivinhar logins. | 401 / 403 | ✅ |
| `GET /usuarios/{id}` | Dono, Admin | Anônimo, Outro | Perfil pessoal. | 401 / 403 | ✅ |
| `PUT /usuarios/{id}` | Dono, Admin | Anônimo, Outro | O `nome` é o identificador de login. | 401 / 403 | ✅ |
| `DELETE /usuarios/{id}` | Dono, Admin | Anônimo, Outro | Ação irreversível, com exclusão em cascata de tarefas e passos. | 401 / 403 | ✅ |

### Assistente IA

| Rota / ação | Permitido | Negado | Motivo | Status negado | Hoje |
|---|---|---|---|---|---|
| `POST /usuarios/{id}/mensagens` | Dono | Anônimo, Outro, Admin | Age em nome do usuário. | 401 / 403 | ✅ |
| `POST /usuarios/{id}/perguntas` | Dono | Anônimo, Outro, Admin | Consome a cota do Gemini e usa o estilo do usuário. | 401 / 403 | ✅ |
| `POST /usuarios/{id}/conversa` | Dono | Anônimo, Outro, Admin | Ao final, cria uma tarefa na conta do usuário. | 401 / 403 | ✅ |

### Tarefas

| Rota / ação | Permitido | Negado | Motivo | Status negado | Hoje |
|---|---|---|---|---|---|
| `GET /usuarios/{id}/tarefas` | Dono | Anônimo, Outro, Admin | Tarefas são pessoais. | 401 / 403 | ✅ |
| `POST /usuarios/{id}/tarefas` | Dono | Anônimo, Outro, Admin | Ninguém cria tarefas na conta de outra pessoa. | 401 / 403 | ✅ |
| `GET /usuarios/{id}/tarefas/{tarefa_id}` | Dono | Anônimo, Outro, Admin | Tarefa pessoal. | 401 / 403 | ✅ |
| `PUT /usuarios/{id}/tarefas/{tarefa_id}` | Dono | Anônimo, Outro, Admin | Altera dados pessoais. | 401 / 403 | ✅ |
| `PATCH /usuarios/{id}/tarefas/{tarefa_id}` | Dono | Anônimo, Outro, Admin | Marcar progresso é ação da própria pessoa. | 401 / 403 | ✅ |
| `DELETE /usuarios/{id}/tarefas/{tarefa_id}` | Dono | Anônimo, Outro, Admin | Irreversível; exclui também os passos. | 401 / 403 | ✅ |

### Passos

| Rota / ação | Permitido | Negado | Motivo | Status negado | Hoje |
|---|---|---|---|---|---|
| `GET .../tarefas/{tarefa_id}/passos` | Dono | Anônimo, Outro, Admin | Parte de uma tarefa pessoal. | 401 / 403 | ✅ |
| `POST .../passos/gerar` | Dono | Anônimo, Outro, Admin | Consome a cota do Gemini. | 401 / 403 | ✅ |
| `PATCH .../passos/{passo_id}` | Dono | Anônimo, Outro, Admin | Marcar progresso é ação da própria pessoa. | 401 / 403 | ✅ |
| `DELETE .../passos/{passo_id}` | Dono | Anônimo, Outro, Admin | Irreversível. | 401 / 403 | ✅ |

## 3. Regras transversais

- **Ordem das verificações:** token → usuário identificado → papel/propriedade → ação. Se a permissão falha, a ação nunca é executada.
- **401** = "não sei quem você é" (sem token, token inválido, expirado ou de conta excluída). O front pode redirecionar para o login, exceto na própria rota de login.
- **403** = "sei quem você é, mas esta ação não é permitida". O front informa a falta de permissão sem encerrar a sessão.
- **403 antes de 404 para quem não é admin:** um usuário comum que pede o `id` de outra conta recebe 403 mesmo que esse `id` não exista, para não revelar quais contas existem. Só o admin vê o 404.
- **O papel é lido do banco a cada requisição**, não do token: uma mudança de papel vale na requisição seguinte.
- **Esconder botões no front não é autorização:** a API nega a requisição mesmo quando chamada diretamente (`/docs`, PowerShell, Postman).
- **O console (`python main.py`) usa os services diretamente, sem passar pela API,** e não aplica autenticação; é uma ferramenta local de desenvolvimento, como o Workbench.

## 4. Arquitetura: arquivos alterados

| Arquivo | Alteração |
|---|---|
| Banco (`tea_db`) | `ALTER TABLE usuarios ADD COLUMN papel ENUM('usuario', 'admin') NOT NULL DEFAULT 'usuario'` |
| `database.sql` | Mesma coluna, documentada |
| `models/usuario.py` | Campo `papel` (`Enum`, com `default` e `server_default` = `usuario`) |
| `api/dependencias.py` | Nova dependência `exigir_dono_ou_admin` (autorização), que reutiliza `obter_usuario_autenticado` (autenticação) |
| `api/rotas_usuarios.py` | `Depends(exigir_dono_ou_admin)` em `DELETE` e `PUT /usuarios/{usuario_id}` |
| `api/dependencias.py` (depois) | Novas dependências `exigir_dono` (tarefas, passos e IA) e `exigir_admin` (`GET /usuarios`) |
| `api/rotas_tarefas.py` (depois) | `Depends(exigir_dono)` no `APIRouter`: vale para todas as rotas de tarefas e passos |
| `api/rotas_usuarios.py` (depois) | `exigir_admin` em `GET /usuarios`, `exigir_dono_ou_admin` em `GET /usuarios/{id}`, `exigir_dono` nas rotas de IA |
| `tests/test_api_permissoes.py` | Testa esta matriz para os perfis Dono, Outro e Admin |

**Não foram alterados:** services, controllers e repositories. A autorização acontece antes da ação, sem mexer na regra de negócio. A verificação vive em um único lugar (`api/dependencias.py`), e cada rota só declara o que precisa.

### Fluxo

```
token válido          → obter_usuario_autenticado   → falha: 401
→ usuário identificado → busca o usuário no banco    → falha: 401
→ papel verificado     → exigir_dono_ou_admin        → falha: 403
→ ação executada       → controller → service → repository (200 / 204 / 404)
```

## 5. Contas de teste

| id | Conta | Papel | Uso |
|---|---|---|---|
| 6 | Matheus | usuario | Dono das tarefas 4 e 6 |
| 17 | Admin Teste | admin | Administrador |
| 19 | Login Teste | usuario | "Outro" usuário, para testar o 403 |

## 6. Pendências

- Decidir se `/docs` fica visível ao publicar a API.
