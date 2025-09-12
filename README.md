# MCP Vulnerability Demonstration System

A comprehensive educational platform for demonstrating vulnerabilities in Model Context Protocol (MCP) server-client architectures, featuring both command-line tools and a modern TypeScript web dashboard.

## 🎯 Overview

This project demonstrates various vulnerabilities in MCP implementations, including SQL injection, environment variable exposure, arbitrary code execution, and cross-platform attack vectors. It's designed for educational and security research purposes, showing how insecure design and implementation can be exploited by attackers.

### Key Features

- **🔧 Multiple Vulnerable Servers**: STDIO and SSE transport-based servers with intentional vulnerabilities
- **🎨 Modern Web Dashboard**: Interactive TypeScript frontend with real-time visualization
- **🌍 Cross-Platform Support**: Optimized for macOS, Linux, and Windows systems
- **📊 Comprehensive Reporting**: Detailed vulnerability analysis and metrics
- **⚡ Live Attack Monitoring**: Real-time attack session monitoring and control
- **🎓 Educational Focus**: Clear visualization of security concepts and best practices

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**: For MCP servers and backend API
- **Node.js 16+**: For TypeScript frontend (optional)
- **macOS/Linux/Windows**: Cross-platform compatibility

### 1. Setup
```bash
# Clone the repository
git clone <repository-url>
cd mcp-insecure-demo

# Setup MCP servers and Python environment
./setup-macos.sh  # or setup script for your platform

# Setup frontend (optional)
./setup-frontend.sh
```

### 2. Start the System
```bash
# Start everything (servers + dashboard)
./start-dashboard.sh

# Or start just the servers
./start-servers.sh
```

### 3. Access the Dashboard
- **Web Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Command-line Tools**: Use the attack clients directly

## 🏗️ Architecture

### Core Components

#### Vulnerable MCP Servers
- **`vuln-mcp.py`**: Basic STDIO transport vulnerable server
- **`enhanced-vuln-mcp.py`**: Enhanced server with comprehensive vulnerability tools
- **`mcp-sse-vulnerable-server.py`**: SSE transport vulnerable server with FastAPI

#### Attack Clients
- **`attack-mcp-client.py`**: Basic attack client for STDIO servers
- **`comprehensive-attack-client.py`**: Advanced client with platform-specific attacks
- **`mcp-sse-client-attack.py`**: SSE-specific attack client
- **`good-mcp-client.py`**: Legitimate client for comparison

#### Web Dashboard
- **TypeScript Frontend**: Modern React application with real-time visualization
- **FastAPI Backend**: RESTful API server with automatic documentation
- **Interactive Charts**: Real-time vulnerability metrics and trends

## 📊 Web Dashboard Features

### 🎨 Frontend Stack
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development with comprehensive interfaces
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Recharts**: Interactive charts and data visualization
- **React Router**: Client-side routing
- **Lucide React**: Beautiful, customizable icons

### 📊 Dashboard Page
- **Real-time Metrics**: Live vulnerability success rates and statistics
- **Interactive Charts**: Bar charts, pie charts, and timeline graphs
- **Server Status**: Real-time monitoring of MCP server health
- **Recent Reports**: Quick overview of latest attack results
- **Platform Detection**: Automatic detection and display of target platform information

### 📈 Reports Page
- **Report Management**: View, filter, and search attack reports
- **File Upload**: Drag-and-drop interface for uploading result files
- **Advanced Filtering**: Filter by platform, date range, and attack type
- **Export Functionality**: Download reports in JSON format
- **Detailed Analysis**: Comprehensive breakdown of vulnerability metrics

### ⚡ Live Attacks Page
- **Real-time Monitoring**: Monitor live attack sessions as they execute
- **Server Control**: Start and stop MCP servers from the web interface
- **Attack Configuration**: Select target servers and specific attack types
- **Session History**: Track and analyze historical attack sessions
- **Live Updates**: Real-time progress tracking and result display

### ⚙️ Settings Page
- **Dashboard Configuration**: Customize themes, refresh intervals, and display options
- **Server Management**: Configure and manage multiple MCP server instances
- **Security Notices**: Built-in educational warnings and best practices
- **Performance Tuning**: Configure caching and auto-refresh settings

## 🔧 Command-Line Usage

### Running Attack Clients

#### Basic STDIO Attack
```bash
python3 attack-mcp-client.py vuln-mcp.py > results/basic-attack.txt
```

