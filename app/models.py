from datetime import datetime

from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    pokemon_name: str = Field(min_length=1, max_length=50)
    note: str | None = Field(default=None, max_length=500)


class FavoriteUpdate(BaseModel):
    note: str | None = None


class Favorite(BaseModel):
    id: int
    pokemon_name: str
    user_id: str
    date_added: datetime
    note: str | None = None
