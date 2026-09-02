import { fetchWithAuth } from '../../../utils/api';

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
    const params = new URLSearchParams({ days: days.toString() });
    if (unit && unit !== 'All Units' && unit !== 'All Commands') {
      params.append('unit_id', unit); // Need backend support for unit_id filtering if any, otherwise it falls back to user scope
    }
    
    const res = await fetchWithAuth(`/analytics/wellness?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    const data = await res.json();
    
    if (data.insufficient_cohort) {
      return []; // Or handle gracefully in UI
    }

    return data.trend.map((t: any) => ({
      date: t.date,
      wellness: (t.average_sleep_hours * 10), // mock aggregation mapping for UI visually
      workload: (t.average_workload_score * 20),
      fatigue: (t.average_stress_score * 20),
    }));
  }

  async getUnitComparison(): Promise<UnitComparisonData[]> {
    const res = await fetchWithAuth(`/analytics/units`);
    if (!res.ok) throw new Error('Failed to fetch unit analytics');
    const data = await res.json();
    
    return data.units.map((u: any) => ({
      unit: u.unit_name,
      wellness: u.insufficient_cohort ? 0 : (u.average_sleep_hours || 0) * 10,
      workload: u.insufficient_cohort ? 0 : (u.average_workload_score || 0) * 20,
      fatigue: u.insufficient_cohort ? 0 : (u.average_stress_score || 0) * 20,
    }));
  }

  async getFactorsData(): Promise<FactorData[]> {
    // Backend doesn't have factors currently. Return empty or static.
    return [];
  }

  async getScatterData(): Promise<ScatterDataPoint[]> {
    // Backend doesn't have scatter currently. Return empty or static.
    return [];
  }

  async getTimePeriodData(): Promise<TimePeriodData[]> {
    // Backend doesn't have specific time period aggregations currently.
    return [];
  }

  exportAnalytics(unit: string, days: number): void {
    // Just hitting the export endpoint if it exists
    window.open(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/reports/export/analytics?days=${days}&token=${localStorage.getItem('manrakshak_token')}`, '_blank');
  }
}

export const analyticsService = new AnalyticsService();
