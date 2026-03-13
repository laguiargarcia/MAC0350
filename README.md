# Game Ranker

Um web app simples para **registrar, avaliar e organizar jogos**.  
O usuário pode adicionar jogos com **gênero, nota e comentário**, além de **buscar e ordenar os jogos cadastrados**.

Os **gêneros são armazenados como um modelo próprio no banco de dados**, permitindo **criar, renomear e remover gêneros** de forma independente.

---

## Funcionalidades

### Jogos

- Adicionar novos jogos
- Atualizar informações de um jogo
- Remover jogos
- Associar cada jogo a um **gênero**
- Dar uma **nota** para o jogo
- Adicionar um **comentário**
- **Buscar jogos** pelo nome
- **Ordenar jogos**
  - por **nota**
  - por **gênero**

### Gêneros

- Criar novos gêneros
- Renomear gêneros existentes
- Remover gêneros

### Interface

- Interface **responsiva** para desktop e mobile

---

## Demonstração

Exemplo de registro de jogo:

| Campo | Exemplo |
|---|---|
| Nome | Hollow Knight |
| Gênero | Metroidvania |
| Nota | 9 |
| Comentário | Combate e exploração excelentes |

---

## Estrutura do Projeto


```
game-ranker/
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── backend/
│   └── main.py
│
├── models/
│   └── game.py
│
└── README.md
```
---

## Tecnologias Utilizadas

Frontend

- HTML
- CSS
- JavaScript

Backend

- FastAPI

Banco de dados

- SQL (ex: SQLite ou PostgreSQL)

---

## Como executar o projeto

### Clonar o repositório

git clone https://github.com/seu-usuario/game-ranker.git
cd game-ranker

### Criar ambiente virtual

python -m venv venv
source venv/bin/activate

Windows:

venv\Scripts\activate

### Instalar dependências

pip install fastapi uvicorn

### Executar o servidor

uvicorn main:app --reload

O backend estará disponível em:

http://localhost:8000

---

## Modelo de Dados

### Game

| Campo | Tipo |
|---|---|
| id | integer |
| name | string |
| rating | float |
| comment | string |
| genre_id | integer |

### Genre

| Campo | Tipo |
|---|---|
| id | integer |
| name | string |

### Relação

- Um **gênero pode ter vários jogos**  
- Cada **jogo pertence a um único gênero**

Relação: **One-to-Many (Genre → Game)**

## Autor

Lucas Aguiar Garcia

Estudante de Ciência da Computação — USP