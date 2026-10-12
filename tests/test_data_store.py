import os
import sqlite3

import pytest

from src.data_store import DataStore
from src.exceptions import RecordNotFoundError, StorageError
from src.models import AnalysisRecord


def make(text="hello", emotion="joy"):
    return AnalysisRecord(input_text=text, emotion=emotion, confidence=0.8,
                          hex_colors=["#000000", "#FFFFFF"])


def test_creates_missing_folder(tmp_path):
    path = tmp_path / "missing" / "nested" / "h.db"
    DataStore(str(path))
    assert path.exists()


def test_crud_cycle(store):
    record = store.add(make())
    assert record.id == 1
    assert store.get(1).input_text == "hello"
    assert store.get(1).hex_colors == ["#000000", "#FFFFFF"]

    record.input_text = "changed"
    store.update(record)
    assert store.get(1).input_text == "changed"

    store.delete(1)
    with pytest.raises(RecordNotFoundError):
        store.get(1)


def test_list_newest_first_and_limit(store):
    for i in range(5):
        store.add(make(f"t{i}"))
    assert [r.input_text for r in store.list_all()][:2] == ["t4", "t3"]
    assert len(store.get_history(limit=3)) == 3
    assert store.count() == 5


@pytest.mark.parametrize("op", ["get", "delete"])
def test_missing_id_raises(store, op):
    with pytest.raises(RecordNotFoundError):
        getattr(store, op)(42)


def test_update_missing_raises(store):
    record = make()
    record.id = 42
    with pytest.raises(RecordNotFoundError):
        store.update(record)


def test_clear(store):
    store.add(make())
    store.add(make())
    assert store.clear() == 2
    assert store.list_all() == []


def test_persists_across_instances(tmp_path):
    path = str(tmp_path / "p.db")
    DataStore(path).add(make("persist me"))
    assert DataStore(path).list_all()[0].input_text == "persist me"


def test_recovers_from_corrupted_database(tmp_path):
    path = tmp_path / "broken.db"
    path.write_bytes(b"this is definitely not a sqlite file" * 100)
    store = DataStore(str(path))
    assert store.recovered_from and os.path.exists(store.recovered_from)
    store.add(make())
    assert store.count() == 1


def test_bad_json_colors_do_not_crash(store):
    store.add(make())
    conn = sqlite3.connect(store.db_path)
    conn.execute("UPDATE palette_history SET hex_colors = 'not json'")
    conn.commit()
    conn.close()
    assert store.get(1).hex_colors == []


def test_storage_error_when_table_dropped(store):
    conn = sqlite3.connect(store.db_path)
    conn.execute("DROP TABLE palette_history")
    conn.close()
    with pytest.raises(StorageError):
        store.list_all()
