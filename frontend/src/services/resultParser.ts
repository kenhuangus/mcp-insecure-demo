import { AttackResult, AttackReport, AttackType } from '@/types';

export class ResultParser {
  private static parseTimestamp(filename: string): string {
    // Extract timestamp from filename like "stdio_basic_20250911_133105.txt"
    const match = filename.match(/(\d{8}_\d{6})/);
    if (match) {
      const [date, time] = match[1].split('_');
      const year = `20${date.slice(0, 2)}`;
      const month = date.slice(2, 4);
      const day = date.slice(4, 6);
      const hour = time.slice(0, 2);
      const minute = time.slice(2, 4);
      const second = time.slice(4, 6);
      return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
    }
    return new Date().toISOString();
  }

  private static parseAttackType(line: string): AttackType | null {
    if (line.includes('SQL Injection')) return 'sql_injection';
    if (line.includes('File Access')) return 'file_access';
    if (line.includes('Command Execution')) return 'command_execution';
    if (line.includes('Network Attacks')) return 'network_attacks';
    if (line.includes('Cryptographic Weaknesses')) return 'crypto_weaknesses';
    if (line.includes('Environment Variable Exposure')) return 'env_exposure';
    return null;
  }

  private static parseSuccessRate(line: string): { success: number; total: number } | null {
    // Parse lines like "Attack Success Rate: 15/25 (60.0%)"
    const match = line.match(/Attack Success Rate:\s*(\d+)\/(\d+)\s*\(([\d.]+)%\)/);
    if (match) {
      return {
        success: parseInt(match[1]),
        total: parseInt(match[2])
      };
    }
    return null;
  }

  private static parseComprehensiveReport(content: string): AttackReport | null {
    let report: Partial<AttackReport> = {
      id: `report_${Date.now()}`,
      timestamp: new Date().toISOString(),
      platform: 'unknown',
      overallSuccessRate: 0,
      totalSuccess: 0,
      totalTests: 0,
      metrics: {
        sqlInjection: { success: 0, total: 0 },
        fileAccess: { success: 0, total: 0 },
        commandExecution: { success: 0, total: 0 },
        networkAttacks: { success: 0, total: 0 },
        cryptoWeaknesses: { success: 0, total: 0 },
        envExposure: { success: 0, total: 0 }
      },
      individualResults: []
    };

    // Parse platform
    const platformMatch = content.match(/COMPREHENSIVE ATTACK REPORT - (\w+)/);
    if (platformMatch) {
      report.platform = platformMatch[1].toLowerCase();
    }

    // Parse overall success rate
    const overallMatch = content.match(/Overall Success Rate:\s*(\d+)\/(\d+)\s*\(([\d.]+)%\)/);
    if (overallMatch) {
      report.totalSuccess = parseInt(overallMatch[1]);
      report.totalTests = parseInt(overallMatch[2]);
      report.overallSuccessRate = parseFloat(overallMatch[3]);
    }

    // Parse individual metrics
    const metricPatterns = {
      sqlInjection: /SQL Injection:\s*(\d+)\/(\d+)/,
      fileAccess: /File Access:\s*(\d+)\/(\d+)/,
      commandExecution: /Command Execution:\s*(\d+)\/(\d+)/,
      networkAttacks: /Network Attacks:\s*(\d+)\/(\d+)/,
      cryptoWeaknesses: /Crypto Weaknesses:\s*(\d+)\/(\d+)/,
      envExposure: /Env Exposure:\s*(\d+)\/(\d+)/
    };

    for (const [key, pattern] of Object.entries(metricPatterns)) {
      const match = content.match(pattern);
      if (match && report.metrics) {
        (report.metrics as any)[key] = {
          success: parseInt(match[1]),
          total: parseInt(match[2])
        };
      }
    }

    return report as AttackReport;
  }

