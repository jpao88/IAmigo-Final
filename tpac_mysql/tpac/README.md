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
```

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
- `.env`: guarda as configurações de conexão.
- `data/data_manager.py`: faz a conexão entre Python e MySQL.
- `main.py`: inicia o sistema.
