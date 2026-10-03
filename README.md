# QA Link Checker

![Tests](https://github.com/alfred-almaalouli/Qa-link-checker/actions/workflows/tests.yml/badge.svg)

A small Python command-line tool that checks a list of URLs for broken links. For every URL it records the HTTP status code and the response time, and it writes a summary report.

## Features

- Checks each URL and sorts the result into **OK** (200), **WARNING** (other status codes) or **FAILED** (no connection, timeout, invalid URL)
- Measures the response time of every request
- Saves a report with all results and a summary (total / OK / warnings / failed)
- Configurable timeout and report file
- Ignores empty lines and `#` comments in the URL list
- Returns **exit code 1** when a link fails, so it can be used as a check in a CI pipeline

## Usage

```bash
pip install -r requirements.txt

python link_checker.py                          # uses urls.txt and writes report.txt
python link_checker.py my_urls.txt --timeout 10 --report result.txt
```

Example output:

```
✅ OK (200) - https://www.google.com - 0.21s
❌ FAILED - https://thisurldoesnotexist12345.com - Error: ...
```

## Tests

Unit tests are written with **pytest**. The HTTP requests are replaced with mocks (`unittest.mock`), so the tests run fast and do not depend on the internet.

```bash
pytest -v
```

Covered cases: status 200, status 404, connection error, timeout, URL file parsing, report content and the exit code of the command.

The tests run automatically with **GitHub Actions** on every push.

## Tech stack

Python · requests · pytest · unittest.mock · GitHub Actions
