"""Tests for check_ssh2web. Stdlib + pytest; offline, no network or install."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "ssh2web" / "scripts" / "check_ssh2web.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_ssh2web", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_ssh2web"] = mod
    spec.loader.exec_module(mod)
    return mod


cs = _load()


def test_install_cmd_points_at_public_repo():
    assert cs.REPO == "https://github.com/wservices/ssh2web"
    assert cs.INSTALL_CMD.startswith("python3 -m pip install")
    assert "gitlab" not in cs.INSTALL_CMD  # no internal host leaks


def test_missing_client_reports_install(monkeypatch, capsys):
    monkeypatch.setattr(cs, "find_client", lambda: None)
    rc = cs.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "not found" in out
    assert "pip install" in out


def test_present_client_prints_version(monkeypatch, capsys):
    monkeypatch.setattr(cs, "find_client", lambda: "/usr/bin/ssh2web")
    monkeypatch.setattr(cs, "client_version", lambda exe: "ssh2web 0.1.0")
    rc = cs.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "/usr/bin/ssh2web" in out
    assert "0.1.0" in out


def test_present_but_version_fails_is_error(monkeypatch, capsys):
    monkeypatch.setattr(cs, "find_client", lambda: "/usr/bin/ssh2web")
    monkeypatch.setattr(cs, "client_version", lambda exe: None)
    rc = cs.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "did not run" in out
