from typing import Optional
from app.models.annotation import Annotation

_store: dict[str, Annotation] = {}


def add_annotation(annotation: Annotation) -> None:
    _store[annotation.id] = annotation


def get_annotation(annotation_id: str) -> Optional[Annotation]:
    return _store.get(annotation_id)


def get_annotations_for_user(user_id: str) -> list[Annotation]:
    return [a for a in _store.values() if a.user_id == user_id]


def get_annotations_for_domain(user_id: str, domain: str) -> list[Annotation]:
    return [
        a for a in _store.values()
        if a.user_id == user_id and a.domain == domain
    ]


def update_annotation(annotation_id: str, body: str = None, label: str = None) -> Optional[Annotation]:
    ann = _store.get(annotation_id)
    if ann is None:
        return None
    ann.update(body=body, label=label)
    return ann


def delete_annotation(annotation_id: str) -> bool:
    if annotation_id in _store:
        del _store[annotation_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()


def annotation_count() -> int:
    return len(_store)
