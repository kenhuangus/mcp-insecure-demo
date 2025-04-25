from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Initialize the MCP server
mcp = FastMCP("Vulnerable MCP Server")

# Database setup
DB_NAME = "vulnerable_mcp.db"

def setup_database():
    """Create the SQLite database and table if they don't exist."""
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

# Tool: Insert a record into the database (No input validation)
@mcp.tool()
def insert_record(name: str, address: str) -> str:
    """Insert a new record into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO records (name, address) VALUES ('{name}', '{address}')")  # SQL Injection vulnerability
    conn.commit()
    conn.close()
    return f"Record inserted: {name}, {address}"

# Tool: Query all records (Exposes sensitive data)
@mcp.tool()
def query_records() -> str:
    """Retrieve all records from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    conn.close()
    return "\n".join([f"ID: {row[0]}, Name: {row[1]}, Address: {row[2]}" for row in rows])

# Tool: Execute arbitrary SQL (No restrictions)
@mcp.tool()
def execute_sql(query: str) -> str:
    """Execute arbitrary SQL queries."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    result = cursor.execute(query).fetchall()  # Arbitrary code execution vulnerability
    conn.commit()
    conn.close()
    return str(result)

# Tool: Access environment variables (Exposes sensitive information)
@mcp.tool()
def get_env_variable(var_name: str) -> str:
    """Retrieve the value of an environment variable."""
    return os.getenv(var_name, "Variable not found")  # Exposes sensitive environment variables

if __name__ == "__main__":
    setup_database()
    mcp.run(transport='stdio')