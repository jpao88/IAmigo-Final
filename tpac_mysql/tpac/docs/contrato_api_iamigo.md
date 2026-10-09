# Contrato da API — IAmigo (tpac_mysql/tpac)

## Convenciones generales

| Tema | Regla |
|---|---|
| URL base (desarrollo) | `http://127.0.0.1:8000` |
| Documentación interactiva | `http://127.0.0.1:8000/docs` (para rutas protegidas: hacer login y pegar el token en **Authorize**) |
| Formato | JSON (`Content-Type: application/json`) |
| Autenticación | JWT. `POST /auth/login` devuelve un `access_token`; las rutas protegidas lo reciben en el header `Authorization: Bearer <token>`. |
| Autorización | Según la matriz de `docs/aula09_autorizacao.md`. Cada ruta indica abajo quién puede usarla. |
| Éxito con contenido | `{"dados": ...}` |
| Éxito sin contenido | `204 No Content`, sin body |
| Error de negocio | `{"detail": "mensagem"}` (texto) |
| Error de validación de FastAPI | `422` con `{"detail": [ ... ]}` (lista). Ocurre si falta un campo obligatorio, un tipo es inválido (fecha mal formada), un valor no está entre los permitidos (`tipo`, `prioridade`, `estilo_instrucao`, `estado`) o un texto supera el tamaño máximo. |
| Fechas | Envío y respuesta en ISO: `prazo` como `AAAA-MM-DD`, `criado_em` como `AAAA-MM-DDTHH:MM:SS` |
| CORS | Orígenes permitidos por defecto: `http://localhost:5500`, `http://127.0.0.1:5500`, `http://localhost:5173`, `http://127.0.0.1:5173`. Configurable con `CORS_ORIGINS` en `.env`. |

### Códigos de estado usados

| Código | Significado en esta API |
|---|---|
| `200` | Operación correcta con datos |
| `201` | Recurso creado |
| `204` | Recurso eliminado |
| `401` | Sin token, token inválido o expirado, o nombre/contraseña incorrectos en el login |
| `403` | Token válido, pero el usuario no tiene permiso para esa ruta (por ejemplo, tareas de otra persona) |
| `404` | Usuario, tarea o paso inexistente, o un paso/tarea que no pertenece a la tarea/usuario de la URL |
| `422` | Regla de negocio incumplida o body inválido |
| `500` | Falla técnica (por ejemplo, base de datos caída). Respuesta: `{"detail": "Não foi possível concluir a operação."}`; el detalle queda en la terminal del servidor. |
| `503` | El servicio de IA (Gemini) no está disponible o no está configurado |

### Perfiles de permiso

| Perfil | Quién es |
|---|---|
| **Pública** | No necesita token |
| **Dono** | Usuario autenticado cuyo `id` es el `{usuario_id}` de la URL |
| **Admin** | Usuario con `papel = 'admin'` (solo se asigna por SQL) |

El admin gestiona **cuentas**, pero no accede a tareas, pasos ni IA de otros usuarios.

### Objetos

**Usuario**
```json
{ "id": 6, "nome": "Matheus", "estilo_instrucao": "direto", "criado_em": "2026-09-22T21:50:02" }
```
- `estilo_instrucao`: `"direto"` o `"detalhado"`
- `nome`: hasta 100 caracteres
- Nunca se devuelven `senha_hash` ni `papel`.

**Tarefa**
```json
{
  "id": 4, "usuario_id": 6, "tipo": "tarefas_diarias", "titulo": "Arrumar a Casa",
  "descricao": null, "prioridade": "media", "prazo": null, "concluida": false,
  "criado_em": "2026-09-24T19:11:17"
}
```
- `tipo`: `"tarefas_diarias"` o `"tarefas_educacionais"`
- `prioridade`: `"baixa"`, `"media"` o `"alta"`
- `titulo`: hasta 200 caracteres

**Passo**
```json
{ "id": 9, "tarefa_id": 4, "texto": "Coletar lixo e itens soltos", "concluido": false, "ordem": 1 }
```

---

## autenticacao

### POST /auth/login — Entrar
- **Permiso:** Pública
- **Body:**
```json
{ "nome": "Matheus", "senha": "minha_senha" }
```
- **Éxito:** `200`
```json
{
  "dados": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600,
    "usuario": { "id": 6, "nome": "Matheus", "estilo_instrucao": "direto", "criado_em": "..." }
  }
}
```
  `expires_in` está en segundos (configurable con `JWT_EXPIRA_MINUTOS`).
