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
    await new Promise(resolve => setTimeout(resolve, 300));
    return [
      { id: '1', reportType: 'Welfare Overview', period: 'Last 30 Days', units: 'All Units', generatedDate: 'Today', createdBy: 'Welfare Officer' },
      { id: '2', reportType: 'Workload Analysis', period: 'Last 90 Days', units: 'Unit C', generatedDate: 'Yesterday', createdBy: 'Commander' },
      { id: '3', reportType: 'Wellness Trends', period: 'Last 7 Days', units: 'Unit A', generatedDate: '2 Days Ago', createdBy: 'Welfare Officer' },
    ];
  }

  async generateReport(type: string, dateRange: string, unit: string, metric: string): Promise<ReportData> {
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate longer loading for generation

    return {
      title: 'Organizational Welfare Report',
      period: `Last ${dateRange} Days`,
      units: unit,
      personnelCovered: unit === 'All Units' ? 1240 : 310,
      wellnessIndicator: 'Improving',
      workloadIndicator: '+8%',
      followups: 34,
      chartData: Array.from({ length: 4 }, (_, i) => ({
        week: `Week ${i + 1}`,
        wellness: 65 + Math.random() * 20,
        workload: 40 + Math.random() * 30,
        fatigue: 30 + Math.random() * 20,
      })),
      unitComparisonData: [
        { unit: 'Unit A', value: 78 },
        { unit: 'Unit B', value: 85 },
        { unit: 'Unit C', value: 62 },
        { unit: 'Unit D', value: 71 },
      ],
      keyFindings: [
        "Overall wellness indicators remained stable during the selected period.",
        "Workload indicators increased in Unit C.",
        "Follow-up activity increased compared with the previous period."
      ],
      recommendations: [
        "Review duty distribution",
        "Consider recovery capacity",
        "Review high workload periods",
        "Ensure welfare support availability"
      ]
    };
  }

  exportCSV(reportType: string, dateRange: string, unit: string): void {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "date,unit,wellness_indicator,workload_indicator,fatigue_indicator,followups\\n"
      + "2026-08-01,Unit A,75.2,45.1,22.4,5\\n"
      + "2026-08-01,Unit B,78.5,42.0,20.1,2\\n"
      + "2026-08-01,Unit C,68.0,60.5,35.0,12\\n"
      + "2026-08-01,Unit D,72.5,50.0,28.1,7\\n";

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `manrakshak_report_${unit.replace(' ', '_')}_${dateRange}d.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  exportJSON(reportType: string, dateRange: string, unit: string): void {
    const data = {
      meta: {
        reportType,
        dateRange,
        unit,
        generatedAt: new Date().toISOString(),
        disclaimer: "Aggregate organizational data only. Prototype."
      },
      data: [
        { date: "2026-08-01", unit: "Unit A", wellness_indicator: 75.2, workload_indicator: 45.1, fatigue_indicator: 22.4, followups: 5 },
        { date: "2026-08-01", unit: "Unit B", wellness_indicator: 78.5, workload_indicator: 42.0, fatigue_indicator: 20.1, followups: 2 },
        { date: "2026-08-01", unit: "Unit C", wellness_indicator: 68.0, workload_indicator: 60.5, fatigue_indicator: 35.0, followups: 12 },
        { date: "2026-08-01", unit: "Unit D", wellness_indicator: 72.5, workload_indicator: 50.0, fatigue_indicator: 28.1, followups: 7 },
      ]
    };

    const jsonContent = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", jsonContent);
    link.setAttribute("download", `manrakshak_report_${unit.replace(' ', '_')}_${dateRange}d.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  printReport(): void {
    window.print();
  }
}

export const reportService = new ReportService();