#### Comprehensive Attack (Platform-Adaptive)
```bash
python3 comprehensive-attack-client.py enhanced-vuln-mcp.py > results/comprehensive-attack.txt
```

#### SSE Attack
```bash
python3 mcp-sse-client-attack.py > results/sse-attack.txt
```

#### Automated Attack Suite
```bash
./run-attacks.sh
```

### Server Management

#### Start Individual Servers
```bash
# STDIO Server
python3 vuln-mcp.py &

# Enhanced STDIO Server
python3 enhanced-vuln-mcp.py &

# SSE Server
python3 mcp-sse-vulnerable-server.py &
```

#### Start All Servers
```bash
./start-servers.sh
```

## 🎯 Demonstrated Vulnerabilities

### Database Vulnerabilities
- **SQL Injection**: Direct string interpolation in SQL queries
- **Arbitrary SQL Execution**: Unrestricted SQL command execution
- **Data Exposure**: Unrestricted access to database records

### File System Vulnerabilities
- **Path Traversal**: Access to sensitive system files
- **Arbitrary File Access**: Read/write access to any file
- **Directory Listing**: Unrestricted directory browsing

### Command Execution Vulnerabilities
- **System Commands**: Arbitrary system command execution
- **Process Management**: Process enumeration and control
- **Platform-specific Commands**: OS-specific command execution

### Network Vulnerabilities
- **SSRF**: Server-Side Request Forgery attacks
- **Port Scanning**: Network reconnaissance capabilities
- **Internal Service Discovery**: Access to internal services

### Environment Variable Exposure
- **Sensitive Variables**: Access to system and application environment variables
- **Platform-specific Variables**: OS-specific environment variable access
- **Configuration Exposure**: Application configuration disclosure

## 🌍 Platform-Specific Features

### macOS Optimizations
- **Keychain Access**: Attempts to access macOS keychain data
- **Homebrew Integration**: Targets Homebrew-specific paths and variables
- **System Profiling**: Uses macOS system profiling commands
- **LaunchDaemon Access**: Attempts to access system launch daemon configurations

### Cross-Platform Compatibility
- **Automatic Detection**: Detects target platform automatically
- **Adaptive Payloads**: Uses platform-appropriate attack vectors
- **Unified Interface**: Consistent experience across all platforms

## 📁 Project Structure

```
mcp-insecure-demo/
├── 🎨 Frontend (TypeScript React)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   └── Layout.tsx      # Main layout component
│   │   ├── pages/             # Dashboard pages
│   │   │   ├── Dashboard.tsx   # Main dashboard
│   │   │   ├── Reports.tsx     # Reports management
│   │   │   ├── LiveAttacks.tsx # Live monitoring
│   │   │   └── Settings.tsx    # Configuration
│   │   ├── services/          # API integration
│   │   │   ├── api.ts         # API client
│   │   │   └── resultParser.ts # Result parser
│   │   ├── types/             # TypeScript definitions
│   │   │   └── index.ts       # Type definitions
│   │   ├── App.tsx            # Main app component
│   │   ├── App.css            # Global styles
│   │   └── main.tsx           # App entry point
│   ├── package.json           # Dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── tailwind.config.js     # Styling config
│   └── vite.config.ts         # Build config
├── 🐍 Backend & Servers
│   ├── backend_api.py         # FastAPI server
│   ├── vuln-mcp.py           # Basic vulnerable server
│   ├── enhanced-vuln-mcp.py  # Enhanced vulnerable server
│   ├── mcp-sse-vulnerable-server.py # SSE vulnerable server
│   └── app_sse.py            # SSE utilities
├── 🎯 Attack Clients
│   ├── attack-mcp-client.py          # Basic attacks
│   ├── comprehensive-attack-client.py # Advanced attacks
│   ├── mcp-sse-client-attack.py      # SSE attacks
│   └── good-mcp-client.py           # Legitimate client
├── 🚀 Setup & Management Scripts
│   ├── setup-macos.sh        # macOS setup
│   ├── setup-frontend.sh     # Frontend setup
│   ├── start-dashboard.sh    # Start everything
│   ├── start-servers.sh      # Start servers only
│   ├── run-attacks.sh        # Run attack suite
│   └── stop-dashboard.sh     # Stop everything
├── 📚 Documentation
│   └── README.md             # Comprehensive guide
├── 📊 Data Directories
│   ├── results/              # Attack result files (.gitkeep)
│   ├── uploads/              # File upload directory (.gitkeep)
│   └── logs/                 # System logs (.gitkeep)
├── 🔧 Configuration
│   ├── requirements.txt      # Python dependencies
│   ├── .gitignore           # Version control ignore
│   └── venv/                # Virtual environment
└── 📄 Database Files
    ├── vulnerable_mcp.db     # SQLite database (ignored)
    └── vulnerable_mcp_sse.db # SSE database (ignored)
```

