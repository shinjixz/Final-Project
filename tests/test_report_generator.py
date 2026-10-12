import csv
import json

import pytest

from src.exceptions import InvalidInputError, StorageError
from src.report_generator import ReportGenerator


def test_export_css(tmp_path):
    out = ReportGenerator.export_to_css(["#FFD700", "#FF8C00"],
                                        str(tmp_path / "x" / "p.css"))
    content = open(out, encoding="utf-8").read()
    assert "--color-1: #FFD700;" in content and "--color-2: #FF8C00;" in content


def test_export_json(tmp_path):
    out = ReportGenerator.export_to_json("joy", ["#FFD700"], str(tmp_path / "p.json"))
    assert json.load(open(out, encoding="utf-8")) == {"emotion": "joy",
                                                      "colors": ["#FFD700"]}


@pytest.mark.parametrize("palette", [[], ["red"], ["#12345"]])
def test_export_rejects_bad_palette(tmp_path, palette):
    with pytest.raises(InvalidInputError):
        ReportGenerator.export_to_css(palette, str(tmp_path / "p.css"))


def test_export_to_unwritable_path(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(StorageError):
        ReportGenerator.export_to_css(["#000000"], str(blocker / "p.css"))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_batch_processes_rows_and_skips_blank(tmp_path, service):
    src = tmp_path / "in.csv"
    write_csv(src, ["text"], [["joy day"], [""], ["sadness"], ["   "]])
    rows = ReportGenerator.process_batch_csv(str(src), service)
    assert [r["emotion"] for r in rows] == ["joy", "sadness"]
    assert len(service.list_history()) == 2

    out = ReportGenerator.write_batch_output(rows, str(tmp_path / "o" / "out.csv"))
    assert open(out, encoding="utf-8").readline().startswith("text,emotion")


def test_batch_row_error_is_recorded_not_fatal(tmp_path, service):
    src = tmp_path / "in.csv"
    write_csv(src, ["text"], [["joy"], ["x" * 2000]])
    rows = ReportGenerator.process_batch_csv(str(src), service)
    assert rows[0]["error"] == "" and "ยาวเกิน" in rows[1]["error"]


def test_batch_missing_file(service):
    with pytest.raises(StorageError):
        ReportGenerator.process_batch_csv("nope/missing.csv", service)


def test_batch_missing_text_column(tmp_path, service):
    src = tmp_path / "in.csv"
    write_csv(src, ["message"], [["joy"]])
    with pytest.raises(InvalidInputError):
        ReportGenerator.process_batch_csv(str(src), service)


def test_batch_binary_file(tmp_path, service):
    src = tmp_path / "in.csv"
    src.write_bytes(b"\xff\xfe\x00\x81garbage")
    with pytest.raises((StorageError, InvalidInputError)):
        ReportGenerator.process_batch_csv(str(src), service)


def test_sample_batch_file_is_valid():
    assert len(ReportGenerator.read_batch_csv("data/sample_batch.csv")) >= 4
