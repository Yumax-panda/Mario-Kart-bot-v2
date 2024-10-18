from __future__ import annotations

import json
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, db, initialize_app

from .types.firebase import FirebaseService as IFirebaseService

__all__ = ("FirebaseService",)

if TYPE_CHECKING:
    from .types import GamePayload


class FirebaseService(IFirebaseService):

    if TYPE_CHECKING:
        ref: db.Reference

    def __init__(self, firebase_key: str, firebase_url: str):
        ref = self.__connect_to_firebase(firebase_key, firebase_url)
        self.ref = ref

    def update_game_data(self, data: dict[str, GamePayload]) -> None:
        return self.ref.update(data)

    def __connect_to_firebase(self, cert: str, url: str) -> db.Reference:
        TABLE_NAME = "user"

        is_connected = len(firebase_admin._apps) > 0

        if not is_connected:
            cred = credentials.Certificate(json.loads(cert, strict=False))
            initialize_app(
                cred,
                {"databaseURL": url},
            )
        return db.reference(TABLE_NAME)
