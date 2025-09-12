import { useState, useEffect, useRef } from 'react';
import { 
  FileText, 
  Upload, 
  Download, 
  Eye, 
  Filter,
  Search,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { ApiService } from '@/services/api';
import { AttackReport } from '@/types';

export function Reports() {
  const [reports, setReports] = useState<AttackReport[]>([]);
  const [filteredReports, setFilteredReports] = useState<AttackReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<AttackReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPlatform, setFilterPlatform] = useState<string>('all');
  const [filterDateRange, setFilterDateRange] = useState<string>('all');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    filterReports();
  }, [reports, searchTerm, filterPlatform, filterDateRange]);

  const fetchReports = async () => {
    try {
      const data = await ApiService.getAttackReports();
      setReports(data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterReports = () => {
    let filtered = [...reports];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(report =>
        report.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.platform.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Platform filter
    if (filterPlatform !== 'all') {
      filtered = filtered.filter(report => report.platform === filterPlatform);
    }

    // Date range filter
    if (filterDateRange !== 'all') {
      const now = new Date();
      
      switch (filterDateRange) {
        case 'today':
          filtered = filtered.filter(report => {
            const reportDate = new Date(report.timestamp);
            return reportDate.toDateString() === now.toDateString();
          });
          break;
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          filtered = filtered.filter(report => new Date(report.timestamp) >= weekAgo);
          break;
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          filtered = filtered.filter(report => new Date(report.timestamp) >= monthAgo);
          break;
      }
    }

    setFilteredReports(filtered);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const report = await ApiService.uploadResultFile(file);
      setReports(prev => [report, ...prev]);
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('Failed to upload file. Please try again.');
    }
  };

  const exportReport = (report: AttackReport) => {
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${report.id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getSeverityColor = (successRate: number) => {
    if (successRate > 70) return 'text-danger-600 bg-danger-100';
    if (successRate > 40) return 'text-warning-600 bg-warning-100';
    return 'text-success-600 bg-success-100';
  };

  const getSeverityIcon = (successRate: number) => {
    if (successRate > 70) return <AlertTriangle className="h-4 w-4" />;
    if (successRate > 40) return <XCircle className="h-4 w-4" />;
    return <CheckCircle className="h-4 w-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Attack Reports</h1>
          <p className="text-gray-600">View and analyze vulnerability assessment results</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-secondary flex items-center"
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload Report
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.json"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <select
            value={filterPlatform}
            onChange={(e) => setFilterPlatform(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Platforms</option>
            <option value="darwin">macOS</option>
            <option value="linux">Linux</option>
            <option value="windows">Windows</option>
          </select>

          <select
            value={filterDateRange}
            onChange={(e) => setFilterDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>

          <div className="text-sm text-gray-500 flex items-center">
            <Filter className="h-4 w-4 mr-1" />
            {filteredReports.length} of {reports.length} reports
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports Table */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Reports</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Report
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Platform
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Success Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredReports.map((report) => (
                    <tr 
                      key={report.id}
                      className={`hover:bg-gray-50 cursor-pointer ${selectedReport?.id === report.id ? 'bg-primary-50' : ''}`}
                      onClick={() => setSelectedReport(report)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {report.id}
                          </div>
                          <div className="text-sm text-gray-500">
                            {new Date(report.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {report.platform}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-2 ${getSeverityColor(report.overallSuccessRate)}`}>
                            {getSeverityIcon(report.overallSuccessRate)}
                            <span className="ml-1">{report.overallSuccessRate.toFixed(1)}%</span>
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedReport(report);
                            }}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              exportReport(report);
                            }}
                            className="text-gray-600 hover:text-gray-900"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Report Details */}
        <div className="lg:col-span-1">
          {selectedReport ? (
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Report Details</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Report ID</label>
                  <p className="text-sm text-gray-900">{selectedReport.id}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Timestamp</label>
                  <p className="text-sm text-gray-900">{new Date(selectedReport.timestamp).toLocaleString()}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Platform</label>
                  <p className="text-sm text-gray-900">{selectedReport.platform}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Overall Success Rate</label>
                  <div className="flex items-center mt-1">
                    <div className="progress-bar flex-1 mr-2">
                      <div 
                        className={`progress-fill ${
                          selectedReport.overallSuccessRate > 70 ? 'progress-danger' :
                          selectedReport.overallSuccessRate > 40 ? 'progress-warning' : 'progress-success'
                        }`}
                        style={{ width: `${selectedReport.overallSuccessRate}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{selectedReport.overallSuccessRate.toFixed(1)}%</span>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-500">Vulnerability Metrics</label>
                  <div className="mt-2 space-y-2">
                    {Object.entries(selectedReport.metrics).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </span>
                        <span className="text-sm font-medium">
                          {value.success}/{value.total}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Select a report to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
