# MCP Insecure Demo Project

## Overview
This project demonstrates common vulnerabilities in Model Context Protocol (MCP) server-client architectures, focusing on SQL injection, environment variable exposure, and arbitrary code execution. It is designed for educational and security research purposes, showing how insecure design and implementation can be exploited by attackers.

**There are two main types of vulnerable server implementations included:**
- `vuln-mcp.py`: STDIO transport based vulnerable MCP server.
- `mcp-sse-vulnerable-server.py`: SSE transport based vulnerable MCP server with Server-Sent Events (SSE) support.

Attack clients are provided to automate and report on exploitation attempts against both server types.

---

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <YOUR_REPO_URL>
cd mcp-insecure-demo
```

### 2. Create and Activate a Virtual Environment
**Windows:**
```sh
python -m venv venv
venv\Scripts\activate
```
**macOS/Linux:**
```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

---

## Running the Vulnerable Servers

### Classic MCP Server
```sh
python vuln-mcp.py
```

### SSE Vulnerable MCP Server
```sh
python mcp-sse-vulnerable-server.py
```

Both servers will start on their respective default ports (see code for details).

---

## Running Attack Clients

### Classic MCP Attack Client
```sh
python attack-mcp-client.py vuln-mcp.py
```

### SSE Attack Client
```sh
python mcp-sse-client-attack.py
```

Each client will attempt a series of attacks (SQL injection, environment variable exposure, etc.) and report the success rate. For the SSE server, the attack client will also attempt to exploit SSE endpoints if present.

---

## What This Demo Is For
- **Education**: Learn how insecure coding practices lead to real-world vulnerabilities.
- **Testing**: Safely test and visualize exploitation techniques in a controlled environment.
- **Awareness**: Understand the importance of input validation, secure coding, and proper environment management.

**Warning:** This project is intentionally insecure. Do NOT deploy it in production or on any system with sensitive data.

---

## Additional Notes
- You may edit or extend the attack payloads in the client scripts to test new exploit scenarios.
- If you modify server code, restart the server before running new tests.
- To avoid port conflicts, ensure only one server is running per port at a time.
- For questions or contributions, open an issue or pull request on the project repository.
