#!/usr/bin/env python3
"""Submit job-leaderboard output to the CS5220 HW3 leaderboard server."""

import sys
import re
import urllib.request
import urllib.error
import json

SERVER_URL = "https://leaderboard-zm07.onrender.com/"

HEADER = "===== CS5220 HW3 LEADERBOARD SUBMISSION ====="
FOOTER = "===== END CS5220 HW3 LEADERBOARD SUBMISSION ====="

ERR = "AssertionError"


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output-file>")
        print("  Submit the output of job-leaderboard to the leaderboard server.")
        sys.exit(1)

    output_file = sys.argv[1]

    try:
        with open(output_file) as f:
            raw_output = f.read()
    except FileNotFoundError:
        print(f"Error: File '{output_file}' not found.")
        sys.exit(1)

    if ERR in raw_output:
        print("Output file contains an AssertionError, meaning your implementation fails one of the correctness checks.")
        sys.exit(1)

    if HEADER not in raw_output:
        print("Error: Output file is missing the leaderboard header.")
        print("       Make sure this is the output of job-leaderboard.")
        sys.exit(1)

    if FOOTER not in raw_output:
        print("Error: Output file is missing the leaderboard footer.")
        print("       The job may not have completed successfully.")
        sys.exit(1)

    name_match = re.search(r"LEADERBOARD_NAME:\s*(\S+)", raw_output)
    if not name_match:
        print("Error: Could not find LEADERBOARD_NAME in output.")
        sys.exit(1)

    name = name_match.group(1)

    url = f"{SERVER_URL}/api/submit"
    req = urllib.request.Request(
        url,
        data=raw_output.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"Submitted successfully!")
            print(f"  Name: {result['name']}")
            print(f"  Timestamp: {result['timestamp']}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            error = json.loads(body)
            print(f"Submission failed: {error.get('error', body)}")
        except json.JSONDecodeError:
            print(f"Submission failed (HTTP {e.code}): {body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not connect to leaderboard server at {SERVER_URL}")
        print(f"       {e.reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()

