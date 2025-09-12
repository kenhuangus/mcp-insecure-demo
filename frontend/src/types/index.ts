export interface AttackResult {
  id: string;
  timestamp: string;
  attackType: AttackType;
  success: boolean;
  payload: string;
  response: string;
  details?: string;
}

export interface VulnerabilityMetrics {
  sqlInjection: { success: number; total: number };
  fileAccess: { success: number; total: number };
  commandExecution: { success: number; total: number };
  networkAttacks: { success: number; total: number };
  cryptoWeaknesses: { success: number; total: number };
  envExposure: { success: number; total: number };
}

export interface AttackReport {
  id: string;
  timestamp: string;
  platform: string;
  overallSuccessRate: number;
  totalSuccess: number;
  totalTests: number;
  metrics: VulnerabilityMetrics;
  individualResults: AttackResult[];
}

export interface ServerStatus {
  name: string;
  type: 'stdio' | 'sse';
  status: 'running' | 'stopped' | 'error';
  port?: number;
  pid?: number;
  lastActivity?: string;
}

export interface LiveAttackSession {
  id: string;
  serverType: string;
  startTime: string;
  status: 'running' | 'completed' | 'failed';
  currentAttack?: string;
  results: AttackResult[];
  metrics: VulnerabilityMetrics;
}

export type AttackType = 
  | 'sql_injection'
  | 'file_access'
  | 'command_execution'
  | 'network_attacks'
  | 'crypto_weaknesses'
  | 'env_exposure';

export type Platform = 'darwin' | 'linux' | 'windows';

export interface AttackPayload {
  type: AttackType;
  payload: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ServerConfig {
  name: string;
  script: string;
  type: 'stdio' | 'sse';
  port?: number;
  enabled: boolean;
}

export interface DashboardSettings {
  autoRefresh: boolean;
  refreshInterval: number;
  theme: 'light' | 'dark';
  showTimestamps: boolean;
  groupByType: boolean;
}
