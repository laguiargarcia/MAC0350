from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine, select

DATABASE_URL = "sqlite:///./game_ranker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

API = "http://localhost:8000"

class GameGenreLink(SQLModel, table=True):
    game_id:  Optional[int] = Field(default=None, foreign_key="game.id",  primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)

class Genre(SQLModel, table=True):
    id:        Optional[int] = Field(default=None, primary_key=True)
    name:      str           = Field(unique=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="genre.id")

    parent:   Optional["Genre"]  = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"foreign_keys": "[Genre.parent_id]",
                                "remote_side": "[Genre.id]"},
    )
    children: List["Genre"]      = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Genre.parent_id]"},
    )
    games:    List["Game"]       = Relationship(back_populates="genres", link_model=GameGenreLink)


class Game(SQLModel, table=True):
    id:      Optional[int] = Field(default=None, primary_key=True)
    name:    str
    rating:  float
    comment: str           = Field(default="")

    genres: List[Genre] = Relationship(back_populates="games", link_model=GameGenreLink)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Game Ranker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_ancestors(genre: Genre) -> list:
    ancestors = []
    current = genre.parent
    while current is not None:
        ancestors.insert(0, current)
        current = current.parent
    return ancestors


def genre_full_path(genre: Genre) -> str:
    parts = [a.name for a in get_ancestors(genre)] + [genre.name]
    return " > ".join(parts)


def get_all_ancestor_ids(genre: Genre) -> set:
    ids = set()
    current = genre.parent
    while current is not None:
        ids.add(current.id)
        current = current.parent
    return ids


def get_all_descendant_ids(genre: Genre) -> set:
    ids = set()
    stack = list(genre.children)
    while stack:
        child = stack.pop()
        ids.add(child.id)
        stack.extend(child.children)
    return ids


def validate_no_ancestor_conflict(genres: list) -> Optional[str]:
    selected_ids = {g.id for g in genres}
    for genre in genres:
        conflict_ids = get_all_ancestor_ids(genre) & selected_ids
        if conflict_ids:
            conflict_names = [g.name for g in genres if g.id in conflict_ids]
            return (
                f'"{genre.name}" já está contido em '
                f'"{", ".join(conflict_names)}". '
                f'Selecione apenas um dos dois.'
            )
    return None

def build_genre_options(genres: list, selected_ids: Optional[set] = None,
                        exclude_ids: Optional[set] = None) -> str:
    if selected_ids is None:
        selected_ids = set()
    if exclude_ids is None:
        exclude_ids = set()

    roots   = [g for g in genres if g.parent_id is None]
    options = ""

    def walk(genre: Genre, depth: int):
        nonlocal options
        if genre.id in exclude_ids:
            return
        indent   = "\u00a0\u00a0\u00a0\u00a0" * depth
        prefix   = "└─ " if depth > 0 else ""
        selected = "selected" if genre.id in selected_ids else ""
        options += f'<option value="{genre.id}" {selected}>{indent}{prefix}{genre.name}</option>'
        for child in genre.children:
            walk(child, depth + 1)

    for root in roots:
        walk(root, 0)

    return options


def render_genre_row(genre: Genre) -> str:
    full_path   = genre_full_path(genre)
    depth       = len(get_ancestors(genre))
    indent_html = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
    arrow       = "└─ " if depth > 0 else ""
    return f"""
    <tr id="genre-{genre.id}">
      <td>{indent_html}{arrow}{genre.name}
        <small style="color:var(--muted); font-size:11px; margin-left:6px">{full_path if depth > 0 else ""}</small>
      </td>
      <td>
        <button hx-get="{API}/genres/{genre.id}/edit-form"
                hx-target="#genre-{genre.id}" hx-swap="outerHTML">Editar</button>
        <button hx-delete="{API}/genres/{genre.id}"
                hx-target="#genre-{genre.id}" hx-swap="outerHTML"
                hx-confirm="Remover gênero '{genre.name}'?">Remover</button>
      </td>
    </tr>
    """


def render_genre_edit_form(genre: Genre, session: Session) -> str:
    all_genres   = session.exec(select(Genre)).all()
    exclude      = get_all_descendant_ids(genre)
    exclude.add(genre.id)
    selected_ids = {genre.parent_id} if genre.parent_id else set()
    options  = '<option value="">— sem pai —</option>'
    options += build_genre_options(all_genres, selected_ids=selected_ids, exclude_ids=exclude)
    return f"""
    <tr id="genre-{genre.id}">
      <td><input id="genre-name-{genre.id}" name="name" value="{genre.name}" /></td>
      <td>
        <select id="genre-parent-{genre.id}" name="parent_id">{options}</select>
      </td>
      <td>
        <button hx-put="{API}/genres/{genre.id}"
                hx-include="#genre-name-{genre.id},#genre-parent-{genre.id}"
                hx-target="#genres-tbody" hx-swap="innerHTML">Salvar</button>
        <button hx-get="{API}/genres/{genre.id}/row"
                hx-target="#genre-{genre.id}" hx-swap="outerHTML">Cancelar</button>
      </td>
    </tr>
    """


