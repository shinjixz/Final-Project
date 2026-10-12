import main


def test_batch_mode_end_to_end(tmp_path, capsys):
    out = tmp_path / "out.csv"
    code = main.main(["--offline", "--db", str(tmp_path / "t.db"),
                      "--batch", "data/sample_batch.csv", "--output", str(out)])
    assert code == 0 and out.exists()
    assert "ผิดพลาด 0" in capsys.readouterr().out


def test_batch_mode_missing_file_returns_error(tmp_path, capsys):
    code = main.main(["--offline", "--db", str(tmp_path / "t.db"),
                      "--batch", "nope.csv"])
    assert code == 1 and "ไม่พบไฟล์" in capsys.readouterr().out
