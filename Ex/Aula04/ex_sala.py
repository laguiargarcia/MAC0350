from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from typing import Optional

app = FastAPI()

users = []

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/htmx-ext-json-enc@2.0.1/json-enc.js"></script>
    <title>Requests</title>
    <style>
        body {
            display: flex;
            gap: 2.5vw;
            justify-content: center;
            min-height: 90vh;
            background-color: #292827;
            color: #e0e0e0;
        }

        .secao-interacao, .secao-respostas {
            border: 2px solid #ff690a;
            border-radius: 15px;
            padding: 20px;
            width: 50%;
            height: auto;
        }

        .secao-interacao, form {
            display: flex;
            flex-direction: column;
        }

        @media(orientation: portrait) {
            body {
                flex-direction: column;
                gap: 2.5vh;
                min-height: auto;
            }

            .secao-interacao, .secao-respostas {
                min-height: 30vh;
                width: auto;
            }
        }

        #json-insert {
            color: #aa690a;
            font-size: xx-large;
        }

        label {
            margin-top: 15px;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 0.9rem;
            color: #ff690a;
        }

        input[type="text"], 
        input[type="number"] {
            background-color: #1e1e1e;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 12px 15px;
            color: #e0e0e0;
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }

        input[type="text"]:hover, 
        input[type="number"]:hover {
            border-color: #666;
        }

        input[type="text"]:focus, 
        input[type="number"]:focus {
            border-color: #ff690a;
            box-shadow: 0 0 8px rgba(255, 105, 10, 0.3);
            background-color: #252525;
        }

        input[type="submit"], button {
            margin-top: 20px;
            padding: 12px;
            border-radius: 8px;
            border: none;
            background-color: #ff690a;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.1s, background-color 0.2s;
        }

        input[type="submit"]:hover, button:hover {
            background-color: #e55a00;
        }

        input[type="submit"]:active, button:active {
            transform: scale(0.98);
        }

        hr {
            border: 0;
            border-top: 1px solid #444;
            margin: 25px 0;
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="secao-interacao">
        <h1>Requests</h1>
        <form hx-post="/users"
            hx-trigger="submit"
            hx-target="#json-insert"
            hx-swap="innerHTML"
            hx-ext="json-enc">  
            <label for="nome">Nome do usuário</label>
            <input type="text" name="nome">
            <label for="idade">Idade do usuário</label>
            <input type="number" name="idade">
            <input type="submit">
        </form>
        <hr>
        <input type="number"
            hx-get="/users"
            hx-trigger="input changed"
            hx-vals="js:{index: event.target.value}"
            hx-target="#json-insert"
            hx-swap="innerHTML"
            placeholder="Índice do usuário">
        <hr>
        <button hx-get="/users"
                hx-target="#json-insert"
                hx-swap="innerHTML">
            Obter todos os usuários
        </button>
        <hr>
        <button hx-delete="/users"
                hx-target="#json-insert"
                hx-swap="innerHTML">
            Apagar todos os usuários
        </button>
    </div>

    <div class="secao-respostas">
        <h1>Respostas</h1>
        <div id="json-insert"></div>
    </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def get_page():
    return HTML


class UserBody:
    def __init__(self, nome: str, idade: int):
        self.nome = nome
        self.idade = idade


from pydantic import BaseModel

class UserModel(BaseModel):
    nome: str
    idade: int


@app.post("/users")
def create_user(user: UserModel):
    users.append({"nome": user.nome, "idade": user.idade})
    return {"mensagem": "Usuário adicionado com sucesso", "usuario": user}


@app.get("/users")
def get_users(index: Optional[int] = Query(default=None)):
    if index is None:
        return users
    if index < 0 or index >= len(users):
        return {"erro": f"Índice {index} fora do intervalo. Total de usuários: {len(users)}"}
    return users[index]


@app.delete("/users")
def delete_users():
    users.clear()
    return {"mensagem": "Lista de usuários apagada com sucesso"}