def _genre_badge(genre: Genre) -> str:
    return f'<span class="genre-badge">{genre_full_path(genre)}</span>'


def render_game_row(game: Game) -> str:
    if game.genres:
        genre_label = " ".join(_genre_badge(g) for g in sorted(game.genres, key=lambda g: g.name))
    else:
        genre_label = '<span class="no-genre">—</span>'
    return f"""
    <tr id="game-{game.id}">
      <td>{game.name}</td>
      <td class="genre-cell">{genre_label}</td>
      <td title="{game.rating}"> {game.rating}</td>
      <td>{game.comment or "—"}</td>
      <td>
        <button hx-get="{API}/games/{game.id}/edit-form"
                hx-target="#game-{game.id}" hx-swap="outerHTML">Editar</button>
        <button hx-delete="{API}/games/{game.id}"
                hx-target="#game-{game.id}" hx-swap="outerHTML"
                hx-confirm="Remover '{game.name}'?">Remover</button>
      </td>
    </tr>
    """


def render_game_edit_form(game: Game, session: Session) -> str:
    genres       = session.exec(select(Genre)).all()
    selected_ids = {g.id for g in game.genres}
    options      = build_genre_options(genres, selected_ids=selected_ids)
    return f"""
    <tr id="game-{game.id}">
      <td><input id="game-name-{game.id}"    name="name"    value="{game.name}" /></td>
      <td>
        <select id="game-genre-{game.id}" name="genre_ids" multiple size="4" style="min-width:160px">
          {options}
        </select>
        <div style="font-size:10px;color:var(--muted);margin-top:3px">Ctrl/⌘ para múltiplos</div>
      </td>
      <td><input id="game-rating-{game.id}"  name="rating"  type="number" min="0" max="10" step="0.1" value="{game.rating}" style="width:60px"/></td>
      <td><input id="game-comment-{game.id}" name="comment" value="{game.comment or ''}" /></td>
      <td>
        <button hx-put="{API}/games/{game.id}"
                hx-include="#game-name-{game.id},#game-genre-{game.id},#game-rating-{game.id},#game-comment-{game.id}"
                hx-target="#game-{game.id}" hx-swap="outerHTML">Salvar</button>
        <button hx-get="{API}/games/{game.id}/row"
                hx-target="#game-{game.id}" hx-swap="outerHTML">Cancelar</button>
      </td>
    </tr>
    """

@app.get("/genres/options", response_class=HTMLResponse)
def genre_options():
    with Session(engine) as session:
        genres  = session.exec(select(Genre)).all()
        options = build_genre_options(genres)
        return options


@app.get("/genres/ancestry")
def genre_ancestry():
    with Session(engine) as session:
        genres = session.exec(select(Genre)).all()
        return {g.id: list(get_all_ancestor_ids(g)) for g in genres}


@app.get("/genres", response_class=HTMLResponse)
def list_genres():
    with Session(engine) as session:
        all_genres   = session.exec(select(Genre)).all()
        roots        = [g for g in all_genres if g.parent_id is None]
        rows         = []
        rendered_ids = set()

        def walk(genre: Genre):
            rows.append(render_genre_row(genre))
            rendered_ids.add(genre.id)
            for child in genre.children:
                walk(child)

        for root in roots:
            walk(root)

        for g in all_genres:
            if g.id not in rendered_ids:
                rows.append(render_genre_row(g))

        return "".join(rows) if rows else '<tr><td colspan="2">Nenhum gênero cadastrado.</td></tr>'


@app.post("/genres", response_class=HTMLResponse)
async def create_genre(request: Request):
    form      = await request.form()
    name      = form.get("name", "").strip()
    parent_id = form.get("parent_id") or None

    if not name:
        raise HTTPException(status_code=400, detail="Nome não pode ser vazio")

    with Session(engine) as session:
        if session.exec(select(Genre).where(Genre.name == name)).first():
            raise HTTPException(status_code=400, detail="Gênero já existe")

        genre = Genre(name=name, parent_id=int(parent_id) if parent_id else None)
        session.add(genre)
        session.commit()

        all_genres   = session.exec(select(Genre)).all()
        roots        = [g for g in all_genres if g.parent_id is None]
        rows         = []
        rendered_ids = set()

        def walk(g: Genre):
            rows.append(render_genre_row(g))
            rendered_ids.add(g.id)
            for child in g.children:
                walk(child)

        for root in roots:
            walk(root)
        for g in all_genres:
            if g.id not in rendered_ids:
                rows.append(render_genre_row(g))

        return "".join(rows)


