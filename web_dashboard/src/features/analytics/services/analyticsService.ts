export interface TrendDataPoint {
  date: string;
  wellness: number;
  workload: number;
  fatigue: number;
}

export interface UnitComparisonData {
  unit: string;
  wellness: number;
  workload: number;
  fatigue: number;
}

export interface FactorData {
  name: string;
  value: number;
}

export interface ScatterDataPoint {
  unit: string;
  period: string;
  workload: number;
  fatigue: number;
}

export interface TimePeriodData {
  day: string;
  workload: number;
  fatigue: number;
}

export class AnalyticsService {
  async getTrendData(unit: string, days: number): Promise<TrendDataPoint[]> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Generate data based on days
    const dataPoints = days === 7 ? 7 : days === 30 ? 4 : 12; // 7 days, 4 weeks, 12 weeks
    const labelPrefix = days === 7 ? 'Day ' : 'Week ';
    
    return Array.from({ length: dataPoints }, (_, i) => ({
      date: `${labelPrefix}${i + 1}`,
      wellness: 60 + Math.random() * 20,
      workload: 30 + Math.random() * 40,
      fatigue: 20 + Math.random() * 30,
    }));
  }

  async getUnitComparison(): Promise<UnitComparisonData[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return [
      { unit: 'Unit A', wellness: 78, workload: 65, fatigue: 32 },
      { unit: 'Unit B', wellness: 85, workload: 45, fatigue: 20 },
      { unit: 'Unit C', wellness: 62, workload: 82, fatigue: 55 },
      { unit: 'Unit D', wellness: 71, workload: 58, fatigue: 40 },
    ];
  }

  async getFactorsData(): Promise<FactorData[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return [
      { name: 'Sleep pattern', value: 85 },
      { name: 'Workload', value: 65 },
      { name: 'Night duty', value: 45 },
      { name: 'Consecutive duty', value: 30 },
      { name: 'Leave gap', value: 20 },
    ];
  }

  async getScatterData(): Promise<ScatterDataPoint[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    const units = ['Unit A', 'Unit B', 'Unit C', 'Unit D'];
    const data: ScatterDataPoint[] = [];
    
    for (const unit of units) {
      for (let i = 1; i <= 4; i++) {
        data.push({
          unit,
          period: `Week ${i}`,
          workload: 30 + Math.random() * 60,
          fatigue: 20 + Math.random() * 60,
        });
      }
    }
    return data;
  }

  async getTimePeriodData(): Promise<TimePeriodData[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return [
      { day: 'Mon', workload: 65, fatigue: 30 },
      { day: 'Tue', workload: 70, fatigue: 35 },
      { day: 'Wed', workload: 75, fatigue: 45 },
      { day: 'Thu', workload: 80, fatigue: 55 },
      { day: 'Fri', workload: 85, fatigue: 65 },
      { day: 'Sat', workload: 40, fatigue: 40 },
      { day: 'Sun', workload: 30, fatigue: 25 },
    ];
  }

  exportAnalytics(unit: string, days: number): void {
    // Generate a mock CSV string
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Date,Aggregate_Wellness,Aggregate_Workload,Aggregate_Fatigue\\n"
      + "Week 1,75.2,45.1,22.4\\n"
      + "Week 2,74.8,48.2,25.1\\n"
      + "Week 3,71.0,60.5,35.0\\n"
      + "Week 4,68.5,65.0,42.1\\n";

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `manrakshak_aggregate_report_${unit.replace(' ', '_')}_${days}d.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

export const analyticsService = new AnalyticsService();
