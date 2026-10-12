from datetime import datetime, timezone
from itertools import count

from fastapi import Depends, FastAPI, HTTPException, status

from app.auth import (
    LoginRequest,
    TokenResponse,
    create_access_token,
    get_current_user,
)
from app.models import Favorite, FavoriteCreate, FavoriteUpdate

app = FastAPI(title="Favorites API")

favorites: dict[int, Favorite] = {}
id_counter = count(1)


def get_owned_or_404(favorite_id: int, user: str) -> Favorite:
    fav = favorites.get(favorite_id)
    if fav is None or fav.user_id != user:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return fav


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(data.username))


@app.post("/favorites", response_model=Favorite, status_code=status.HTTP_201_CREATED)
def create_favorite(
    data: FavoriteCreate, user: str = Depends(get_current_user)
) -> Favorite:
    fav = Favorite(
        id=next(id_counter),
        pokemon_name=data.pokemon_name,
        user_id=user,
        date_added=datetime.now(timezone.utc),
        note=data.note,
    )
    favorites[fav.id] = fav
    return fav


@app.get("/favorites", response_model=list[Favorite])
def list_favorites(user: str = Depends(get_current_user)) -> list[Favorite]:
    return [f for f in favorites.values() if f.user_id == user]


@app.get("/favorites/{favorite_id}", response_model=Favorite)
def get_favorite(favorite_id: int, user: str = Depends(get_current_user)) -> Favorite:
    return get_owned_or_404(favorite_id, user)


@app.patch("/favorites/{favorite_id}", response_model=Favorite)
def update_favorite(
    favorite_id: int, data: FavoriteUpdate, user: str = Depends(get_current_user)
) -> Favorite:
    fav = get_owned_or_404(favorite_id, user)
    updated = fav.model_copy(update=data.model_dump(exclude_unset=True))
    favorites[favorite_id] = updated
    return updated


@app.delete("/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(favorite_id: int, user: str = Depends(get_current_user)) -> None:
    get_owned_or_404(favorite_id, user)
    del favorites[favorite_id]
