#!/usr/bin/env python3
"""
drillr.py — unified dispatcher for the drillr REST API.

Usage:
  python drillr.py setup-key <drl_...>          # store key in ~/.drillr/config.json (mode 0600)
  python drillr.py probe                        # verify key works (calls list_tables)
  python drillr.py call <tool> [--json BODY] [--query Q]
                                                # POST/GET /api/v1/data/<tool>

Tools:
  POST: run_sql, sec_report_search, company_search
  GET:  sec_report_list, signal_list, list_tables, get_table_schema, fiscal_utility

Output:
  Success -> stdout: pretty-printed JSON response, exit 0
  Error   -> stderr first line: "<CODE>: <message>", exit code per table below

Exit codes:
  0  ok
  1  generic (network / parse / usage)
  2  NO_KEY        — ~/.drillr/config.json missing or empty
  3  INVALID_KEY   — 401 / 403 from gateway
  4  RATE_LIMIT    — 429
  5  API_ERROR     — other 4xx / 5xx

No third-party deps (stdlib only).
"""

import argparse
import json
import os
import ssl
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GATEWAY_URL = os.environ.get("DRILLR_GATEWAY_URL", "https://gateway.drillr.ai")
CONFIG_PATH = Path.home() / ".drillr" / "config.json"

# tool -> HTTP method. Mirrors gateway's /api/v1/data/* routes.
TOOL_METHODS = {
    "run_sql": "POST",
    "sec_report_search": "POST",
    "company_search": "POST",
    "sec_report_list": "GET",
    "signal_list": "GET",
    "list_tables": "GET",
    "get_table_schema": "GET",
    "fiscal_utility": "GET",
}


def die(code: int, label: str, message: str, body: str = "") -> "None":
    print(f"{label}: {message}", file=sys.stderr)
    if body:
        print(body, file=sys.stderr)
    sys.exit(code)


def mask_key(key: str) -> str:
    if len(key) < 12:
        return "drl_***"
    return f"{key[:8]}...{key[-4:]}"


def load_key() -> str:
    if not CONFIG_PATH.exists():
        die(
            2,
            "NO_KEY",
            f"no config at {CONFIG_PATH}. Run: python scripts/drillr.py setup-key <drl_...>",
        )
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except (OSError, json.JSONDecodeError) as e:
        die(2, "NO_KEY", f"failed to read {CONFIG_PATH}: {e}")
    key = data.get("api_key")
    if not key or not isinstance(key, str):
        die(2, "NO_KEY", f"{CONFIG_PATH} missing 'api_key' field")
    return key


