import pytest
from datetime import datetime, timezone
from app.models.annotation import Annotation


def make_annotation(**kwargs) -> Annotation:
    defaults = dict(user_id="u1", domain="example.com", body="interesting site")
    defaults.update(kwargs)
    return Annotation(**defaults)


def test_annotation_defaults():
    ann = make_annotation()
    assert ann.user_id == "u1"
    assert ann.domain == "example.com"
    assert ann.body == "interesting site"
    assert ann.label == ""
    assert ann.id is not None
    assert ann.updated_at is None


def test_to_dict_contains_expected_keys():
    ann = make_annotation(label="research")
    d = ann.to_dict()
    assert d["user_id"] == "u1"
    assert d["domain"] == "example.com"
    assert d["body"] == "interesting site"
    assert d["label"] == "research"
    assert "id" in d
    assert "created_at" in d
    assert d["updated_at"] is None


def test_update_body_changes_body():
    ann = make_annotation()
    ann.update(body="updated body")
    assert ann.body == "updated body"
    assert ann.updated_at is not None


def test_update_label_changes_label():
    ann = make_annotation()
    ann.update(label="productive")
    assert ann.label == "productive"


def test_update_blank_body_raises():
    ann = make_annotation()
    with pytest.raises(ValueError):
        ann.update(body="   ")


def test_from_dict_roundtrip():
    ann = make_annotation(label="distraction")
    d = ann.to_dict()
    restored = Annotation.from_dict(d)
    assert restored.id == ann.id
    assert restored.user_id == ann.user_id
    assert restored.domain == ann.domain
    assert restored.body == ann.body
    assert restored.label == ann.label


def test_unique_ids():
    a1 = make_annotation()
    a2 = make_annotation()
    assert a1.id != a2.id
