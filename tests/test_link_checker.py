from unittest.mock import Mock, patch

import requests

from link_checker import check_link, format_result, load_urls, main, save_report


def fake_response(status_code):
    response = Mock()
    response.status_code = status_code
    return response


@patch("link_checker.requests.get", return_value=fake_response(200))
def test_status_200_is_ok(mock_get):
    result = check_link("https://example.com")

    assert result["status"] == "OK"
    assert result["code"] == 200
    mock_get.assert_called_once_with("https://example.com", timeout=5)


@patch("link_checker.requests.get", return_value=fake_response(404))
def test_status_404_is_warning(mock_get):
    result = check_link("https://example.com/missing")

    assert result["status"] == "WARNING"
    assert result["code"] == 404


@patch("link_checker.requests.get", side_effect=requests.exceptions.ConnectionError("no connection"))
def test_connection_error_is_failed(mock_get):
    result = check_link("https://does-not-exist.example")

    assert result["status"] == "FAILED"
    assert "no connection" in result["error"]


@patch("link_checker.requests.get", side_effect=requests.exceptions.Timeout("timed out"))
def test_timeout_is_failed(mock_get):
    result = check_link("https://slow.example", timeout=1)

    assert result["status"] == "FAILED"
    mock_get.assert_called_once_with("https://slow.example", timeout=1)


def test_load_urls_skips_empty_lines_and_comments(tmp_path):
    file = tmp_path / "urls.txt"
    file.write_text("https://a.example\n\n# comment\n  https://b.example  \n")

    assert load_urls(file) == ["https://a.example", "https://b.example"]


def test_report_contains_results_and_summary(tmp_path):
    results = [
        {"url": "https://a.example", "status": "OK", "code": 200, "time": 0.1, "error": None},
        {"url": "https://b.example", "status": "FAILED", "code": None, "time": None, "error": "boom"},
    ]
    report = tmp_path / "report.txt"

    save_report(results, report)
    text = report.read_text()

    assert "OK (200) - https://a.example - 0.1s" in text
    assert "FAILED - https://b.example - Error: boom" in text
    assert "Total: 2 | OK: 1 | Warnings: 0 | Failed: 1" in text


def test_format_result_warning():
    result = {"url": "https://c.example", "status": "WARNING", "code": 500, "time": 0.3, "error": None}

    assert format_result(result) == "WARNING (500) - https://c.example - 0.3s"


@patch("link_checker.requests.get", return_value=fake_response(200))
def test_main_returns_0_when_all_links_work(mock_get, tmp_path):
    urls = tmp_path / "urls.txt"
    urls.write_text("https://a.example\nhttps://b.example\n")

    assert main([str(urls), "--report", str(tmp_path / "r.txt")]) == 0


@patch("link_checker.requests.get", side_effect=requests.exceptions.ConnectionError("down"))
def test_main_returns_1_when_a_link_fails(mock_get, tmp_path):
    urls = tmp_path / "urls.txt"
    urls.write_text("https://a.example\n")

    assert main([str(urls), "--report", str(tmp_path / "r.txt")]) == 1
