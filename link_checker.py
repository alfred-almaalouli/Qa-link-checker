import argparse
import sys
import time

import requests


def check_link(url, timeout=5):
    """Checks one URL and returns the result as a dictionary."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = round(time.time() - start_time, 2)

        status = "OK" if response.status_code == 200 else "WARNING"
        return {"url": url, "status": status, "code": response.status_code,
                "time": elapsed, "error": None}
    except requests.exceptions.RequestException as e:
        return {"url": url, "status": "FAILED", "code": None, "time": None,
                "error": str(e)}


def format_result(result):
    if result["status"] == "FAILED":
        return f"FAILED - {result['url']} - Error: {result['error']}"
    return f"{result['status']} ({result['code']}) - {result['url']} - {result['time']}s"


def load_urls(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file
                if line.strip() and not line.strip().startswith("#")]


def save_report(results, filename="report.txt"):
    ok = sum(r["status"] == "OK" for r in results)
    warnings = sum(r["status"] == "WARNING" for r in results)
    failed = sum(r["status"] == "FAILED" for r in results)

    with open(filename, "w") as file:
        file.write("QA Link Check Report\n")
        file.write("=" * 40 + "\n\n")
        for result in results:
            file.write(format_result(result) + "\n")
        file.write("\n" + "-" * 40 + "\n")
        file.write(f"Total: {len(results)} | OK: {ok} | Warnings: {warnings} | Failed: {failed}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a list of URLs for broken links.")
    parser.add_argument("file", nargs="?", default="urls.txt", help="text file with one URL per line")
    parser.add_argument("--timeout", type=float, default=5, help="timeout per request in seconds")
    parser.add_argument("--report", default="report.txt", help="where to save the report")
    args = parser.parse_args(argv)

    results = []
    for url in load_urls(args.file):
        result = check_link(url, args.timeout)
        icon = {"OK": "✅", "WARNING": "⚠️", "FAILED": "❌"}[result["status"]]
        print(f"{icon} {format_result(result)}")
        results.append(result)

    save_report(results, args.report)
    print(f"\n📄 Report saved to {args.report}")

    # exit code 1 if any link failed, so the check can be used in a CI pipeline
    return 1 if any(r["status"] == "FAILED" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
