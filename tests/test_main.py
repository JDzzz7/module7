
import sys
import logging
from pathlib import Path
from unittest.mock import patch

import pytest
import main


# Test 1: Logging setup
def test_setup_logging():
    with patch("main.logging.basicConfig") as mock_logging:
        main.setup_logging()
        mock_logging.assert_called_once()


# Test 2: Create directory successfully
def test_create_directory(tmp_path):
    directory = tmp_path / "qr_codes"

    main.create_directory(directory)

    assert directory.exists()
    assert directory.is_dir()


# Test 3: Directory creation failure
def test_create_directory_failure(tmp_path):
    directory = tmp_path / "qr_codes"

    with patch.object(Path, "mkdir",
                      side_effect=PermissionError("Access denied")):
        with patch("main.logging.error") as mock_error:
            with pytest.raises(SystemExit) as exc:
                main.create_directory(directory)

    assert exc.value.code == 1
    mock_error.assert_called_once()


# Test 4: Valid URL
def test_valid_url():
    assert main.is_valid_url(
        "https://github.com/JDzzz7"
    ) is True


# Test 5: Invalid URL
def test_invalid_url():
    assert main.is_valid_url(
        "not-a-valid-url"
    ) is False


# Test 6: Generate QR code successfully
def test_generate_qr_code(tmp_path):
    output_file = tmp_path / "test_qr.png"

    main.generate_qr_code(
        "https://github.com/JDzzz7",
        output_file
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0


# Test 7: Invalid URL should not generate QR code
def test_generate_qr_code_invalid_url(tmp_path):
    output_file = tmp_path / "invalid_qr.png"

    main.generate_qr_code(
        "invalid-url",
        output_file
    )

    assert not output_file.exists()


# Test 8: QR code generation error
def test_generate_qr_code_error(tmp_path):
    output_file = tmp_path / "missing" / "test.png"

    with patch("main.logging.error") as mock_error:
        main.generate_qr_code(
            "https://github.com/JDzzz7",
            output_file
        )

    assert not output_file.exists()
    mock_error.assert_called_once()


# Test 9: Main application with default URL
def test_main_default_url(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py"])

    main.main()

    files = list((tmp_path / "qr_codes").glob("*.png"))

    assert len(files) == 1
    assert files[0].stat().st_size > 0


# Test 10: Main application with custom URL
def test_main_custom_url(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--url",
            "https://github.com/JDzzz7"
        ]
    )

    main.main()

    files = list((tmp_path / "qr_codes").glob("*.png"))

    assert len(files) == 1
    assert files[0].stat().st_size > 0

# Test 11: Execute main.py as a script
def test_main_as_script(tmp_path):
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            str(Path(main.__file__)),
            "--url",
            "https://github.com/JDzzz7"
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "QR code successfully saved" in result.stdout

# Test 12: Execute main.py as __main__
def test_main_entry_point(tmp_path, monkeypatch):
    import runpy

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--url", "https://github.com/JDzzz7"]
    )

    runpy.run_path(main.__file__, run_name="__main__")

    files = list((tmp_path / "qr_codes").glob("*.png"))

    assert len(files) == 1
    assert files[0].stat().st_size > 0