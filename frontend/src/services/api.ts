import { AttackReport, ServerStatus, LiveAttackSession } from '@/types';

export class ApiService {
  private static baseUrl = '/api';

  static async getAttackReports(): Promise<AttackReport[]> {
    try {
      const response = await fetch(`${this.baseUrl}/reports`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch attack reports:', error);
      // Return mock data for development
      return this.getMockReports();
    }
  }

  static async getServerStatus(): Promise<ServerStatus[]> {
    try {
      const response = await fetch(`${this.baseUrl}/servers/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch server status:', error);
      return this.getMockServerStatus();
    }
  }

  static async startServer(serverType: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/servers/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ serverType }),
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to start server:', error);
      return false;
    }
  }

  static async stopServer(serverType: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/servers/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ serverType }),
      });
      return response.ok;
    } catch (error) {
      console.error('Failed to stop server:', error);
      return false;
    }
  }

  static async runAttack(serverType: string, attackType?: string): Promise<LiveAttackSession> {
    try {
      const response = await fetch(`${this.baseUrl}/attacks/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ serverType, attackType }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to run attack:', error);
      throw error;
    }
  }

  static async getLiveAttackSession(sessionId: string): Promise<LiveAttackSession> {
    try {
      const response = await fetch(`${this.baseUrl}/attacks/session/${sessionId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch live attack session:', error);
      throw error;
    }
  }

  static async uploadResultFile(file: File): Promise<AttackReport> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${this.baseUrl}/reports/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to upload result file:', error);
      throw error;
    }
  }

  // Mock data for development
  private static getMockReports(): AttackReport[] {
    return [
      {
        id: 'report_1',
        timestamp: '2025-01-11 13:31:05',
        platform: 'darwin',
        overallSuccessRate: 60.0,
        totalSuccess: 15,
        totalTests: 25,
        metrics: {
          sqlInjection: { success: 8, total: 10 },
          fileAccess: { success: 3, total: 8 },
          commandExecution: { success: 2, total: 5 },
          networkAttacks: { success: 1, total: 4 },
          cryptoWeaknesses: { success: 1, total: 3 },
          envExposure: { success: 0, total: 0 }
        },
        individualResults: []
      },
      {
        id: 'report_2',
        timestamp: '2025-01-11 13:30:45',
        platform: 'darwin',
        overallSuccessRate: 25.0,
        totalSuccess: 5,
        totalTests: 20,
        metrics: {
          sqlInjection: { success: 4, total: 10 },
          fileAccess: { success: 0, total: 0 },
          commandExecution: { success: 0, total: 0 },
          networkAttacks: { success: 0, total: 0 },
          cryptoWeaknesses: { success: 0, total: 0 },
          envExposure: { success: 1, total: 10 }
        },
        individualResults: []
      }
    ];
  }

  private static getMockServerStatus(): ServerStatus[] {
    return [
      {
        name: 'STDIO Server',
        type: 'stdio',
        status: 'running',
        pid: 12345,
        lastActivity: '2025-01-11 13:31:05'
      },
      {
        name: 'Enhanced STDIO Server',
        type: 'stdio',
        status: 'stopped',
        lastActivity: '2025-01-11 13:25:30'
      },
      {
        name: 'SSE Server',
        type: 'sse',
        status: 'running',
        port: 9000,
        pid: 12346,
        lastActivity: '2025-01-11 13:31:05'
      }
    ];
  }
}
