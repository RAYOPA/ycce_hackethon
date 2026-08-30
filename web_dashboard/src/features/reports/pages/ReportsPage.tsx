import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, Printer, Filter, ShieldCheck, 
  Activity, Users, RefreshCw, TrendingUp, ChevronRight, CheckCircle, Search
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';
import { reportService } from '../services/reportService';
import type { ReportHistoryItem, ReportData } from '../services/reportService';

export const ReportsPage: React.FC = () => {
  // Config state
  const [reportType, setReportType] = useState('Welfare Overview');
  const [dateRange, setDateRange] = useState('30');
  const [unit, setUnit] = useState('All Units');
  const [metric, setMetric] = useState('Wellness');

  // App state
  const [history, setHistory] = useState<ReportHistoryItem[]>([]);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    const loadHistory = async () => {
      const data = await reportService.getReportHistory();
      setHistory(data);
    };
    loadHistory();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setShowSuccess(false);
    setReportData(null); // Clear previous
    
    try {
      const data = await reportService.generateReport(reportType, dateRange, unit, metric);
      setReportData(data);
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportCSV = () => {
    reportService.exportCSV(reportType, dateRange, unit);
  };

  const handleExportJSON = () => {
    reportService.exportJSON(reportType, dateRange, unit);
  };

  const handlePrint = () => {
    reportService.printReport();
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Reports</h1>
          <p className="text-slate-500 mt-1">Generate organizational welfare and workload reports</p>
        </div>
        <button 
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex items-center gap-2 px-6 py-2.5 bg-primary-navy text-white rounded-lg hover:bg-primary-navy/90 transition-colors shadow-md font-bold disabled:opacity-70"
        >
          {isGenerating ? <RefreshCw className="animate-spin" size={18} /> : <FileText size={18} />}
          {isGenerating ? 'Preparing report...' : 'Generate Report'}
        </button>
      </div>

      {/* Privacy Notice */}
      <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 p-3 rounded-lg text-slate-600 shadow-sm print:hidden">
        <ShieldCheck size={18} className="mt-0.5 text-secondary-teal shrink-0" />
        <div>
          <p className="font-bold text-slate-800 text-sm">Privacy-first reporting</p>
          <p className="text-xs mt-0.5">
            Reports are generated according to the user's access permissions. Individual welfare information is restricted to authorized personnel. Aggregate organizational data only.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LEFT COLUMN: Config & History (Hidden in print) */}
        <div className="lg:col-span-4 space-y-6 print:hidden">
          
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Filter size={18} className="text-slate-400" />
              <h2 className="font-bold text-primary-navy text-lg">Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Report Type</label>
                <select 
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <option>Welfare Overview</option>
                  <option>Wellness Trends</option>
                  <option>Workload Analysis</option>
                  <option>Unit Comparison</option>
                  <option>Follow-up Summary</option>
                  <option>Intervention Summary</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Date Range</label>
                <select 
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                >
                  <option value="7">Last 7 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                  <option value="custom">Custom Range</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Unit</label>
                <select 
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                  value={unit}
                  onChange={(e) => setUnit(e.target.value)}
                >
                  <option>All Units</option>
                  <option>Unit A</option>
                  <option>Unit B</option>
                  <option>Unit C</option>
                  <option>Unit D</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Metric Focus</label>
                <select 
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                >
                  <option>Wellness</option>
                  <option>Workload</option>
                  <option>Fatigue</option>
                  <option>Sleep</option>
                  <option>Night Duty</option>
                  <option>Follow-ups</option>
                  <option>Interventions</option>
                </select>
              </div>

              <div className="pt-2 flex gap-2">
                <button 
                  onClick={handleGenerate}
                  className="flex-1 bg-secondary-teal text-white py-2 rounded-lg font-bold text-sm hover:bg-secondary-teal/90 transition-colors"
                >
                  Apply Filters
                </button>
                <button className="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg font-bold text-sm hover:bg-slate-200 transition-colors">
                  Reset
                </button>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50">
              <h2 className="font-bold text-primary-navy">Recent Reports</h2>
            </div>
            <div className="divide-y divide-slate-100">
              {history.map(item => (
                <div key={item.id} className="p-4 hover:bg-slate-50 transition-colors">
                  <p className="font-bold text-sm text-slate-800">{item.reportType}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{item.period} • {item.units}</p>
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-[10px] uppercase font-bold text-slate-400">{item.generatedDate}</span>
                    <button className="text-xs font-bold text-secondary-teal hover:text-primary-navy flex items-center gap-1">
                      View <ChevronRight size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Report Preview & Actions */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          
          {/* Status Message */}
          {showSuccess && (
            <div className="bg-[#E6F4EA] border border-[#CEEAD6] text-[#137333] px-4 py-3 rounded-lg flex items-center gap-2 shadow-sm print:hidden">
              <CheckCircle size={18} />
              <span className="font-medium text-sm">Report generated successfully.</span>
            </div>
          )}

          {isGenerating ? (
            <div className="bg-white flex-1 min-h-[500px] rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-slate-400">
              <RefreshCw className="animate-spin mb-3 text-secondary-teal" size={32} />
              <p className="font-medium">Preparing report...</p>
            </div>
          ) : !reportData ? (
            <div className="bg-white flex-1 min-h-[500px] rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-slate-400 p-8 text-center print:hidden">
              <Search className="mb-4 text-slate-300" size={48} />
              <p className="font-bold text-lg text-slate-600">No reports yet</p>
              <p className="text-sm mt-1 max-w-xs">Configure your report on the left and select Generate Report to see the preview here.</p>
            </div>
          ) : (
            <>
              {/* Report Preview Card */}
              <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm print:shadow-none print:border-none print:p-0 relative">
                
                <div className="absolute top-6 right-6 px-2 py-1 bg-slate-100 text-slate-500 text-[10px] font-bold uppercase rounded border border-slate-200 print:hidden">
                  Demo / Prototype Data
                </div>

                <div className="mb-8 border-b border-slate-200 pb-6">
                  <h2 className="text-2xl font-black text-primary-navy uppercase tracking-tight">ManRakshak</h2>
                  <h3 className="text-lg text-slate-600 mt-1">{reportData.title}</h3>
                  <div className="flex gap-6 mt-4 text-sm">
                    <div>
                      <span className="text-slate-400 block text-xs uppercase font-bold">Period</span>
                      <span className="font-medium text-slate-800">{reportData.period}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-xs uppercase font-bold">Units</span>
                      <span className="font-medium text-slate-800">{reportData.units}</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-1 flex items-center gap-1">
                      <Users size={14} /> Personnel Covered
                    </p>
                    <p className="text-xl font-black text-slate-800">{reportData.personnelCovered.toLocaleString()}</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-1 flex items-center gap-1">
                      <Activity size={14} /> Wellness Indicator
                    </p>
                    <p className="text-xl font-black text-positive">{reportData.wellnessIndicator}</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-1 flex items-center gap-1">
                      <TrendingUp size={14} /> Workload Indicator
                    </p>
                    <p className="text-xl font-black text-attention-700">{reportData.workloadIndicator}</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs font-bold text-slate-500 uppercase mb-1 flex items-center gap-1">
                      <RefreshCw size={14} /> Follow-ups
                    </p>
                    <p className="text-xl font-black text-primary-navy">{reportData.followups}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                  <div>
                    <h4 className="font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Indicators Trend</h4>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={reportData.chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                          <RechartsTooltip />
                          <Line type="monotone" name="Wellness" dataKey="wellness" stroke="#8BBB92" strokeWidth={2} dot={false} />
                          <Line type="monotone" name="Workload" dataKey="workload" stroke="#F59E0B" strokeWidth={2} dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Unit Comparison</h4>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={reportData.unitComparisonData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="unit" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                          <RechartsTooltip cursor={{ fill: '#f8fafc' }} />
                          <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                            {reportData.unitComparisonData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={index === 0 ? '#092328' : index === 1 ? '#12544F' : '#8BBB92'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h4 className="font-bold text-slate-800 mb-3 flex items-center justify-between border-b border-slate-100 pb-2">
                      Key Findings
                      <span className="text-[10px] font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded">Prototype-generated summary</span>
                    </h4>
                    <ul className="space-y-2">
                      {reportData.keyFindings.map((finding, idx) => (
                        <li key={idx} className="text-sm text-slate-600 flex gap-2">
                          <span className="text-secondary-teal">•</span> {finding}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2">Planning Considerations</h4>
                    <ul className="space-y-2">
                      {reportData.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-sm text-slate-600 flex gap-2">
                          <span className="text-amber-500">•</span> {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

              </div>

              {/* Export Actions Panel */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm print:hidden">
                <h3 className="font-bold text-primary-navy mb-4">Export Report</h3>
                <div className="flex flex-wrap gap-3">
                  <button 
                    onClick={handleExportCSV}
                    className="flex items-center justify-center gap-2 flex-1 min-w-[120px] px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    <Download size={16} /> Export CSV
                  </button>
                  <button 
                    onClick={handleExportJSON}
                    className="flex items-center justify-center gap-2 flex-1 min-w-[120px] px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    <FileText size={16} /> Export JSON
                  </button>
                  <button 
                    onClick={handlePrint}
                    className="flex items-center justify-center gap-2 flex-1 min-w-[120px] px-4 py-2 bg-slate-100 border border-slate-200 rounded-lg text-sm font-bold text-primary-navy hover:bg-slate-200 transition-colors"
                  >
                    <Printer size={16} /> Print Report
                  </button>
                  <button className="flex items-center justify-center gap-2 flex-1 min-w-[120px] px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-400 cursor-not-allowed">
                    Generate PDF
                    <span className="text-[10px] uppercase bg-slate-100 px-1 rounded ml-1">V2</span>
                  </button>
                </div>
              </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
};