def cmd_setup_key(args: argparse.Namespace) -> None:
    key = args.key.strip()
    if not key:
        die(1, "USAGE", "empty key")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({"api_key": key}, indent=2) + "\n")
    os.chmod(CONFIG_PATH, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    print(json.dumps({"ok": True, "path": str(CONFIG_PATH), "key": mask_key(key)}, indent=2))


def _make_ssl_context() -> ssl.SSLContext:
    # Fall back to the system CA bundle when Python's default location is empty.
    # python.org's macOS installer ships without certs unless "Install Certificates.command"
    # has been run; this avoids forcing every drillr user to discover that.
    ctx = ssl.create_default_context()
    paths = ssl.get_default_verify_paths()
    if paths.cafile and Path(paths.cafile).exists():
        return ctx
    for candidate in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
        if Path(candidate).exists():
            try:
                ctx.load_verify_locations(cafile=candidate)
                return ctx
            except OSError:
                continue
    return ctx


def http_call(method: str, path: str, query: str = "", body: "dict | None" = None) -> dict:
    key = load_key()
    url = f"{GATEWAY_URL}{path}"
    if query:
        url = f"{url}?{query}"

    data = None
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "User-Agent": "drillr-skill/2.0",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60, context=_make_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        if e.code in (401, 403):
            die(3, "INVALID_KEY", f"{e.code} from {url}", raw)
        if e.code == 429:
            die(4, "RATE_LIMIT", f"429 from {url}", raw)
        die(5, "API_ERROR", f"{e.code} from {url}", raw)
    except urllib.error.URLError as e:
        die(1, "NETWORK", f"failed to reach {url}: {e.reason}")
    except (json.JSONDecodeError, ValueError) as e:
        die(1, "PARSE", f"failed to decode response from {url}: {e}")
    return {}  # unreachable, satisfies type checker


def cmd_probe(args: argparse.Namespace) -> None:
    # signal_list with limit=1 is the lightest unauthenticated-payload tool
    # (all params optional, 2 cr per call). Use it just to confirm the key
    # is valid and the gateway is reachable.
    out = http_call("GET", "/api/v1/data/signal_list", query="limit=1")
    summary = {
        "ok": True,
        "gateway": GATEWAY_URL,
        "key": mask_key(load_key()),
    }
    if isinstance(out, dict):
        if "_credits" in out:
            summary["credits"] = out["_credits"]
        if "data" in out and isinstance(out["data"], dict):
            sample = out["data"].get("signals")
            if isinstance(sample, list):
                summary["signals_returned"] = len(sample)
    print(json.dumps(summary, indent=2))


def cmd_call(args: argparse.Namespace) -> None:
    tool = args.tool
    if tool not in TOOL_METHODS:
        die(
            1,
            "USAGE",
            f"unknown tool '{tool}'. Valid: {', '.join(sorted(TOOL_METHODS))}",
        )
    method = TOOL_METHODS[tool]
    path = f"/api/v1/data/{tool}"

    body = None
    query = ""

    if args.json:
        try:
            body = json.loads(args.json)
        except json.JSONDecodeError as e:
            die(1, "USAGE", f"--json is not valid JSON: {e}")
        if method == "GET":
            # GET tools read params from query string. We accept --json as a
            # convenience (so callers can use the same {k:v} shape as POST),
            # but the top-level must be an object. Anything else is a usage error.
            if not isinstance(body, dict):
                die(
                    1,
                    "USAGE",
                    f"--json for GET tool '{tool}' must be a JSON object (got {type(body).__name__}). "
                    f"Use --query 'k=v&k=v' instead, or pass a dict like --json '{{\"ticker\":\"AAPL\"}}'.",
                )
            query = urllib.parse.urlencode(
                {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in body.items()}
            )
            body = None
    elif args.query:
        if method != "GET":
            die(1, "USAGE", f"--query only valid for GET tools; '{tool}' is {method}. Use --json '{{...}}' instead.")
        query = args.query

    if method == "POST" and body is None:
        die(1, "USAGE", f"--json required for POST tool '{tool}' (e.g. --json '{{\"ticker\":\"AAPL\"}}')")
    if method == "GET" and not query and not args.json:
        die(1, "USAGE", f"GET tool '{tool}' requires --query 'k=v&k=v' or --json '{{...}}'.")

    out = http_call(method, path, query=query, body=body)
    print(json.dumps(out, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="drillr",
        description="drillr REST dispatcher (skill v2)",
    )
    # required=True needs Python 3.7+; emulate it for 3.6 (default on
    # older Linux distros — Alibaba Cloud 8, CentOS 7, etc.).
    sub = parser.add_subparsers(dest="cmd")

    sp = sub.add_parser("setup-key", help="store drl_* key in ~/.drillr/config.json")
    sp.add_argument("key", help="the drl_... key from drillr.ai/developer/keys")
    sp.set_defaults(func=cmd_setup_key)

    sp = sub.add_parser("probe", help="verify stored key works")
    sp.set_defaults(func=cmd_probe)

    sp = sub.add_parser("call", help="invoke a data tool")
    sp.add_argument("tool", help=f"one of: {', '.join(sorted(TOOL_METHODS))}")
    sp.add_argument("--json", help="JSON body (for POST) or params dict (for GET)")
    sp.add_argument("--query", help="raw query string, GET only")
    sp.set_defaults(func=cmd_call)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help(sys.stderr)
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
