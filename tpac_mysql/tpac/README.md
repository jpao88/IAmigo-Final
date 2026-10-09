# Sistema TPAC com MySQL

Este projeto foi ajustado para usar banco de dados MySQL no lugar do arquivo JSON.

## 1. Criar o banco no MySQL Workbench

1. Abra o MySQL Workbench.
2. Conecte no seu servidor local.
3. Abra o arquivo `database.sql`.
4. Execute o script completo clicando no raio.
5. Confirme se apareceu o banco `tea_db`.

## 2. Instalar as dependências do Python

No terminal, dentro da pasta do projeto, execute:

```bash
pip install -r requirements.txt
```

## 3. Configurar a conexão

Abra o arquivo `.env` e ajuste:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_do_mysql
DB_NAME=tea_db

# Login da API: use um texto longo e aleatório (32+ caracteres)
JWT_SECRET=troque_por_um_segredo_longo
JWT_EXPIRA_MINUTOS=60

# IA (opcional: sem ela, as funções de IA avisam que não está configurada)
GEMINI_API_KEY=sua_chave_do_gemini

# Opcional: origens do front liberadas no CORS, separadas por vírgula
# CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Todas essas variáveis são lidas em um único lugar: `config/settings.py`.

## 4. Executar o sistema

No terminal, dentro da pasta do projeto, execute:

```bash
python main.py
```

## 5. Aula web e testes da API

- Aula web (frontend): https://frontend-aula-1409.vercel.app/?k=pjp-fq2mrAE
- Os testes da API são feitos no Swagger: http://127.0.0.1:8000/docs

Para abrir o Swagger, inicie a API antes, dentro da pasta do projeto:

```bash
uvicorn api_app:app --reload
```

## Arquivos principais

- `database.sql`: cria o banco, tabelas e dados de exemplo.
- `.env`: guarda as configurações (lidas por `config/settings.py`).
- `main.py`: inicia o sistema no console (`ui/menus.py`).
- `api_app.py`: inicia a API (FastAPI).

O console e a API usam as mesmas camadas para acessar o banco:
`services/` (regras de negócio) → `repositories/` (consultas) → `models/` (tabelas).
