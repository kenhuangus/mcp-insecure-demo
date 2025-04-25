import os
import sqlite3
import sys
import asyncio
# Windows event loop fix for asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from app_sse import create_sse_server

# Database setup
DB_NAME = "vulnerable_mcp_sse.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

app = FastAPI()
mcp = FastMCP("Vulnerable SSE MCP Server")

print('[SERVER] Module loaded')

from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/attack")
async def attack_endpoint(request: Request):
    data = await request.json()
    attack_type = data.get("attack_type")
    result = ""
    # Always drop and recreate the table for repeatable SQLi
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS records")
        cursor.execute("CREATE TABLE records (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT)")
        conn.commit()
    except Exception as e:
        return JSONResponse({"error": f"Table recreate error: {e}"}, status_code=500)
    conn.close()
    if attack_type == "sqli":
        # SQL Injection attack
        payload = data.get("payload", {
            "name": "attacker', '123 exploit st'); DROP TABLE records;--",
            "address": "hacked"
        })
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO records (name, address) VALUES ('{payload['name']}', '{payload['address']}')")
            conn.commit()
            # Try to query the table after attack
            try:
                cursor.execute("SELECT * FROM records")
                rows = cursor.fetchall()
                result = {
                    "sqli": "failed",
                    "rows": rows
                }
            except Exception as e:
                result = {
                    "sqli": "success",
                    "error": str(e)
                }
            conn.close()
        except Exception as e:
            result = {
                "sqli": "success",
                "error": str(e)
            }
        return JSONResponse(result)
    elif attack_type == "env":
        var_name = data.get("var_name", "SECRET_KEY")
        value = os.environ.get(var_name, "Not found")
        return JSONResponse({"env_var": var_name, "value": value})
    else:
        return JSONResponse({"error": "Unknown attack_type"}, status_code=400)
# Minimal SSE test endpoint
from sse_starlette.sse import EventSourceResponse
import asyncio
from fastapi.responses import StreamingResponse

@app.get("/ping")
def ping():
    print('[SERVER] /ping endpoint called')
    return {"pong": True}

@app.get("/sse-test/")
async def sse_test():
    print('[SERVER] /sse-test/ endpoint entered')
    async def event_gen():
        i = 0
        while True:
            await asyncio.sleep(1)
            i += 1
            import json
            # Emit a relevant MCP-style event as JSON
            message = {"mcp_event": "update", "count": i}
            yield f"data: {json.dumps(message)}\n\n"
            print(f'[SERVER] /sse-test/ yielding message {i}')
            # Optionally, emit a plain string message for demonstration (commented out to avoid parse errors)
            # yield f"data: test message {i}\n\n"
            # i += 1
    return EventSourceResponse(event_gen())

@app.get("/sse-test2/")
async def sse_test2():
    print('[SERVER] /sse-test2/ endpoint entered')
    async def event_gen():
        print('[SERVER] /sse-test2/ generator created')
        i = 0
        while True:
            await asyncio.sleep(1)
            msg = f"data: starlette test message {i}\n\n"
            print(f'[SERVER] /sse-test2/ yielding: {msg.strip()}')
            yield msg.encode()
            i += 1
    return StreamingResponse(event_gen(), media_type='text/event-stream')

# Mount the Starlette SSE server onto the FastAPI app
app.mount("/sse", create_sse_server(mcp))

@app.on_event("startup")
def on_startup():
    setup_database()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Tool: Insert a record into the database (No input validation)
@mcp.tool()
def insert_record(name: str, address: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO records (name, address) VALUES ('{name}', '{address}')")  # SQL Injection vulnerability
        conn.commit()
        result = f"Record inserted: {name}, {address}"
    except Exception as e:
        result = f"SQL ERROR: {e}"
    conn.close()
    return result

# Tool: Query all records (Exposes sensitive data)
@mcp.tool()
def query_records() -> str:
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records")
        rows = cursor.fetchall()
        conn.close()
        return "\n".join([f"ID: {row[0]}, Name: {row[1]}, Address: {row[2]}" for row in rows])
    except Exception as e:
        return f"SQL ERROR: {e}"

# Tool: Execute arbitrary SQL (No restrictions)
@mcp.tool()
def execute_sql(query: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    result = cursor.execute(query).fetchall()  # Arbitrary code execution vulnerability
    conn.commit()
    conn.close()
    return str(result)

# Tool: Access environment variables (Exposes sensitive information)
@mcp.tool()
def get_env_variable(var_name: str) -> str:
    return os.environ.get(var_name, "Not found")
