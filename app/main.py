from datetime import datetime, timezone
from itertools import count

from fastapi import FastAPI, HTTPException, status

from app.models import Favorite, FavoriteCreate, FavoriteUpdate

app = FastAPI(title="Favorites API")

favorites: dict[int, Favorite] = {}
id_counter = count(1)
CURRENT_USER = "demo-user"  # swapped for the JWT user in Phase 4


def get_owned_or_404(favorite_id: int) -> Favorite:
    fav = favorites.get(favorite_id)
    if fav is None or fav.user_id != CURRENT_USER:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return fav


@app.post("/favorites", response_model=Favorite, status_code=status.HTTP_201_CREATED)
def create_favorite(data: FavoriteCreate) -> Favorite:
    fav = Favorite(
        id=next(id_counter),
        pokemon_name=data.pokemon_name,
        user_id=CURRENT_USER,
        date_added=datetime.now(timezone.utc),
        note=data.note,
    )
    favorites[fav.id] = fav
    return fav


@app.get("/favorites", response_model=list[Favorite])
def list_favorites() -> list[Favorite]:
    return [f for f in favorites.values() if f.user_id == CURRENT_USER]


@app.get("/favorites/{favorite_id}", response_model=Favorite)
def get_favorite(favorite_id: int) -> Favorite:
    return get_owned_or_404(favorite_id)


@app.patch("/favorites/{favorite_id}", response_model=Favorite)
def update_favorite(favorite_id: int, data: FavoriteUpdate) -> Favorite:
    fav = get_owned_or_404(favorite_id)
    updated = fav.model_copy(update=data.model_dump(exclude_unset=True))
    favorites[favorite_id] = updated
    return updated


@app.delete("/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(favorite_id: int) -> None:
    get_owned_or_404(favorite_id)
    del favorites[favorite_id]