  private static parseBasicReport(content: string, filename: string): AttackReport {
    const lines = content.split('\n');
    const report: AttackReport = {
      id: `report_${Date.now()}`,
      timestamp: this.parseTimestamp(filename),
      platform: 'unknown',
      overallSuccessRate: 0,
      totalSuccess: 0,
      totalTests: 0,
      metrics: {
        sqlInjection: { success: 0, total: 0 },
        fileAccess: { success: 0, total: 0 },
        commandExecution: { success: 0, total: 0 },
        networkAttacks: { success: 0, total: 0 },
        cryptoWeaknesses: { success: 0, total: 0 },
        envExposure: { success: 0, total: 0 }
      },
      individualResults: []
    };

    // Parse individual attack results
    let currentAttack: Partial<AttackResult> | null = null;
    
    for (const line of lines) {
      if (line.includes('Testing') && line.includes('...')) {
        const attackType = this.parseAttackType(line);
        if (attackType && currentAttack) {
          report.individualResults.push(currentAttack as AttackResult);
        }
        currentAttack = {
          id: `attack_${Date.now()}_${Math.random()}`,
          timestamp: report.timestamp,
          attackType: attackType || 'sql_injection',
          success: false,
          payload: '',
          response: ''
        };
      }

      if (line.includes('Trying payload:') && currentAttack) {
        currentAttack.payload = line.split('Trying payload: ')[1] || '';
      }

      if (line.includes('Result:') && currentAttack) {
        currentAttack.response = line.split('Result: ')[1] || '';
      }

      if (line.includes('Error:') && currentAttack) {
        currentAttack.success = false;
        currentAttack.details = line.split('Error: ')[1] || '';
      }

      // Parse success rates for different attack types
      const successRate = this.parseSuccessRate(line);
      if (successRate) {
        // Try to determine which metric this belongs to based on context
        if (line.includes('SQL Injection')) {
          report.metrics.sqlInjection = successRate;
        } else if (line.includes('Arbitrary SQL')) {
          report.metrics.sqlInjection.total += successRate.total;
          report.metrics.sqlInjection.success += successRate.success;
        } else if (line.includes('Env Leak')) {
          report.metrics.envExposure = successRate;
        } else if (line.includes('Query Insert/Check')) {
          report.metrics.sqlInjection.total += successRate.total;
          report.metrics.sqlInjection.success += successRate.success;
        } else if (line.includes('Tool Enum')) {
          // Tool enumeration doesn't map to a specific metric, skip
        }
      }
    }

    // Add the last attack if exists
    if (currentAttack) {
      report.individualResults.push(currentAttack as AttackResult);
    }

    // Calculate overall metrics
    report.totalSuccess = Object.values(report.metrics).reduce((sum, metric) => sum + metric.success, 0);
    report.totalTests = Object.values(report.metrics).reduce((sum, metric) => sum + metric.total, 0);
    report.overallSuccessRate = report.totalTests > 0 ? (report.totalSuccess / report.totalTests) * 100 : 0;

    return report;
  }

  private static parseSSEReport(content: string, filename: string): AttackReport {
    const lines = content.split('\n');
    const report: AttackReport = {
      id: `sse_report_${Date.now()}`,
      timestamp: this.parseTimestamp(filename),
      platform: 'unknown',
      overallSuccessRate: 0,
      totalSuccess: 0,
      totalTests: 0,
      metrics: {
        sqlInjection: { success: 0, total: 0 },
        fileAccess: { success: 0, total: 0 },
        commandExecution: { success: 0, total: 0 },
        networkAttacks: { success: 0, total: 0 },
        cryptoWeaknesses: { success: 0, total: 0 },
        envExposure: { success: 0, total: 0 }
      },
      individualResults: []
    };

    let sqlInjectionSuccess = 0;
    let sqlInjectionTotal = 0;
    let envLeakSuccess = 0;
    let envLeakTotal = 0;

    for (const line of lines) {
      if (line.includes('[CLIENT][SUCCESS] SQLi attack succeeded!')) {
        sqlInjectionSuccess++;
      }
      if (line.includes('[CLIENT][ATTACK]') && line.includes('SQL Injection')) {
        sqlInjectionTotal++;
      }
      if (line.includes('[CLIENT][ATTACK]') && line.includes('Env Leak')) {
        envLeakTotal++;
      }
      if (line.includes('"value":"Not found"') && line.includes('env_var')) {
        // Environment variable not found - this is actually a "success" for the attack
        envLeakSuccess++;
      }
    }

    report.metrics.sqlInjection = { success: sqlInjectionSuccess, total: sqlInjectionTotal };
    report.metrics.envExposure = { success: envLeakSuccess, total: envLeakTotal };

    // Parse the final success rate
    const finalMatch = content.match(/Attack success rate:\s*(\d+)\/(\d+)\s*\(([\d.]+)%\)/);
    if (finalMatch) {
      report.totalSuccess = parseInt(finalMatch[1]);
      report.totalTests = parseInt(finalMatch[2]);
      report.overallSuccessRate = parseFloat(finalMatch[3]);
    } else {
      report.totalSuccess = sqlInjectionSuccess + envLeakSuccess;
      report.totalTests = sqlInjectionTotal + envLeakTotal;
      report.overallSuccessRate = report.totalTests > 0 ? (report.totalSuccess / report.totalTests) * 100 : 0;
    }

    return report;
  }

  static parseResultFile(filename: string, content: string): AttackReport {
    if (filename.includes('comprehensive') || content.includes('COMPREHENSIVE ATTACK REPORT')) {
      return this.parseComprehensiveReport(content) || this.parseBasicReport(content, filename);
    } else if (filename.includes('sse')) {
      return this.parseSSEReport(content, filename);
    } else {
      return this.parseBasicReport(content, filename);
    }
  }

  static parseMultipleFiles(files: { filename: string; content: string }[]): AttackReport[] {
    return files.map(file => this.parseResultFile(file.filename, file.content));
  }
}
