import { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Activity,
  Server,
  Clock
} from 'lucide-react';
import { ApiService } from '@/services/api';
import { AttackReport, ServerStatus } from '@/types';

const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];

export function Dashboard() {
  const [reports, setReports] = useState<AttackReport[]>([]);
  const [serverStatus, setServerStatus] = useState<ServerStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [reportsData, statusData] = await Promise.all([
          ApiService.getAttackReports(),
          ApiService.getServerStatus()
        ]);
        setReports(reportsData);
        setServerStatus(statusData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const latestReport = reports[0];
  const totalVulnerabilities = reports.reduce((sum, report) => sum + report.totalSuccess, 0);
  const totalTests = reports.reduce((sum, report) => sum + report.totalTests, 0);
  const overallSuccessRate = totalTests > 0 ? (totalVulnerabilities / totalTests) * 100 : 0;

  const chartData = latestReport ? Object.entries(latestReport.metrics).map(([key, value]) => ({
    name: key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
    success: value.success,
    total: value.total,
    rate: value.total > 0 ? (value.success / value.total) * 100 : 0
  })) : [];

  const pieData = chartData.map((item, index) => ({
    name: item.name,
    value: item.success,
    color: COLORS[index % COLORS.length]
  }));

  const timelineData = reports.slice(0, 10).map(report => ({
    timestamp: new Date(report.timestamp).toLocaleTimeString(),
    successRate: report.overallSuccessRate
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Security Dashboard</h1>
          <p className="text-gray-600">MCP Vulnerability Assessment Overview</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="h-4 w-4 mr-1" />
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="metric-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Shield className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Overall Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{overallSuccessRate.toFixed(1)}%</p>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-danger-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Vulnerabilities</p>
              <p className="text-2xl font-bold text-gray-900">{totalVulnerabilities}</p>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Activity className="h-8 w-8 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Tests</p>
              <p className="text-2xl font-bold text-gray-900">{totalTests}</p>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Server className="h-8 w-8 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Servers</p>
              <p className="text-2xl font-bold text-gray-900">
                {serverStatus.filter(s => s.status === 'running').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vulnerability Types Chart */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Vulnerability Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="success" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Success Rate Distribution */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Success Rate Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Timeline and Server Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Success Rate Timeline */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Success Rate Timeline</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="successRate" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Server Status */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Server Status</h3>
          <div className="space-y-3">
            {serverStatus.map((server) => (
              <div key={server.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Server className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{server.name}</p>
                    <p className="text-xs text-gray-500">
                      {server.type.toUpperCase()} {server.port && `:${server.port}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center">
                  <span className={`status-${server.status}`}>
                    {server.status === 'running' && <CheckCircle className="h-4 w-4 mr-1" />}
                    {server.status === 'stopped' && <XCircle className="h-4 w-4 mr-1" />}
                    {server.status === 'error' && <AlertTriangle className="h-4 w-4 mr-1" />}
                    {server.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Attack Reports</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vulnerabilities
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Tests
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reports.slice(0, 5).map((report) => (
                <tr key={report.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(report.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {report.platform}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <div className="progress-bar mr-2">
                        <div 
                          className={`progress-fill ${
                            report.overallSuccessRate > 70 ? 'progress-danger' :
                            report.overallSuccessRate > 40 ? 'progress-warning' : 'progress-success'
                          }`}
                          style={{ width: `${report.overallSuccessRate}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{report.overallSuccessRate.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {report.totalSuccess}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {report.totalTests}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
