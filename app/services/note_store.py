import uuid
from typing import Optional

from app.models.note import Note

_store: dict[str, Note] = {}


def add_note(note: Note) -> Note:
    if not note.note_id:
        note.note_id = str(uuid.uuid4())
    _store[note.note_id] = note
    return note


def get_note(note_id: str) -> Optional[Note]:
    return _store.get(note_id)


def get_notes_for_user(user_id: str) -> list[Note]:
    return [n for n in _store.values() if n.user_id == user_id]


def get_notes_for_domain(user_id: str, domain: str) -> list[Note]:
    return [
        n for n in _store.values()
        if n.user_id == user_id and n.domain == domain
    ]


def update_note(note_id: str, new_body: str) -> Optional[Note]:
    note = _store.get(note_id)
    if note is None:
        return None
    note.update_body(new_body)
    return note


def delete_note(note_id: str) -> bool:
    if note_id in _store:
        del _store[note_id]
        return True
    return False


def clear_all_notes() -> None:
    _store.clear()


def note_count() -> int:
    return len(_store)
