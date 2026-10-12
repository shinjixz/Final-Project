from datetime import date, timedelta

import pytest

from src.exceptions import InvalidInputError, RecordNotFoundError


def test_analyze_saves_record(service):
    record = service.analyze("  so much joy  ")
    assert record.id == 1
    assert record.input_text == "so much joy"
    assert record.emotion == "joy" and len(record.hex_colors) == 8
    assert service.list_history()[0].id == 1


def test_analyze_without_save(service):
    service.analyze("joy", save=False)
    assert service.list_history() == []


def test_analyze_empty_text_rejected(service):
    with pytest.raises(InvalidInputError):
        service.analyze("   ")


def test_update_text_reanalyses(seeded):
    record = seeded.update_text(1, "now it is anger")
    assert record.emotion == "anger"
    assert seeded.get(1).hex_colors == record.hex_colors


def test_update_missing_record(seeded):
    with pytest.raises(RecordNotFoundError):
        seeded.update_text(999, "joy")


@pytest.mark.parametrize("bad_id", ["abc", "", "-1", "0", None, "1.5"])
def test_invalid_ids(seeded, bad_id):
    with pytest.raises(InvalidInputError):
        seeded.get(bad_id)


def test_delete(seeded):
    seeded.delete("2")
    assert len(seeded.list_history()) == 4
    with pytest.raises(RecordNotFoundError):
        seeded.delete(2)


def test_search_text_emotion_and_color(seeded):
    records = seeded.list_history()
    assert [r.input_text for r in seeded.search(records, "LETTER")] == ["love letter"]
    assert len(seeded.search(records, "fear")) == 1
    assert len(seeded.search(records, "#ff69b4")) == 1  # joy palette colour
    assert seeded.search(records, "nothing-matches") == []


def test_search_empty_keyword(seeded):
    with pytest.raises(InvalidInputError):
        seeded.search(seeded.list_history(), "  ")


def test_filter_by_emotion_and_confidence(seeded):
    seeded.analyze("plain text")  # fake analyser -> joy 0.55
    records = seeded.list_history()
    assert len(seeded.filter(records, emotion="JOY")) == 2
    assert len(seeded.filter(records, min_confidence=0.6)) == 5
    assert len(seeded.filter(records, emotion="joy", max_confidence=0.6)) == 1


def test_filter_by_date(seeded):
    records = seeded.list_history()
    today = date.today()
    assert len(seeded.filter(records, date_from=today, date_to=today)) == 5
    assert seeded.filter(records, date_to=today - timedelta(days=1)) == []


@pytest.mark.parametrize("kwargs", [
    {"emotion": "happy"},
    {"min_confidence": -0.05},
    {"max_confidence": 1.5},
    {"min_confidence": 0.9, "max_confidence": 0.1},
    {"date_from": date(2026, 2, 1), "date_to": date(2026, 1, 1)},
])
def test_filter_invalid_arguments(seeded, kwargs):
    with pytest.raises(InvalidInputError):
        seeded.filter(seeded.list_history(), **kwargs)


def test_sort_single_and_multi_key(seeded):
    seeded.analyze("plain text")  # joy 0.55
    records = seeded.list_history()
    by_conf = seeded.sort(records, by="confidence", descending=False)
    assert by_conf[0].confidence == 0.55
    multi = seeded.sort(records, by="emotion", descending=False, then_by="confidence")
    joys = [r.confidence for r in multi if r.emotion == "joy"]
    assert multi[0].emotion == "anger" and joys == [0.55, 0.9]
    by_id = seeded.sort(records, by="id", descending=False)
    assert [r.id for r in by_id] == [1, 2, 3, 4, 5, 6]


def test_sort_invalid_field(seeded):
    with pytest.raises(InvalidInputError):
        seeded.sort(seeded.list_history(), by="colour")


def test_sort_empty_list(seeded):
    assert seeded.sort([], by="date") == []


def test_statistics_and_insight(seeded):
    stats = seeded.statistics()
    assert stats["total"] == 5 and stats["by_emotion"]["joy"] == 1
    assert stats["average_confidence"] == 0.9
    assert "5 รายการ" in seeded.insight_report()


def test_statistics_empty(service):
    assert service.statistics() == {"total": 0, "by_emotion": {},
                                    "average_confidence": 0.0}


def test_same_text_updates_instead_of_duplicating(service):
    first = service.analyze("Joy is here")
    assert service.last_was_duplicate is False
    again = service.analyze("  joy   IS here ")
    assert service.last_was_duplicate is True
    assert again.id == first.id
    assert len(service.list_history()) == 1


def test_different_text_is_saved_separately(service):
    service.analyze("joy one")
    service.analyze("joy two")
    assert service.last_was_duplicate is False
    assert len(service.list_history()) == 2


def test_analyze_without_save_never_marks_duplicate(service):
    service.analyze("joy")
    service.analyze("joy", save=False)
    assert service.last_was_duplicate is False
