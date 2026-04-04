from pathlib import Path

from relaytic.security.git_guard import scan_files_for_leaks


def test_git_guard_detects_token_pattern(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("token = sk-abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")
    findings = scan_files_for_leaks([sample])
    assert findings


def test_git_guard_skips_safe_text(tmp_path: Path) -> None:
    sample = tmp_path / "safe.txt"
    sample.write_text("hello world", encoding="utf-8")
    findings = scan_files_for_leaks([sample])
    assert not findings


def test_git_guard_does_not_flag_function_calls_named_token(tmp_path: Path) -> None:
    sample = tmp_path / "runtime_stage.py"
    sample.write_text("token = record_stage_start(run_dir=run_dir)\n", encoding="utf-8")
    findings = scan_files_for_leaks([sample])
    assert not findings


def test_git_guard_still_flags_literal_secret_assignments(tmp_path: Path) -> None:
    sample = tmp_path / "secret_assignment.py"
    sample.write_text('token = "abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8")
    findings = scan_files_for_leaks([sample])
    assert any(item.pattern_name == "generic_secret_assignment" for item in findings)