@app.get("/genres/{genre_id}/row", response_class=HTMLResponse)
def get_genre_row(genre_id: int):
    with Session(engine) as session:
        genre = session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Gênero não encontrado")
        return render_genre_row(genre)


@app.get("/genres/{genre_id}/edit-form", response_class=HTMLResponse)
def edit_genre_form(genre_id: int):
    with Session(engine) as session:
        genre = session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Gênero não encontrado")
        return render_genre_edit_form(genre, session)


@app.put("/genres/{genre_id}", response_class=HTMLResponse)
async def update_genre(genre_id: int, request: Request):
    form      = await request.form()
    name      = form.get("name", "").strip()
    parent_id = form.get("parent_id")

    with Session(engine) as session:
        genre = session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Gênero não encontrado")

        if parent_id:
            new_parent_id = int(parent_id)
            if new_parent_id == genre.id or new_parent_id in get_all_descendant_ids(genre):
                raise HTTPException(status_code=400, detail="Ciclo detectado")
            genre.parent_id = new_parent_id
        else:
            genre.parent_id = None

        if name:
            genre.name = name

        session.add(genre)
        session.commit()

        all_genres   = session.exec(select(Genre)).all()
        roots        = [g for g in all_genres if g.parent_id is None]
        rows         = []
        rendered_ids = set()

        def walk(g: Genre):
            rows.append(render_genre_row(g))
            rendered_ids.add(g.id)
            for child in g.children:
                walk(child)

        for root in roots:
            walk(root)
        for g in all_genres:
            if g.id not in rendered_ids:
                rows.append(render_genre_row(g))

        return "".join(rows)


@app.delete("/genres/{genre_id}", response_class=HTMLResponse)
def delete_genre(genre_id: int):
    with Session(engine) as session:
        genre = session.get(Genre, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Gênero não encontrado")
        session.delete(genre)
        session.commit()
        return ""
    
@app.get("/games", response_class=HTMLResponse)
def list_games(search: Optional[str] = None, order_by: Optional[str] = None):
    with Session(engine) as session:
        query = select(Game)

        if search:
            query = query.where(Game.name.ilike(f"%{search}%"))
        if order_by == "rating":
            query = query.order_by(Game.rating.desc())
        elif order_by == "name":
            query = query.order_by(Game.name)

        games = session.exec(query).all()

        if order_by == "genre":
            games = sorted(games, key=lambda g: g.genres[0].name if g.genres else "")

        if not games:
            return '<tr><td colspan="5">Nenhum jogo encontrado.</td></tr>'

        return "".join(render_game_row(g) for g in games)


def _resolve_genres(genre_ids: list, session: Session) -> list:
    ids = [int(i) for i in genre_ids if i]
    if not ids:
        return []
    return session.exec(select(Genre).where(Genre.id.in_(ids))).all()


@app.post("/games", response_class=HTMLResponse)
async def create_game(request: Request):
    form      = await request.form()
    name      = form.get("name", "").strip()
    rating    = form.get("rating", "0")
    comment   = form.get("comment", "").strip()
    genre_ids = form.getlist("genre_ids")

    if not name:
        raise HTTPException(status_code=400, detail="Nome não pode ser vazio")
    try:
        rating = float(rating)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nota inválida")

    with Session(engine) as session:
        genres = _resolve_genres(genre_ids, session)
        error  = validate_no_ancestor_conflict(genres)
        if error:
            raise HTTPException(status_code=400, detail=error)

        game = Game(name=name, rating=rating, comment=comment, genres=genres)
        session.add(game)
        session.commit()
        session.refresh(game)
        return render_game_row(game)


@app.get("/games/{game_id}/row", response_class=HTMLResponse)
def get_game_row(game_id: int):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")
        return render_game_row(game)


@app.get("/games/{game_id}/edit-form", response_class=HTMLResponse)
def edit_game_form(game_id: int):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")
        return render_game_edit_form(game, session)


@app.put("/games/{game_id}", response_class=HTMLResponse)
async def update_game(game_id: int, request: Request):
    form = await request.form()

    name      = form.get("name", "").strip()
    rating    = form.get("rating")
    comment   = form.get("comment", "").strip()
    genre_ids = form.getlist("genre_ids")

    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")

        genres = _resolve_genres(genre_ids, session)
        error  = validate_no_ancestor_conflict(genres)
        if error:
            raise HTTPException(status_code=400, detail=error)

        if name:
            game.name = name
        if rating:
            game.rating = float(rating)
        game.comment = comment
        game.genres  = genres

        session.add(game)
        session.commit()
        session.refresh(game)
        return render_game_row(game)


@app.delete("/games/{game_id}", response_class=HTMLResponse)
def delete_game(game_id: int):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Jogo não encontrado")
        session.delete(game)
        session.commit()
        return ""