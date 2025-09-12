from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import subprocess
import requests
import hashlib
import random
import string
import platform
import socket

# Initialize the MCP server
mcp = FastMCP("Enhanced Vulnerable MCP Server")

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
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    return "\n".join([f"ID: {row[0]}, Name: {row[1]}, Address: {row[2]}, Created: {row[3]}" for row in rows])

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

# Tool: Read arbitrary files (Path traversal vulnerability)
@mcp.tool()
def read_file(file_path: str) -> str:
    """Read contents of any file on the system."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Tool: Write to arbitrary files (File system vulnerability)
@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """Write content to any file on the system."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Content written to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

# Tool: Execute system commands (Command injection vulnerability)
@mcp.tool()
def execute_command(command: str) -> str:
    """Execute arbitrary system commands."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Output: {result.stdout}\nError: {result.stderr}\nReturn Code: {result.returncode}"
    except Exception as e:
        return f"Command execution error: {e}"

# Tool: Make HTTP requests (SSRF vulnerability)
@mcp.tool()
def make_request(url: str, method: str = "GET", data: str = "") -> str:
    """Make HTTP requests to any URL."""
    try:
        response = requests.request(method, url, data=data, timeout=10)
        return f"Status: {response.status_code}\nContent: {response.text[:500]}"
    except Exception as e:
        return f"Request error: {e}"

# Tool: Scan network ports (Network reconnaissance)
@mcp.tool()
def scan_port(host: str, port: int) -> str:
    """Scan a specific port on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return "Open" if result == 0 else "Closed"
    except Exception as e:
        return f"Scan error: {e}"

# Tool: Generate hashes with weak algorithms
@mcp.tool()
def generate_hash(data: str, algorithm: str = "md5") -> str:
    """Generate hash using specified algorithm (includes weak algorithms)."""
    try:
        hasher = getattr(hashlib, algorithm)()
        hasher.update(data.encode())
        return hasher.hexdigest()
    except Exception as e:
        return f"Hash error: {e}"

# Tool: Generate weak random tokens
@mcp.tool()
def generate_token(length: int = 8) -> str:
    """Generate a random token (uses weak random generation)."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# Tool: Get system information (Information disclosure)
@mcp.tool()
def get_system_info() -> str:
    """Get detailed system information."""
    info = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "current_user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
        "home_directory": os.getenv("HOME", os.getenv("USERPROFILE", "unknown")),
        "current_directory": os.getcwd()
    }
    return "\n".join([f"{k}: {v}" for k, v in info.items()])

# Tool: List directory contents (Directory traversal)
@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List contents of any directory."""
    try:
        files = os.listdir(path)
        return "\n".join(files)
    except Exception as e:
        return f"Directory listing error: {e}"

# Tool: Get process information (Process enumeration)
@mcp.tool()
def get_processes() -> str:
    """Get information about running processes."""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["tasklist"], capture_output=True, text=True)
        else:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        return result.stdout[:1000]  # Limit output
    except Exception as e:
        return f"Process listing error: {e}"

# Tool: Database connection with arbitrary connection strings
@mcp.tool()
def connect_database(connection_string: str, query: str) -> str:
    """Connect to database with arbitrary connection string."""
    try:
        conn = sqlite3.connect(connection_string)
        cursor = conn.cursor()
        result = cursor.execute(query).fetchall()
        conn.close()
        return str(result)
    except Exception as e:
        return f"Database connection error: {e}"

if __name__ == "__main__":
    setup_database()
    print(f"[SERVER] Starting Enhanced Vulnerable MCP Server on {platform.system()}")
    mcp.run(transport='stdio')



