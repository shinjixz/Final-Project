"""Integration tests: drive the real CLI with scripted input."""
from src.cli_app import CLIApp


def run(service, *answers):
    inputs = iter(answers)
    output = []
    app = CLIApp(service, input_func=lambda prompt: next(inputs),
                 output_func=output.append, use_color=False)
    app.run()
    return "\n".join(output)


def test_quit_is_case_insensitive(service):
    for word in ("QUIT", " Quit ", "exit", "0", "ออก"):
        assert "ขอบคุณ" in run(service, word)


def test_full_crud_flow(service):
    out = run(service,
              "1", "joy is here",           # create
              "1", "sadness",               # create
              "4", "1", "anger now",        # update
              "5", "2", "y",                # delete
              "2",                          # list
              "0")
    assert "บันทึกแล้ว id=1" in out and "แก้ไขแล้ว" in out and "ลบแล้ว" in out
    remaining = service.list_history()
    assert [(r.id, r.emotion) for r in remaining] == [(1, "anger")]


def test_invalid_inputs_never_crash(service):
    out = run(service,
              "99",                 # unknown menu
              "1", "   ",           # empty text
              "3", "abc",           # non-numeric id
              "5", "42",            # missing id
              "7", "happy",         # unknown emotion
              "7", "", "abc",       # non-numeric confidence
              "7", "", "", "", "13-10-2026",  # bad date
              "8", "colour",        # bad sort field
              "10", "missing.csv",  # missing file
              "QUIT")
    assert out.count("⚠️") == 9
    assert "ไม่คาดคิด" not in out and "ขอบคุณ" in out


def test_cancel_delete(service):
    service.analyze("joy")
    out = run(service, "5", "1", "n", "0")
    assert "ยกเลิกการลบ" in out and len(service.list_history()) == 1


def test_search_filter_sort_from_menu(seeded):
    out = run(seeded,
              "6", "dark",
              "7", "love", "50", "", "", "",
              "8", "confidence", "id", "n",
              "11",
              "0")
    assert "fear of the dark" in out and "love letter" in out
    assert "วิเคราะห์ทั้งหมด 5 รายการ" in out


def test_export_from_menu(service, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    service.analyze("joy")
    out = run(service, "9", "1", "0")
    assert (tmp_path / "exports" / "palette_1.css").exists()
    assert "ส่งออก" in out


def test_ctrl_c_exits_gracefully(service):
    def interrupt(prompt):
        raise KeyboardInterrupt
    output = []
    CLIApp(service, input_func=interrupt, output_func=output.append).run()
    assert "ยกเลิกการทำงาน" in output[-1]