- **Errores:** `401` "Nome ou senha inválidos." (también para usuarios creados sin contraseña)

---

## usuarios
El front necesita registrar usuarios, ver y editar el propio perfil, y eliminar la cuenta. El listado completo es una función de administración.

### GET /usuarios — Listar usuários
- **Permiso:** Admin
- **Éxito:** `200` → `{"dados": [Usuario, ...]}`, ordenados por `nome`
- **Errores:** `401`, `403`
- **Evidencia:** auditado con spot-check en `/docs` y SELECT en MySQL; coincidencia total entre API y banco. Permisos cubiertos por `tests/test_api_permissoes.py`.

### GET /usuarios/{usuario_id} — Buscar um usuário específico
- **Permiso:** Dono o Admin
- **Éxito:** `200` → `{"dados": Usuario}`
- **Errores:** `401`, `403`, `404` "Usuário não encontrado." (solo el admin puede recibir `404`; un usuario común que pide otro `id` recibe `403`)
- **Evidencia:** ruta con `UsuarioService.buscar_usuario`. Probado con `id=1` (200) y `id=9999` (404), confirmado con SELECT.

### POST /usuarios — Criar usuário
- **Permiso:** Pública (registro abierto; el body no acepta `papel`)
- **Body:**
```json
{ "nome": "Ana", "estilo_instrucao": "direto", "senha": "minha_senha" }
```
  `estilo_instrucao` es opcional (por defecto `"direto"`). `senha` es opcional, pero **sin contraseña el usuario no puede hacer login** en la API.
- **Éxito:** `201` → `{"dados": Usuario}` (incluye el `id` creado)
- **Errores (`422`):**
  - "O nome não pode ficar vazio."
  - "O nome precisa ter pelo menos 3 caracteres."
  - "Já existe um perfil com esse nome."
  - "A senha precisa ter pelo menos 6 caracteres."
  - Lista de FastAPI si `estilo_instrucao` no es `"direto"`/`"detalhado"` o `nome` supera 100 caracteres
- **Evidencia:** auditado probando las validaciones en `/docs` y SELECT. Reglas cubiertas por `tests/test_usuario_service.py`.

### PUT /usuarios/{usuario_id} — Atualizar perfil
- **Permiso:** Dono o Admin
- **Body:** (ambos campos obligatorios)
```json
{ "nome": "Matheus Silva", "estilo_instrucao": "detalhado" }
```
- **Éxito:** `200` → `{"dados": Usuario}`
- **Errores:**
  - `401`, `403`
  - `404` "Usuário não encontrado."
  - `422` con las mismas reglas de `POST /usuarios`. Mantener el propio nombre está permitido; usar el nombre de **otro** usuario devuelve "Já existe um perfil com esse nome."
- **Nota:** el `nome` es el identificador de login; cambiarlo cambia con qué nombre se entra.
- **Evidencia:** probado con éxito (200), usuario inexistente (404) y nombre vacío (422), confirmado con SELECT. Regla del propio nombre cubierta por `tests/test_usuario_service.py`.

### DELETE /usuarios/{usuario_id} — Excluir usuário
- **Permiso:** Dono o Admin
- **Éxito:** `204`, sin body
- **Errores:** `401`, `403`, `404` "Usuário não encontrado."
- **⚠️ Importante:** por `ON DELETE CASCADE`, eliminar un usuario elimina también **todas sus tareas y pasos**. El front debería pedir confirmación antes de llamar a esta ruta.
- **Evidencia:** probado con un usuario con tareas y pasos (204); SELECT confirmó que no quedó ninguna tarea ni paso.

---

## tarefas
Es el recurso central del producto: el front necesita listar las tareas de un usuario, crearlas, editarlas, marcarlas como concluidas y eliminarlas.

**Permiso de todas las rutas de tarefas:** Dono. Sin token → `401`; otro usuario o admin → `403`.

### GET /usuarios/{usuario_id}/tarefas — Listar tarefas do usuário
- **Éxito:** `200` → `{"dados": [Tarefa, ...]}`, ordenadas por `id`. Lista vacía si el usuario no tiene tareas.
- **Errores:** `401`, `403`
- **Evidencia:** `TarefaController` → `TarefaService` → `TarefaRepository` (SQLAlchemy). Confirmado con SELECT.

### POST /usuarios/{usuario_id}/tarefas — Criar tarefa
- **Body:**
```json
{
  "tipo": "tarefas_diarias",
  "titulo": "Estudar SQL",
  "descricao": null,
  "prioridade": "media",
  "prazo": "2026-10-15"
}
```
  Obligatorios: `tipo`, `titulo`. Opcionales: `descricao` (null), `prioridade` (`"media"`), `prazo` (null, formato `AAAA-MM-DD`).
