import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Save, 
  Server, 
  AlertTriangle
} from 'lucide-react';
import { DashboardSettings, ServerConfig } from '@/types';

export function Settings() {
  const [settings, setSettings] = useState<DashboardSettings>({
    autoRefresh: true,
    refreshInterval: 30,
    theme: 'light',
    showTimestamps: true,
    groupByType: false
  });

  const [serverConfigs, setServerConfigs] = useState<ServerConfig[]>([
    {
      name: 'STDIO Server',
      script: 'vuln-mcp.py',
      type: 'stdio',
      enabled: true
    },
    {
      name: 'Enhanced STDIO Server',
      script: 'enhanced-vuln-mcp.py',
      type: 'stdio',
      enabled: true
    },
    {
      name: 'SSE Server',
      script: 'mcp-sse-vulnerable-server.py',
      type: 'sse',
      port: 9000,
      enabled: true
    }
  ]);

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('dashboard-settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }

    const savedServerConfigs = localStorage.getItem('server-configs');
    if (savedServerConfigs) {
      setServerConfigs(JSON.parse(savedServerConfigs));
    }
  }, []);

  const saveSettings = () => {
    localStorage.setItem('dashboard-settings', JSON.stringify(settings));
    localStorage.setItem('server-configs', JSON.stringify(serverConfigs));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const updateSetting = <K extends keyof DashboardSettings>(
    key: K,
    value: DashboardSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const updateServerConfig = (index: number, updates: Partial<ServerConfig>) => {
    setServerConfigs(prev => prev.map((config, i) => 
      i === index ? { ...config, ...updates } : config
    ));
  };

  const addServerConfig = () => {
    setServerConfigs(prev => [...prev, {
      name: 'New Server',
      script: '',
      type: 'stdio',
      enabled: false
    }]);
  };

  const removeServerConfig = (index: number) => {
    setServerConfigs(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure dashboard preferences and server settings</p>
        </div>
        <button
          onClick={saveSettings}
          className={`btn-primary flex items-center ${saved ? 'bg-success-600 hover:bg-success-700' : ''}`}
        >
          <Save className="h-4 w-4 mr-2" />
          {saved ? 'Saved!' : 'Save Settings'}
        </button>
      </div>

      {/* Dashboard Settings */}
      <div className="card">
        <div className="flex items-center mb-4">
          <SettingsIcon className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Dashboard Settings</h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Auto Refresh</label>
              <p className="text-sm text-gray-500">Automatically refresh data</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={(e) => updateSetting('autoRefresh', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Refresh Interval (seconds)
            </label>
            <select
              value={settings.refreshInterval}
              onChange={(e) => updateSetting('refreshInterval', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={10}>10 seconds</option>
              <option value={30}>30 seconds</option>
              <option value={60}>1 minute</option>
              <option value={300}>5 minutes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Theme
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  checked={settings.theme === 'light'}
                  onChange={(e) => updateSetting('theme', e.target.value as 'light' | 'dark')}
                  className="mr-2"
                />
                Light
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  checked={settings.theme === 'dark'}
                  onChange={(e) => updateSetting('theme', e.target.value as 'light' | 'dark')}
                  className="mr-2"
                />
                Dark
              </label>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Show Timestamps</label>
              <p className="text-sm text-gray-500">Display timestamps in results</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.showTimestamps}
                onChange={(e) => updateSetting('showTimestamps', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Group by Type</label>
              <p className="text-sm text-gray-500">Group results by attack type</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.groupByType}
                onChange={(e) => updateSetting('groupByType', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Server Configuration */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Server className="h-5 w-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Server Configuration</h3>
          </div>
          <button
            onClick={addServerConfig}
            className="btn-secondary text-sm"
          >
            Add Server
          </button>
        </div>

        <div className="space-y-4">
          {serverConfigs.map((config, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    value={config.name}
                    onChange={(e) => updateServerConfig(index, { name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Script
                  </label>
                  <input
                    type="text"
                    value={config.script}
                    onChange={(e) => updateServerConfig(index, { script: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    value={config.type}
                    onChange={(e) => updateServerConfig(index, { type: e.target.value as 'stdio' | 'sse' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="stdio">STDIO</option>
                    <option value="sse">SSE</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Port (SSE only)
                  </label>
                  <input
                    type="number"
                    value={config.port || ''}
                    onChange={(e) => updateServerConfig(index, { port: parseInt(e.target.value) || undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    disabled={config.type === 'stdio'}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between mt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={config.enabled}
                    onChange={(e) => updateServerConfig(index, { enabled: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Enabled</span>
                </label>
                <button
                  onClick={() => removeServerConfig(index)}
                  className="text-danger-600 hover:text-danger-800 text-sm"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Security Notice */}
      <div className="card border-warning-200 bg-warning-50">
        <div className="flex items-start">
          <AlertTriangle className="h-5 w-5 text-warning-600 mr-3 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-warning-800">Security Notice</h3>
            <p className="text-sm text-warning-700 mt-1">
              This dashboard is designed for educational and testing purposes only. 
              Do not use in production environments or with sensitive data. 
              All servers are intentionally vulnerable and should only be run in isolated environments.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
