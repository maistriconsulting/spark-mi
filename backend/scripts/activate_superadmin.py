#!/usr/bin/env python3
"""One-time superadmin activation, run interactively on the API host.

Reads BOOTSTRAP_TOKEN from the protected env file, asks for the password,
creates the account, verifies it, then removes the token and restarts the API.
The password and the token are never printed, logged or passed as arguments.
Safe to re-run if a previous attempt stopped halfway.
"""
import argparse
import getpass
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

EMAIL = "info@maistriconsulting.com"
TOKEN_LINE = re.compile(r"(?m)^BOOTSTRAP_TOKEN=(.*)$")


def call(base, path, body=None, headers=None):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, {}


def check(condition, message):
    if not condition:
        sys.exit(f"ERRORE: {message}")
    print(f"ok  {message}")


def wait_for_api(base):
    for _ in range(30):
        try:
            if call(base, "/ready")[0] == 200:
                return True
        except OSError:
            pass
        time.sleep(1)
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8800/api/v1")
    parser.add_argument("--env-file", default=str(Path(__file__).resolve().parents[1] / ".env"))
    parser.add_argument("--service", default="spark-mi-api")
    args = parser.parse_args()
    base = args.base_url
    env_file = Path(args.env_file).resolve()

    match = TOKEN_LINE.search(env_file.read_text())
    token = match.group(1).strip().strip("\"'") if match else ""
    status, body = call(base, "/auth/bootstrap-status")
    check(status == 200, "API raggiungibile")
    initialized = body["initialized"]
    if not initialized and not token:
        sys.exit("ERRORE: BOOTSTRAP_TOKEN non configurato")

    if initialized:
        print("Account gia' creato: verifico l'accesso e completo la chiusura.")
        password = getpass.getpass(f"Password di {EMAIL}: ")
    else:
        password = getpass.getpass(f"Nuova password per {EMAIL} (minimo 12 caratteri): ")
        if not 12 <= len(password) <= 128:
            sys.exit("ERRORE: la password deve avere tra 12 e 128 caratteri")
        if getpass.getpass("Ripeti la password: ") != password:
            sys.exit("ERRORE: le password non coincidono")

    credentials = {"email": EMAIL, "password": password}
    bootstrap_headers = {"X-Bootstrap-Token": token}
    if not initialized:
        status, _ = call(base, "/auth/bootstrap", credentials, bootstrap_headers)
        check(status == 201, f"superadmin creato (HTTP {status})")

    status, login = call(base, "/auth/login", credentials)
    check(status == 200 and login.get("is_superadmin") is True, f"login superadmin (HTTP {status})")
    status, _ = call(base, "/auth/platform/overview", headers={"Authorization": "Bearer " + login["access_token"]})
    check(status == 200, f"panoramica piattaforma (HTTP {status})")

    if token:
        status, _ = call(base, "/auth/bootstrap", credentials, bootstrap_headers)
        check(status == 409, f"secondo bootstrap rifiutato con il token ancora attivo (HTTP {status})")
        # Write through the symlink target so file permissions are preserved.
        env_file.write_text(TOKEN_LINE.sub("BOOTSTRAP_TOKEN=", env_file.read_text()))
        subprocess.run(["systemctl", "--user", "restart", args.service], check=True)
        check(wait_for_api(base), "token rimosso e API riavviata")
        status, _ = call(base, "/auth/bootstrap", credentials, bootstrap_headers)
        check(status == 404, f"bootstrap disattivato (HTTP {status})")

    status, _ = call(base, "/auth/login", credentials)
    check(status == 200, "login finale")
    print("\nAttivazione completata.")


if __name__ == "__main__":
    main()