- **Éxito:** `201` → `{"dados": Tarefa}`
- **Errores:**
  - `401`, `403`
  - `422` "O título não pode ficar vazio."
  - `422` (lista de FastAPI) si `tipo` o `prioridade` no son valores permitidos, si `titulo` supera 200 caracteres o si `prazo` no tiene formato `AAAA-MM-DD`
- **Evidencia:** INSERT puntual vía SQLAlchemy. Probado con éxito (201) y título vacío (422), confirmado con SELECT.

### GET /usuarios/{usuario_id}/tarefas/{tarefa_id} — Buscar tarefa
- **Éxito:** `200` → `{"dados": Tarefa}`
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada." (también si la tarea es de otro usuario)

### PUT /usuarios/{usuario_id}/tarefas/{tarefa_id} — Atualizar tarefa
- **Body:** igual al de `POST /usuarios/{usuario_id}/tarefas`
- **Éxito:** `200` → `{"dados": Tarefa}`
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada.", `422` con las mismas reglas de creación

### PATCH /usuarios/{usuario_id}/tarefas/{tarefa_id} — Alternar status concluída
- **Body:** ninguno. Cada llamada invierte `concluida` (`false` → `true` → `false`).
- **Éxito:** `200` → `{"dados": Tarefa}`
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada."
- **Evidencia:** identifica la tarea por `id` de banco, no por índice de lista. Probado con éxito (200) y tarea inexistente (404), confirmado con SELECT.

### DELETE /usuarios/{usuario_id}/tarefas/{tarefa_id} — Excluir tarefa
- **Éxito:** `204`, sin body
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada."
- **Nota:** elimina también los pasos de la tarea (`ON DELETE CASCADE`).

---

## passos
El front necesita mostrar, generar con IA, marcar y eliminar los pasos de cada tarea, que es una funcionalidad central de accesibilidad del producto.

**Permiso de todas las rutas de passos:** Dono.

### GET /usuarios/{usuario_id}/tarefas/{tarefa_id}/passos — Listar passos de uma tarefa
- **Éxito:** `200` → `{"dados": [Passo, ...]}`, ordenados por `ordem`. Lista vacía si no hay pasos.
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada."
- **Evidencia:** modelo `Passo` y `PassoRepository`, orquestados por `TarefaService`. Confirmado con SELECT.

### POST /usuarios/{usuario_id}/tarefas/{tarefa_id}/passos/gerar — Gerar passos com IA
- **Body:** ninguno. Usa el `titulo` de la tarea.
- **Éxito:** `201` → `{"dados": [Passo, ...]}` (normalmente 3 o 4 pasos nuevos, guardados en el banco)
- **Errores:**
  - `401`, `403`, `404` "Tarefa não encontrada."
  - `503` "GEMINI_API_KEY não configurada. Configure sua chave de API." o "Não foi possível gerar os passos agora. Tente novamente."
- **Nota:** cada llamada **agrega** pasos nuevos a continuación de los existentes (su `ordem` sigue la numeración); no reemplaza los anteriores.
- **Evidencia:** usa `gerar_passos_tarefa()` de `core/ia_service.py`. Probado con IA disponible (201) y con falla de la IA (503), confirmado con SELECT.

### PATCH /usuarios/{usuario_id}/tarefas/{tarefa_id}/passos/{passo_id} — Alternar status concluído
- **Body:** ninguno. Cada llamada invierte `concluido`.
- **Éxito:** `200` → `{"dados": Passo}`
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada." o "Passo não encontrado." (también si el paso pertenece a otra tarea)
- **Evidencia:** identifica el paso por `id` de banco (`passo_id`), no por índice. Probado con éxito (200) y paso inexistente (404), confirmado con SELECT.

### DELETE /usuarios/{usuario_id}/tarefas/{tarefa_id}/passos/{passo_id} — Excluir passo
- **Éxito:** `204`, sin body
- **Errores:** `401`, `403`, `404` "Tarefa não encontrada." o "Passo não encontrado."
- **Nota:** los pasos restantes **no** se renumeran; puede quedar un hueco en `ordem` (por ejemplo 1, 2, 3 sin el 4). El front debe ordenar por `ordem`, no asumir números consecutivos.
- **Evidencia:** probado con éxito (204); SELECT confirmó que solo se eliminó el paso indicado.

---

