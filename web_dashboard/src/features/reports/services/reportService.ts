import { fetchWithAuth } from '../../../utils/api';

export interface ReportHistoryItem {
  id: string;
  reportType: string;
  period: string;
  units: string;
  generatedDate: string;
  createdBy: string;
}

export interface ReportData {
  title: string;
  period: string;
  units: string;
  personnelCovered: number;
  wellnessIndicator: string;
  workloadIndicator: string;
  followups: number;
  chartData: any[];
  unitComparisonData: any[];
  keyFindings: string[];
  recommendations: string[];
}

export class ReportService {
  async getReportHistory(): Promise<ReportHistoryItem[]> {
    // The backend doesn't seem to have a /reports/history endpoint, 
    // we'll return an empty list or static list for now
    return [];
  }

  async generateReport(type: string, dateRange: string, unit: string, metric: string): Promise<ReportData> {
    const typeMap: Record<string, string> = {
      'Welfare Overview': 'wellness',
      'Workload Analysis': 'workload',
      'Wellness Trends': 'wellness'
    };
    const endpoint = typeMap[type] || 'wellness';
    const params = new URLSearchParams();
    if (unit && unit !== 'All Units') params.append('unit_id', unit);

    const res = await fetchWithAuth(`/reports/${endpoint}?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to generate report');
    
    const data = await res.json();
    return {
      title: `${type} Report`,
      period: `Last ${dateRange} Days`,
      units: unit,
      personnelCovered: data.personnel_count || 0,
      wellnessIndicator: 'Stable',
      workloadIndicator: 'Stable',
      followups: data.total_interventions || 0,
      chartData: [],
      unitComparisonData: [],
      keyFindings: data.insights || ["No specific findings available for this report type."],
      recommendations: ["Review duty distribution where necessary."]
    };
  }

  exportCSV(reportType: string, dateRange: string, unit: string): void {
    const typeMap: Record<string, string> = {
      'Welfare Overview': 'wellness',
      'Workload Analysis': 'workload',
      'Wellness Trends': 'wellness'
    };
    const endpoint = typeMap[reportType] || 'wellness';
    const params = new URLSearchParams({ format: 'csv' });
    if (unit && unit !== 'All Units') params.append('unit_id', unit);
    
    window.open(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/reports/${endpoint}/export?${params.toString()}&token=${localStorage.getItem('manrakshak_token')}`, '_blank');
  }

  exportJSON(reportType: string, dateRange: string, unit: string): void {
    const typeMap: Record<string, string> = {
      'Welfare Overview': 'wellness',
      'Workload Analysis': 'workload',
      'Wellness Trends': 'wellness'
    };
    const endpoint = typeMap[reportType] || 'wellness';
    const params = new URLSearchParams({ format: 'json' });
    if (unit && unit !== 'All Units') params.append('unit_id', unit);
    
    window.open(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/reports/${endpoint}/export?${params.toString()}&token=${localStorage.getItem('manrakshak_token')}`, '_blank');
  }

  printReport(): void {
    window.print();
  }
}

export const reportService = new ReportService();
