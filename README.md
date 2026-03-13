# Game Ranker

Um web app simples para **registrar, avaliar e organizar jogos**.  
O usuário pode adicionar jogos com **gênero, nota e comentário**, além de **buscar e ordenar os jogos cadastrados**.

## Funcionalidades

-  Adicionar novos jogos
-  Associar cada jogo a um **gênero**
-  Dar uma **nota** para o jogo
-  Adicionar um **comentário**
-  **Buscar jogos** pelo nome
-  **Ordenar jogos**
  - por **nota**
  - por **gênero**
-  Interface **responsiva** para desktop e mobile

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
| genre | string |
| rating | float |
| comment | string |

---

## Exemplos de Uso

### Adicionar jogo

POST /games

{
  "name": "Celeste",
  "genre": "Platformer",
  "rating": 9.5,
  "comment": "Gameplay muito preciso"
}

### Buscar jogo

GET /games/search?name=celeste

### Ordenar jogos

Por nota:

GET /games?sort=rating

Por gênero:

GET /games?sort=genre

---

## Possíveis melhorias

- Sistema de usuários
- Upload de capa do jogo
- Filtros avançados
- API pública
- Ranking global

---

## Autor

Lucas Aguiar Garcia

Estudante de Ciência da Computação — USP