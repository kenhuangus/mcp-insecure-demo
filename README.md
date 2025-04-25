# Insecure MCP SSE Demo

## Overview
This project demonstrates two types of vulnerable Model Context Protocol (MCP) servers:
- A pure STDIO-based MCP server for local CLI/agent integration.
- An SSE/HTTP-based MCP server using FastAPI, supporting both real-time Server-Sent Events and HTTP endpoints.

Both are designed for educational purposes to showcase security vulnerabilities in MCP server implementations.

## Project Structure
- `mcp-sse-vulnerable-server.py`: Main FastAPI SSE server exposing insecure tools and endpoints (HTTP + SSE).
- `vuln_server.py`: Minimal standalone FastAPI HTTP vulnerable server for 100% repeatable SQL injection and environment variable leak demos (no SSE, just HTTP POST).
- `vuln-mcp.py`: Pure STDIO-based MCP server for local CLI/agent integration and demonstration (no HTTP/SSE, uses stdin/stdout only).
- `mcp-sse-client-attack.py`: Automated attack client that demonstrates exploitation of server vulnerabilities via HTTP POST.
- `requirements.txt`: Python dependencies for the project.

## Features & Vulnerabilities
### Exposed Server Tools
1. **insert_record**
   - Inserts a name/address record into the database.
   - **Vulnerability:** Prone to SQL injection due to direct string interpolation of user input into SQL queries.
2. **query_records**
   - Lists all records in the database.
   - **Vulnerability:** Exposes all data without authentication or access control.
3. **execute_sql**
   - Executes arbitrary SQL queries provided by the client.
   - **Vulnerability:** Allows any SQL command, including destructive ones (e.g., data exfiltration, schema changes).
4. **get_env_variable**
   - Returns the value of any environment variable requested.
   - **Vulnerability:** Leaks sensitive environment variables (e.g., secrets, API keys).

## How to Run

git clone https://github.com/kenhuangus/mcp-insecure-demo

### 1. Install Dependencies
Install the required Python packages:
```bash
pip install fastapi uvicorn requests
```
Or, if you have a requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Start the Server
You can run one of three demo servers, depending on your use case:

**Option A: Full SSE MCP server (HTTP + SSE endpoints):**
```bash
python -m uvicorn mcp-sse-vulnerable-server:app --reload --host 127.0.0.1 --port 8000
```
- Exposes both HTTP and SSE endpoints for MCP events and all vulnerable tools.

**Option B: Minimal HTTP attack demo server (no SSE, just HTTP POST):**
```bash
python -m uvicorn vuln_server:app --reload --host 127.0.0.1 --port 8000
```
- Exposes only the `/attack` HTTP endpoint for repeatable SQL injection and env leak demos.

**Option C: STDIO-based MCP server (for local CLI/agent integration):**
```bash
python vuln-mcp.py
```
- Runs the MCP server over stdin/stdout (no HTTP, no SSE). Useful for direct integration with CLI tools, agents, or local automation.

#### Summary Table
| Server File                  | Protocol(s)    | Endpoints/Interface          | Use Case                                 |
|------------------------------|----------------|------------------------------|------------------------------------------|
| mcp-sse-vulnerable-server.py | HTTP + SSE     | /sse, /attack, etc.          | Full demo with real-time events          |
| vuln_server.py               | HTTP           | /attack                      | Minimal, always-repeatable attack demo   |
| vuln-mcp.py                  | STDIO          | stdin/stdout (no HTTP/SSE)   | Local CLI/agent integration, pure MCP    |

### 3. Run the Attack Client
In another terminal:
```bash
python mcp-sse-client-attack.py
```
This will automatically:
- Attempt SQL injection attacks (with 100% repeatable success)
- Attempt to read environment variables (e.g., `SECRET_KEY`)
- Print a summary of attack success rates

## Example Output

```
[CLIENT][ATTACK] Attempt 1 - SQL Injection
[CLIENT][POST] SQLi attack response: 200 {"sqli":"success","error":"no such table: records"}
[CLIENT][SUCCESS] SQLi attack succeeded!
...
[CLIENT] Attack success rate: 100.0%
[CLIENT][INFO] 100% attack success rate achieved.
```

## Notes
- The attack client and vulnerable server are for educational/demo purposes only. **Do not deploy in production!**
- You can modify the attack payloads or server logic to demonstrate other vulnerabilities.
- Attack client will show which payloads succeed or fail, and print out database contents and environment variable values if accessible.

## Vulnerabilities Demonstrated
- **SQL Injection:** User input is unsanitized, allowing attackers to manipulate SQL logic and insert arbitrary data.
- **Arbitrary Code Execution:** The `execute_sql` tool allows attackers to run any SQL command, including data theft or destruction.
- **Sensitive Data Exposure:** The `get_env_variable` tool allows attackers to read secrets and configuration values.
- **Lack of Access Control:** Anyone can run all tools and access all data without authentication.

## Mitigation Strategies
To secure a real-world MCP server, you should:

1. **Use Parameterized Queries:**
   - Always use parameter substitution instead of string interpolation for SQL queries to prevent injection.
   - Example (secure):
     ```python
     cursor.execute("INSERT INTO records (name, address) VALUES (?, ?)", (name, address))
     ```
2. **Restrict Dangerous Tools:**
   - Remove or strictly limit tools like `execute_sql` and `get_env_variable`.
   - Only expose necessary functionality.
3. **Implement Authentication & Authorization:**
   - Require users to authenticate and check permissions before allowing access to sensitive tools or data.
4. **Validate and Sanitize Input:**
   - Check and sanitize all user inputs, especially those that interact with the database or system.
5. **Limit Environment Variable Access:**
   - Only allow access to non-sensitive variables, or remove this tool entirely.
6. **Audit and Monitor Usage:**
   - Log all tool invocations and monitor for suspicious or abusive behavior.
7. **Principle of Least Privilege:**
   - Run the server with minimal privileges and restrict database and OS access as much as possible.

## Disclaimer
This project is for educational and demonstration purposes only. **Do not deploy this code in production environments.**

---

For questions or further improvements, please open an issue or contact the project maintainer.