## assistente_ia
El front necesita que el usuario pueda escribir un mensaje libre y recibir una respuesta o una tarea interpretada automáticamente, que es la propuesta de valor principal de IAmigo.

**Permiso de todas las rutas del asistente:** Dono (el admin tampoco puede usarlas en nombre de otro usuario).

### POST /usuarios/{usuario_id}/mensagens — Interpretar mensagem do usuário
- **Body:**
```json
{ "texto": "preciso estudar matemática amanhã" }
```
- **Éxito:** `200`
```json
{ "dados": { "intencao": "registrar_tarefa", "titulo": "Estudar matemática amanhã", "categoria": "tarefas_educacionais" } }
```
  Si no detecta una tarea: `{"dados": {"intencao": "pergunta", "titulo": null, "categoria": null}}`
- **Errores:** `401`, `403`
- **Nota:** solo clasifica el texto; **no guarda nada** en el banco. No usa Gemini.
- **Evidencia:** usa `interpretar_mensagem()` de `core/interpretador.py`. Probado con intención de tarea y con pregunta.

### POST /usuarios/{usuario_id}/perguntas — Responder pergunta geral
- **Body:**
```json
{ "texto": "o que é uma variável em programação?" }
```
- **Éxito:** `200` → `{"dados": ["línea 1", "línea 2", ...]}`. La respuesta se adapta al `estilo_instrucao` del usuario.
- **Errores:**
  - `401`, `403`
  - `503` "GEMINI_API_KEY não configurada. Configure sua chave de API." o "Não foi possível falar com a IA agora. Tente novamente."
- **Nota:** no guarda la pregunta ni la respuesta.
- **Evidencia:** usa `obter_resposta_ia()` de `core/ia_service.py`. Probado con preguntas reales (200).

### POST /usuarios/{usuario_id}/conversa — Cadastro de tarefa por conversa
- **Cómo funciona:** el servidor **no guarda** el estado de la conversación. El front debe reenviar en cada llamada el `estado` y la `tarefa` que recibió en la respuesta anterior (como `tarefa_parcial`).
- **Body:**
```json
{ "mensagem": "preciso lavar o carro", "estado": null, "tarefa_parcial": null }
```
- **Éxito:** `200`
```json
{
  "dados": {
    "respostas": ["📝 Entendi o que você precisa fazer!", "📌 Lavar o carro", "Qual é o prazo?", "..."],
    "estado": "esperando_prazo",
    "tarefa": { "titulo": "Lavar o carro", "categoria": "tarefas_diarias", "prazo": null, "prioridade": "media" }
  }
}
```
- **Flujo:**

| Paso | `estado` enviado | `mensagem` esperada | `estado` devuelto |
|---|---|---|---|
| 1 | `null` | Texto con una tarea ("preciso ...") | `esperando_prazo` |
| 2 | `esperando_prazo` | `DD/MM/AAAA` o `sem prazo` | `esperando_prioridade` |
| 3 | `esperando_prioridade` | `1`/`2`/`3` o `baixa`/`media`/`alta` | `esperando_mensagem` (tarea guardada) |

  - En cualquier paso, `cancelar` reinicia el flujo sin guardar.
  - Si el prazo o la prioridad son inválidos, responde `200` con un mensaje de ayuda y **mantiene el mismo estado**.
  - **⚠️ Cuando la respuesta trae `"estado": "esperando_mensagem"`, la siguiente llamada debe enviar `"estado": null`.** Enviar cualquier otro valor fuera de la tabla devuelve `422` (lista de FastAPI).
- **Errores:**
  - `401`, `403`
  - `422` "Não consegui identificar uma tarefa nessa mensagem." (paso 1 sin intención de tarea)
  - `422` si los datos de `tarefa_parcial` no forman una tarea válida al guardarla (por ejemplo, título vacío)
- **Evidencia:** `ConversaTarefa` recibe el estado del cliente y guarda la tarea final con `TarefaService.criar_tarefa()`. Probado con el flujo completo de 3 llamadas y con mensaje sin tarea, confirmado con SELECT.

---

## Limitaciones conocidas

1. **Eliminación en cascada.** `DELETE /usuarios/{id}` elimina todas las tareas y pasos del usuario, y `DELETE .../tarefas/{id}` elimina los pasos de la tarea.
2. **`ordem` de pasos no consecutivo** después de eliminar pasos.
3. **Registro abierto.** Cualquiera puede crear una cuenta con `POST /usuarios`.
4. **Mensajes de validación de FastAPI en inglés.** Los errores de formato (`422` con lista) vienen del framework; los de reglas de negocio (`422` con texto) vienen en portugués.
