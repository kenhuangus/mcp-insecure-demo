#!/usr/bin/env python3
"""
Backend API server for MCP Vulnerability Dashboard
Provides REST API endpoints for the TypeScript frontend
"""

import os
import json
import glob
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="MCP Vulnerability Dashboard API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend build)
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# Data models
class AttackReport(BaseModel):
    id: str
    timestamp: str
    platform: str
    overallSuccessRate: float
    totalSuccess: int
    totalTests: int
    metrics: Dict[str, Dict[str, int]]
    individualResults: List[Dict[str, Any]]

class ServerStatus(BaseModel):
    name: str
    type: str
    status: str
    port: Optional[int] = None
    pid: Optional[int] = None
    lastActivity: Optional[str] = None

class LiveAttackSession(BaseModel):
    id: str
    serverType: str
    startTime: str
    status: str
    currentAttack: Optional[str] = None
    results: List[Dict[str, Any]]
    metrics: Dict[str, Dict[str, int]]

# Global state
active_sessions: Dict[str, LiveAttackSession] = {}
server_processes: Dict[str, subprocess.Popen] = {}

def parse_attack_result_file(filepath: str) -> AttackReport:
    """Parse an attack result file and return structured data"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract timestamp from filename
        filename = os.path.basename(filepath)
        timestamp_match = None
        if '_' in filename:
            parts = filename.split('_')
            if len(parts) >= 3:
                date_part = parts[-2]
                time_part = parts[-1].replace('.txt', '')
                if len(date_part) == 8 and len(time_part) == 6:
                    timestamp = f"20{date_part[:2]}-{date_part[2:4]}-{date_part[4:6]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                else:
                    timestamp = datetime.now().isoformat()
            else:
                timestamp = datetime.now().isoformat()
        else:
            timestamp = datetime.now().isoformat()
        
        # Parse content based on file type
        if 'comprehensive' in filename or 'COMPREHENSIVE ATTACK REPORT' in content:
            return parse_comprehensive_report(content, filename, timestamp)
        elif 'sse' in filename:
            return parse_sse_report(content, filename, timestamp)
        else:
            return parse_basic_report(content, filename, timestamp)
    
    except Exception as e:
        print(f"Error parsing file {filepath}: {e}")
        return create_empty_report(filename, timestamp)

def parse_comprehensive_report(content: str, filename: str, timestamp: str) -> AttackReport:
    """Parse comprehensive attack report"""
    lines = content.split('\n')
    
    # Extract platform
    platform = 'unknown'
    platform_match = None
    for line in lines:
        if 'COMPREHENSIVE ATTACK REPORT -' in line:
            platform = line.split('COMPREHENSIVE ATTACK REPORT - ')[1].strip().lower()
            break
    
    # Extract overall success rate
    total_success = 0
    total_tests = 0
    overall_success_rate = 0.0
    
    for line in lines:
        if 'Overall Success Rate:' in line:
            import re
            match = re.search(r'(\d+)/(\d+)\s*\(([\d.]+)%\)', line)
            if match:
                total_success = int(match.group(1))
                total_tests = int(match.group(2))
                overall_success_rate = float(match.group(3))
            break
    
    # Parse individual metrics
    metrics = {
        'sqlInjection': {'success': 0, 'total': 0},
        'fileAccess': {'success': 0, 'total': 0},
        'commandExecution': {'success': 0, 'total': 0},
        'networkAttacks': {'success': 0, 'total': 0},
        'cryptoWeaknesses': {'success': 0, 'total': 0},
        'envExposure': {'success': 0, 'total': 0}
    }
    
    metric_patterns = {
        'sqlInjection': r'SQL Injection:\s*(\d+)/(\d+)',
        'fileAccess': r'File Access:\s*(\d+)/(\d+)',
        'commandExecution': r'Command Execution:\s*(\d+)/(\d+)',
        'networkAttacks': r'Network Attacks:\s*(\d+)/(\d+)',
        'cryptoWeaknesses': r'Crypto Weaknesses:\s*(\d+)/(\d+)',
        'envExposure': r'Env Exposure:\s*(\d+)/(\d+)'
    }
    
    for line in lines:
        for metric, pattern in metric_patterns.items():
            import re
            match = re.search(pattern, line)
            if match:
                metrics[metric] = {
                    'success': int(match.group(1)),
                    'total': int(match.group(2))
                }
    
    return AttackReport(
        id=f"report_{int(datetime.now().timestamp())}",
        timestamp=timestamp,
        platform=platform,
        overallSuccessRate=overall_success_rate,
        totalSuccess=total_success,
        totalTests=total_tests,
        metrics=metrics,
        individualResults=[]
    )

def parse_sse_report(content: str, filename: str, timestamp: str) -> AttackReport:
    """Parse SSE attack report"""
    lines = content.split('\n')
    
    sql_success = 0
    sql_total = 0
    env_success = 0
    env_total = 0
    
    for line in lines:
        if '[CLIENT][SUCCESS] SQLi attack succeeded!' in line:
            sql_success += 1
        if '[CLIENT][ATTACK]' in line and 'SQL Injection' in line:
            sql_total += 1
        if '[CLIENT][ATTACK]' in line and 'Env Leak' in line:
            env_total += 1
        if '"value":"Not found"' in line and 'env_var' in line:
            env_success += 1
    
    # Parse final success rate
    total_success = 0
    total_tests = 0
    overall_success_rate = 0.0
    
    for line in lines:
        if 'Attack success rate:' in line:
            import re
            match = re.search(r'(\d+)/(\d+)\s*\(([\d.]+)%\)', line)
            if match:
                total_success = int(match.group(1))
                total_tests = int(match.group(2))
                overall_success_rate = float(match.group(3))
            break
    
    if total_success == 0:
        total_success = sql_success + env_success
        total_tests = sql_total + env_total
        overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    metrics = {
        'sqlInjection': {'success': sql_success, 'total': sql_total},
        'fileAccess': {'success': 0, 'total': 0},
        'commandExecution': {'success': 0, 'total': 0},
        'networkAttacks': {'success': 0, 'total': 0},
        'cryptoWeaknesses': {'success': 0, 'total': 0},
        'envExposure': {'success': env_success, 'total': env_total}
    }
    
    return AttackReport(
        id=f"sse_report_{int(datetime.now().timestamp())}",
        timestamp=timestamp,
        platform='unknown',
        overallSuccessRate=overall_success_rate,
        totalSuccess=total_success,
        totalTests=total_tests,
        metrics=metrics,
        individualResults=[]
    )

def parse_basic_report(content: str, filename: str, timestamp: str) -> AttackReport:
    """Parse basic attack report"""
    lines = content.split('\n')
    
    metrics = {
        'sqlInjection': {'success': 0, 'total': 0},
        'fileAccess': {'success': 0, 'total': 0},
        'commandExecution': {'success': 0, 'total': 0},
        'networkAttacks': {'success': 0, 'total': 0},
        'cryptoWeaknesses': {'success': 0, 'total': 0},
        'envExposure': {'success': 0, 'total': 0}
    }
    
    # Parse success rates
    for line in lines:
        if 'SQL Injection:' in line:
            import re
            match = re.search(r'(\d+)/(\d+)', line)
            if match:
                metrics['sqlInjection'] = {'success': int(match.group(1)), 'total': int(match.group(2))}
        elif 'Arbitrary SQL:' in line:
            import re
            match = re.search(r'(\d+)/(\d+)', line)
            if match:
                metrics['sqlInjection']['total'] += int(match.group(2))
                metrics['sqlInjection']['success'] += int(match.group(1))
        elif 'Env Leak:' in line:
            import re
            match = re.search(r'(\d+)/(\d+)', line)
            if match:
                metrics['envExposure'] = {'success': int(match.group(1)), 'total': int(match.group(2))}
    
    total_success = sum(m['success'] for m in metrics.values())
    total_tests = sum(m['total'] for m in metrics.values())
    overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    return AttackReport(
        id=f"basic_report_{int(datetime.now().timestamp())}",
        timestamp=timestamp,
        platform='unknown',
        overallSuccessRate=overall_success_rate,
        totalSuccess=total_success,
        totalTests=total_tests,
        metrics=metrics,
        individualResults=[]
    )

def create_empty_report(filename: str, timestamp: str) -> AttackReport:
    """Create an empty report for failed parsing"""
    return AttackReport(
        id=f"empty_report_{int(datetime.now().timestamp())}",
        timestamp=timestamp,
        platform='unknown',
        overallSuccessRate=0.0,
        totalSuccess=0,
        totalTests=0,
        metrics={
            'sqlInjection': {'success': 0, 'total': 0},
            'fileAccess': {'success': 0, 'total': 0},
            'commandExecution': {'success': 0, 'total': 0},
            'networkAttacks': {'success': 0, 'total': 0},
            'cryptoWeaknesses': {'success': 0, 'total': 0},
            'envExposure': {'success': 0, 'total': 0}
        },
        individualResults=[]
    )

# API Endpoints
@app.get("/")
async def root():
    """Serve the frontend"""
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return {"message": "MCP Vulnerability Dashboard API", "status": "running"}

@app.get("/vite.svg")
async def favicon():
    """Serve the favicon"""
    if os.path.exists("frontend/dist/vite.svg"):
        return FileResponse("frontend/dist/vite.svg")
    return {"error": "Favicon not found"}

@app.get("/api/reports", response_model=List[AttackReport])
async def get_attack_reports():
    """Get all attack reports from results directory"""
    reports = []
    results_dir = Path("results")
    
    if results_dir.exists():
        for filepath in results_dir.glob("*.txt"):
            try:
                report = parse_attack_result_file(str(filepath))
                reports.append(report)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    # Sort by timestamp (newest first)
    reports.sort(key=lambda x: x.timestamp, reverse=True)
    return reports

@app.post("/api/reports/upload", response_model=AttackReport)
async def upload_result_file(file: UploadFile = File(...)):
    """Upload and parse a result file"""
    try:
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        filepath = upload_dir / file.filename
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse the file
        report = parse_attack_result_file(str(filepath))
        
        # Move to results directory
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        final_path = results_dir / file.filename
        filepath.rename(final_path)
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@app.get("/api/servers/status", response_model=List[ServerStatus])
async def get_server_status():
    """Get status of all configured servers"""
    status_list = []
    
    # Check STDIO servers
    stdio_servers = [
        ("STDIO Server", "vuln-mcp.py"),
        ("Enhanced STDIO Server", "enhanced-vuln-mcp.py")
    ]
    
    for name, script in stdio_servers:
        if os.path.exists(script):
            # Check if process is running (simplified check)
            status = "stopped"
            pid = None
            try:
                result = subprocess.run(["pgrep", "-f", script], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    status = "running"
                    pid = int(result.stdout.strip().split('\n')[0])
            except:
                pass
            
            status_list.append(ServerStatus(
                name=name,
                type="stdio",
                status=status,
                pid=pid,
                lastActivity=datetime.now().isoformat() if status == "running" else None
            ))
    
    # Check SSE server
    sse_script = "mcp-sse-vulnerable-server.py"
    if os.path.exists(sse_script):
        status = "stopped"
        pid = None
        try:
            result = subprocess.run(["pgrep", "-f", sse_script], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                status = "running"
                pid = int(result.stdout.strip().split('\n')[0])
        except:
            pass
        
        status_list.append(ServerStatus(
            name="SSE Server",
            type="sse",
            status=status,
            port=9000,
            pid=pid,
            lastActivity=datetime.now().isoformat() if status == "running" else None
        ))
    
    return status_list

@app.post("/api/servers/start")
async def start_server(serverType: str):
    """Start a server"""
    try:
        script_map = {
            "STDIO Server": "vuln-mcp.py",
            "Enhanced STDIO Server": "enhanced-vuln-mcp.py",
            "SSE Server": "mcp-sse-vulnerable-server.py"
        }
        
        script = script_map.get(serverType)
        if not script or not os.path.exists(script):
            raise HTTPException(status_code=404, detail="Server script not found")
        
        # Start server in background
        process = subprocess.Popen(
            ["python3", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        server_processes[serverType] = process
        return {"status": "started", "pid": process.pid}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start server: {str(e)}")

@app.post("/api/servers/stop")
async def stop_server(serverType: str):
    """Stop a server"""
    try:
        if serverType in server_processes:
            process = server_processes[serverType]
            process.terminate()
            del server_processes[serverType]
            return {"status": "stopped"}
        else:
            # Try to find and kill by script name
            script_map = {
                "STDIO Server": "vuln-mcp.py",
                "Enhanced STDIO Server": "enhanced-vuln-mcp.py",
                "SSE Server": "mcp-sse-vulnerable-server.py"
            }
            
            script = script_map.get(serverType)
            if script:
                subprocess.run(["pkill", "-f", script])
            
            return {"status": "stopped"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop server: {str(e)}")

@app.post("/api/attacks/run", response_model=LiveAttackSession)
async def run_attack(serverType: str, attackType: Optional[str] = None):
    """Start a live attack session"""
    session_id = f"session_{int(datetime.now().timestamp())}"
    
    session = LiveAttackSession(
        id=session_id,
        serverType=serverType,
        startTime=datetime.now().isoformat(),
        status="running",
        currentAttack=attackType,
        results=[],
        metrics={
            'sqlInjection': {'success': 0, 'total': 0},
            'fileAccess': {'success': 0, 'total': 0},
            'commandExecution': {'success': 0, 'total': 0},
            'networkAttacks': {'success': 0, 'total': 0},
            'cryptoWeaknesses': {'success': 0, 'total': 0},
            'envExposure': {'success': 0, 'total': 0}
        }
    )
    
    active_sessions[session_id] = session
    
    # In a real implementation, you would start the actual attack here
    # For now, we'll simulate it
    
    return session

@app.get("/api/attacks/session/{session_id}", response_model=LiveAttackSession)
async def get_live_attack_session(session_id: str):
    """Get live attack session status"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]

if __name__ == "__main__":
    # Create necessary directories
    Path("results").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    
    print("Starting MCP Vulnerability Dashboard API...")
    print("Frontend will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
