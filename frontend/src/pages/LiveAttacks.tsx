import { useState, useEffect } from 'react';
import { 
  Play, 
  Square, 
  Activity, 
  Server, 
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Zap
} from 'lucide-react';
import { ApiService } from '@/services/api';
import { LiveAttackSession, ServerStatus } from '@/types';

export function LiveAttacks() {
  const [sessions, setSessions] = useState<LiveAttackSession[]>([]);
  const [serverStatus, setServerStatus] = useState<ServerStatus[]>([]);
  const [selectedServer, setSelectedServer] = useState<string>('');
  const [selectedAttackType, setSelectedAttackType] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [currentSession, setCurrentSession] = useState<LiveAttackSession | null>(null);

  useEffect(() => {
    fetchServerStatus();
    const interval = setInterval(fetchServerStatus, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (currentSession) {
      const interval = setInterval(() => {
        fetchSessionStatus(currentSession.id);
      }, 2000); // Update session every 2 seconds
      return () => clearInterval(interval);
    }
  }, [currentSession]);

  const fetchServerStatus = async () => {
    try {
      const status = await ApiService.getServerStatus();
      setServerStatus(status);
    } catch (error) {
      console.error('Failed to fetch server status:', error);
    }
  };

  const fetchSessionStatus = async (sessionId: string) => {
    try {
      const session = await ApiService.getLiveAttackSession(sessionId);
      setCurrentSession(session);
      setSessions(prev => prev.map(s => s.id === sessionId ? session : s));
    } catch (error) {
      console.error('Failed to fetch session status:', error);
    }
  };

  const startAttack = async () => {
    if (!selectedServer) {
      alert('Please select a server');
      return;
    }

    setIsRunning(true);
    try {
      const session = await ApiService.runAttack(selectedServer, selectedAttackType);
      setCurrentSession(session);
      setSessions(prev => [session, ...prev]);
    } catch (error) {
      console.error('Failed to start attack:', error);
      alert('Failed to start attack. Please try again.');
    } finally {
      setIsRunning(false);
    }
  };

  const stopAttack = async () => {
    if (!currentSession) return;

    try {
      // In a real implementation, you would call an API to stop the attack
      setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null);
    } catch (error) {
      console.error('Failed to stop attack:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-primary-600 bg-primary-100';
      case 'completed': return 'text-success-600 bg-success-100';
      case 'failed': return 'text-danger-600 bg-danger-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Activity className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'failed': return <XCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const runningServers = serverStatus.filter(s => s.status === 'running');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Attacks</h1>
          <p className="text-gray-600">Monitor and control real-time vulnerability testing</p>
        </div>
        <div className="flex items-center space-x-3">
          {currentSession && currentSession.status === 'running' ? (
            <button
              onClick={stopAttack}
              className="btn-danger flex items-center"
            >
              <Square className="h-4 w-4 mr-2" />
              Stop Attack
            </button>
          ) : (
            <button
              onClick={startAttack}
              disabled={isRunning || runningServers.length === 0}
              className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="h-4 w-4 mr-2" />
              {isRunning ? 'Starting...' : 'Start Attack'}
            </button>
          )}
        </div>
      </div>

      {/* Server Selection */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Attack Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Server
            </label>
            <select
              value={selectedServer}
              onChange={(e) => setSelectedServer(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Select a server...</option>
              {runningServers.map((server) => (
                <option key={server.name} value={server.name}>
                  {server.name} ({server.type.toUpperCase()})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attack Type (Optional)
            </label>
            <select
              value={selectedAttackType}
              onChange={(e) => setSelectedAttackType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Attack Types</option>
              <option value="sql_injection">SQL Injection</option>
              <option value="file_access">File Access</option>
              <option value="command_execution">Command Execution</option>
              <option value="network_attacks">Network Attacks</option>
              <option value="crypto_weaknesses">Crypto Weaknesses</option>
              <option value="env_exposure">Environment Exposure</option>
            </select>
          </div>
        </div>
      </div>

      {/* Current Session */}
      {currentSession && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Current Attack Session</h3>
            <span className={`status-indicator ${getStatusColor(currentSession.status)}`}>
              {getStatusIcon(currentSession.status)}
              <span className="ml-1">{currentSession.status}</span>
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Session ID</label>
              <p className="text-sm text-gray-900">{currentSession.id}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Server Type</label>
              <p className="text-sm text-gray-900">{currentSession.serverType}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Start Time</label>
              <p className="text-sm text-gray-900">{new Date(currentSession.startTime).toLocaleTimeString()}</p>
            </div>
          </div>

          {currentSession.currentAttack && (
            <div className="mb-4">
              <label className="text-sm font-medium text-gray-500">Current Attack</label>
              <p className="text-sm text-gray-900">{currentSession.currentAttack}</p>
            </div>
          )}

          {/* Live Results */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Live Results</h4>
            <div className="max-h-64 overflow-y-auto space-y-2">
              {currentSession.results.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center">
                    <Target className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-900">{result.attackType}</span>
                  </div>
                  <div className="flex items-center">
                    {result.success ? (
                      <CheckCircle className="h-4 w-4 text-success-600 mr-1" />
                    ) : (
                      <XCircle className="h-4 w-4 text-danger-600 mr-1" />
                    )}
                    <span className="text-xs text-gray-500">
                      {new Date(result.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Server Status */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Server Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {serverStatus.map((server) => (
            <div key={server.name} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  <Server className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm font-medium text-gray-900">{server.name}</span>
                </div>
                <span className={`status-indicator ${getStatusColor(server.status)}`}>
                  {getStatusIcon(server.status)}
                  <span className="ml-1">{server.status}</span>
                </span>
              </div>
              <div className="text-xs text-gray-500">
                <p>Type: {server.type.toUpperCase()}</p>
                {server.port && <p>Port: {server.port}</p>}
                {server.pid && <p>PID: {server.pid}</p>}
                {server.lastActivity && (
                  <p>Last Activity: {new Date(server.lastActivity).toLocaleTimeString()}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Attack History */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Attack History</h3>
        {sessions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Session ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Server Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Start Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Results
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {session.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {session.serverType}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`status-indicator ${getStatusColor(session.status)}`}>
                        {getStatusIcon(session.status)}
                        <span className="ml-1">{session.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(session.startTime).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {session.results.length} attacks
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No attack sessions yet</p>
            <p className="text-sm text-gray-400">Start an attack to see live results here</p>
          </div>
        )}
      </div>
    </div>
  );
}
