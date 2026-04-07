# Game Ranker

Um web app simples para **registrar, avaliar e organizar jogos**.  
O usuário pode adicionar jogos com **gêneros, nota e comentário**, além de **buscar e ordenar os jogos cadastrados**.  
Os **gêneros são armazenados como um modelo próprio no banco de dados**, permitindo **criar, renomear e remover gêneros** de forma independente, com suporte a **hierarquia de gêneros** em profundidade arbitrária.

---

## Funcionalidades

### Jogos

- Adicionar novos jogos
- Atualizar informações de um jogo
- Remover jogos
- Associar cada jogo a **múltiplos gêneros**
- Dar uma **nota** de 0 a 10 para o jogo
- Adicionar um **comentário**
- **Buscar jogos** pelo nome
- **Ordenar jogos** por nota, gênero ou nome

### Gêneros

- Criar novos gêneros
- Renomear gêneros existentes
- Remover gêneros
- **Aninhar gêneros** em hierarquias de profundidade arbitrária (ex: `Ação > RPG > Action RPG`)
- Validação de ciclos ao definir gênero pai
- Validação de conflito ancestral ao associar gêneros a um jogo (impede selecionar um gênero e um de seus ancestrais simultaneamente)

---

## Demonstração

Exemplo de registro de jogo:

| Campo      | Exemplo                          |
|------------|----------------------------------|
| Nome       | Hollow Knight                    |
| Gêneros    | Metroidvania, Indie              |
| Nota       | 9.5                              |
| Comentário | Combate e exploração excelentes  |

Exemplo de hierarquia de gêneros:

```
Ação
└─ RPG
    └─ Action RPG
Plataforma
└─ Metroidvania
```

---

## Estrutura do Projeto

```
game-ranker/
│
├── frontend/
│   ├── index.html     # Página principal — lista e cadastro de jogos
│   ├── genres.html    # Página de gerenciamento de gêneros
│   ├── styles.css
│   └── script.js
│
├── backend/
│   └── main.py        # API FastAPI + modelos SQLAlchemy + renderização HTMX
│
└── README.md
```

---

## Tecnologias Utilizadas

**Frontend**
- HTML / CSS / JavaScript
- [HTMX](https://htmx.org/) — interatividade sem framework JS

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/) (ORM)
- SQLite

---

## Modelo de Dados

### Genre

| Campo      | Tipo    | Descrição                                 |
|------------|---------|-------------------------------------------|
| id         | integer | Chave primária                            |
| name       | string  | Nome único do gênero                      |
| parent_id  | integer | FK para `genres.id` (nullable) — hierarquia |

### Game

| Campo   | Tipo    | Descrição      |
|---------|---------|----------------|
| id      | integer | Chave primária |
| name    | string  | Nome do jogo   |
| rating  | float   | Nota (0–10)    |
| comment | string  | Comentário     |

### game_genres (tabela de associação)

| Campo    | Tipo    | Descrição         |
|----------|---------|-------------------|
| game_id  | integer | FK → `games.id`   |
| genre_id | integer | FK → `genres.id`  |

### Relações

- Um **gênero** pode ter um **gênero pai** (auto-referência, hierarquia em árvore)
- Um **jogo** pode ter **vários gêneros** e um **gênero** pode estar em vários jogos

Relação Game ↔ Genre: **Many-to-Many** (via `game_genres`)  
Relação Genre ↔ Genre: **One-to-Many** auto-referenciada (hierarquia)

## Processo de Desenvolvimento

O desenvolvimento contou com o auxílio de **ferramentas de IA** (Claude) em algumas etapas:

- Geração e refinamento de partes do **frontend** (HTML/CSS)
- Suporte ao **debugging** de comportamentos inesperados no backend e nas integrações HTMX
- Revisão pontual de lógica em trechos específicos do código