## 🔒 Security Considerations

### For Educational Use
- **Isolated Environment**: Run only in isolated, non-production environments
- **No Sensitive Data**: Ensure no sensitive data is present on the system
- **Network Isolation**: Consider running in a network-isolated environment

### For Development
- **Code Review**: Review all code before deployment
- **Input Validation**: Implement proper input validation
- **Access Controls**: Implement appropriate access controls
- **Monitoring**: Monitor for suspicious activities

## 🎓 Educational Use Cases

### Security Training
- **Penetration Testing**: Learn real-world attack techniques
- **Secure Coding**: Understand common vulnerability patterns
- **Defense Strategies**: Practice implementing security controls

### Research Applications
- **Vulnerability Assessment**: Test security tools and techniques
- **Attack Simulation**: Simulate real-world attack scenarios
- **Security Tool Development**: Test and validate security tools

## 🚀 Advanced Features

### Real-time Monitoring
- **Live Attack Sessions**: Monitor attacks as they execute
- **Server Health**: Real-time server status monitoring
- **Performance Metrics**: Track attack success rates and timing

### Data Visualization
- **Interactive Charts**: Dynamic charts that update with new data
- **Color-coded Metrics**: Visual indicators for vulnerability severity
- **Timeline Analysis**: Historical trend analysis with time-series data

### Automation
- **Automated Testing**: Run comprehensive attack suites
- **Scheduled Attacks**: Schedule attacks for regular testing
- **Report Generation**: Automated report generation and distribution

## 🔌 API Documentation

### Backend API Endpoints

#### Reports
- `GET /api/reports` - Get all attack reports
- `POST /api/reports/upload` - Upload and parse result file
- `GET /api/reports/{id}` - Get specific report details

#### Servers
- `GET /api/servers/status` - Get server status
- `POST /api/servers/start` - Start a server
- `POST /api/servers/stop` - Stop a server

#### Live Attacks
- `POST /api/attacks/run` - Start live attack session
- `GET /api/attacks/session/{id}` - Get session status
- `DELETE /api/attacks/session/{id}` - Stop attack session

### Data Models

#### AttackReport
```typescript
interface AttackReport {
  id: string;
  timestamp: string;
  platform: string;
  overallSuccessRate: number;
  totalSuccess: number;
  totalTests: number;
  metrics: VulnerabilityMetrics;
  individualResults: AttackResult[];
}
```

#### ServerStatus
```typescript
interface ServerStatus {
  name: string;
  type: 'stdio' | 'sse';
  status: 'running' | 'stopped' | 'error';
  port?: number;
  pid?: number;
  lastActivity?: string;
}
```

#### VulnerabilityMetrics
```typescript
interface VulnerabilityMetrics {
  sqlInjection: { success: number; total: number };
  fileAccess: { success: number; total: number };
  commandExecution: { success: number; total: number };
  networkAttacks: { success: number; total: number };
  cryptoWeaknesses: { success: number; total: number };
  envExposure: { success: number; total: number };
}
```

## 🐛 Troubleshooting

### Common Issues

#### Python Dependencies
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Frontend Build Issues
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Port Conflicts
```bash
# Check if ports are in use
lsof -i :8000  # Dashboard
lsof -i :9000  # SSE Server

# Kill existing processes
pkill -f "backend_api.py"
pkill -f "mcp-sse-vulnerable-server.py"
```

#### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh

# Check file permissions
ls -la *.sh
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

### Development Guidelines
- Follow security best practices
- Test on multiple platforms
- Add comprehensive documentation
- Include educational value

## 📄 License

This project is for educational purposes only. Use at your own risk.

## ⚠️ Security Warning

**This project is intentionally vulnerable software for educational purposes only.**

- Do NOT deploy in production environments
- Do NOT use on systems with sensitive data
- Run only in isolated, controlled environments
- Use for educational and research purposes only

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue with detailed information

**Remember: This is intentionally vulnerable software for educational purposes only!**