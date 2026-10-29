#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

# Only the latest attempt for each txn_id counts.
latest = {}  # txn_id -> (ts, event)

with open("payments.jsonl", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue  # unreadable line
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if not txn_id:
            continue  # event without a txn_id
        ts = event.get("ts") or ""
        prev = latest.get(txn_id)
        # ISO-8601 UTC timestamps sort chronologically as strings
        if prev is None or ts >= prev[0]:
            latest[txn_id] = (ts, event)


def to_amount(value):
    """Amounts are numbers, or strings like '4,804.15'."""
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return float(value)


total = 0.0
count = 0
for _, event in latest.values():
    if event.get("status") == "success":
        total += to_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
