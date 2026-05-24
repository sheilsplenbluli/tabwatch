from typing import Dict, List, Optional
from app.models.tab_snapshot import TabSnapshot

_store: Dict[str, TabSnapshot] = {}


def add_snapshot(snap: TabSnapshot) -> None:
    _store[snap.snapshot_id] = snap


def get_snapshot(snapshot_id: str) -> Optional[TabSnapshot]:
    return _store.get(snapshot_id)


def get_snapshots_for_user(user_id: str) -> List[TabSnapshot]:
    return [
        s for s in _store.values()
        if s.user_id == user_id
    ]


def delete_snapshot(snapshot_id: str) -> bool:
    if snapshot_id in _store:
        del _store[snapshot_id]
        return True
    return False


def restore_snapshot(snapshot_id: str) -> Optional[TabSnapshot]:
    snap = _store.get(snapshot_id)
    if snap is None:
        return None
    snap.restore()
    return snap


def clear_all() -> None:
    _store.clear()


def snapshot_count() -> int:
    return len(_store)
