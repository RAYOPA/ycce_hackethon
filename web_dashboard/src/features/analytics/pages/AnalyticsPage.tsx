import React, { useState, useEffect } from 'react';
import { 
  Download, Filter, ShieldCheck, TrendingUp, AlertTriangle, 
  Activity, RefreshCw, ChevronRight
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  BarChart, Bar,
  ScatterChart, Scatter, ZAxis
} from 'recharts';
import { analyticsService } from '../services/analyticsService';
import type { TrendDataPoint, UnitComparisonData, FactorData, ScatterDataPoint, TimePeriodData } from '../services/analyticsService';

export const AnalyticsPage: React.FC = () => {
  // Filters
  const [unitFilter, setUnitFilter] = useState('All Units');
  const [dateRange, setDateRange] = useState(30);
  const [metricFilter, setMetricFilter] = useState('Wellness');

  // Data state
  const [trendData, setTrendData] = useState<TrendDataPoint[]>([]);
  const [unitData, setUnitData] = useState<UnitComparisonData[]>([]);
  const [factorsData, setFactorsData] = useState<FactorData[]>([]);
  const [scatterData, setScatterData] = useState<ScatterDataPoint[]>([]);
  const [timeData, setTimeData] = useState<TimePeriodData[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock distribution
  const distributionData = [
    { name: 'Lower', value: 72, color: '#8BBB92' },
    { name: 'Moderate', value: 21, color: '#F59E0B' },
    { name: 'Elevated', value: 7, color: '#EF4444' },
  ];

  const alerts = [
    { id: 1, title: 'Rising workload', subtitle: 'Unit A workload indicator increased 14% over the selected period.', action: 'Review' },
    { id: 2, title: 'Fatigue trend', subtitle: 'Unit C fatigue indicator has increased over the past 7 days.', action: 'Review' },
    { id: 3, title: 'Improving trend', subtitle: 'Unit B shows an improving wellbeing trend.', action: 'View' }
  ];

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const [trends, units, factors, scatter, time] = await Promise.all([
        analyticsService.getTrendData(unitFilter, dateRange),
        analyticsService.getUnitComparison(),
        analyticsService.getFactorsData(),
        analyticsService.getScatterData(),
        analyticsService.getTimePeriodData()
      ]);
      setTrendData(trends);
      
      // Sort unit data based on metric filter
      const sortedUnits = [...units].sort((a, b) => {
        if (metricFilter === 'Wellness') return b.wellness - a.wellness;
        if (metricFilter === 'Workload') return b.workload - a.workload;
        return b.fatigue - a.fatigue;
      });
      setUnitData(sortedUnits);
      
      setFactorsData(factors);
      setScatterData(scatter);
      setTimeData(time);
      setLoading(false);
    };

    loadData();
  }, [unitFilter, dateRange, metricFilter]);

  const handleExport = () => {
    analyticsService.exportAnalytics(unitFilter, dateRange);
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Privacy Notice */}
      <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 p-3 rounded-lg text-slate-600 shadow-sm">
        <ShieldCheck size={18} className="mt-0.5 text-secondary-teal shrink-0" />
        <div>
          <p className="font-bold text-slate-800 text-sm">Privacy-first analytics</p>
          <p className="text-xs mt-0.5">
            Analytics shown here are aggregated to support organizational welfare planning.
          </p>
        </div>
      </div>

      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Wellness Analytics</h1>
          <p className="text-slate-500 mt-1">Understand organizational wellbeing patterns over time</p>
          <span className="inline-block mt-2 text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded font-medium border border-slate-200">
            Prototype analytics
          </span>
        </div>
        
        <div className="flex flex-wrap items-center gap-3">
          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={unitFilter}
            onChange={(e) => setUnitFilter(e.target.value)}
          >
            <option>All Units</option>
            <option>Unit A</option>
            <option>Unit B</option>
            <option>Unit C</option>
            <option>Unit D</option>
          </select>

          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={dateRange}
            onChange={(e) => setDateRange(Number(e.target.value))}
          >
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>

          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-primary-navy text-white rounded-lg hover:bg-primary-navy/90 transition-colors shadow-sm font-medium text-sm"
          >
            <Download size={16} /> Export Report
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Overall Wellness Trend</p>
          <p className="text-2xl font-bold text-positive flex items-center gap-2">
            Improving <TrendingUp size={20} />
          </p>
          <p className="text-xs text-slate-400 mt-2">vs previous period</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Workload Indicator</p>
          <p className="text-2xl font-bold text-attention-700 flex items-center gap-2">
            +8% <Activity size={20} />
          </p>
          <p className="text-xs text-slate-400 mt-2">vs previous period</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Fatigue Indicator</p>
          <p className="text-2xl font-bold text-attention-700 flex items-center gap-2">
            +5% <AlertTriangle size={20} />
          </p>
          <p className="text-xs text-slate-400 mt-2">vs previous period</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Follow-ups</p>
          <p className="text-2xl font-bold text-primary-navy flex items-center gap-2">
            34 <RefreshCw size={20} />
          </p>
          <p className="text-xs text-slate-400 mt-2">vs previous period</p>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400">Loading analytics...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Trend Chart */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[400px]">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg font-bold text-primary-navy">Wellness Indicators</h3>
                <p className="text-sm text-slate-500">Aggregate observed trends</p>
              </div>
            </div>
            
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    labelStyle={{ color: '#64748B', marginBottom: '8px', fontSize: '12px', fontWeight: 'bold' }}
                    formatter={(value: any, name: any) => [`${Math.round(value)}`, name]}
                  />
                  <Line type="monotone" name="Wellness" dataKey="wellness" stroke="#8BBB92" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                  <Line type="monotone" name="Workload" dataKey="workload" stroke="#F59E0B" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                  <Line type="monotone" name="Fatigue" dataKey="fatigue" stroke="#12544F" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center gap-6 mt-4">
              <LegendItem color="#8BBB92" label="Wellness" />
              <LegendItem color="#F59E0B" label="Workload" />
              <LegendItem color="#12544F" label="Fatigue" />
            </div>
          </div>

          {/* Wellness Distribution Donut */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[400px]">
            <h3 className="text-lg font-bold text-primary-navy mb-1">Current Welfare Indicator Distribution</h3>
            <p className="text-sm text-slate-500 mb-4">Aggregate prototype data</p>
            
            <div className="flex-1 w-full min-h-0 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    stroke="none"
                  >
                    {distributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    formatter={(value: any) => [`${value}%`, 'Personnel']}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="flex justify-center gap-6 mt-2">
              {distributionData.map(item => (
                <LegendItem key={item.name} color={item.color} label={item.name} />
              ))}
            </div>
          </div>

          {/* Unit Comparison */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[350px]">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg font-bold text-primary-navy">Unit Wellness Comparison</h3>
                <p className="text-sm text-slate-500">Aggregate comparison only</p>
              </div>
              <select 
                className="px-2 py-1 bg-slate-50 border border-slate-200 rounded text-xs font-medium text-slate-600 focus:outline-none"
                value={metricFilter}
                onChange={e => setMetricFilter(e.target.value)}
              >
                <option>Wellness</option>
                <option>Workload</option>
                <option>Fatigue</option>
              </select>
            </div>
            
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={unitData} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="unit" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#475569', fontWeight: 500 }} width={60} />
                  <RechartsTooltip 
                    cursor={{ fill: '#F1F5F9' }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Bar dataKey={metricFilter.toLowerCase()} fill="#092328" radius={[0, 4, 4, 0]} barSize={20}>
                    {unitData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#092328' : index === 1 ? '#12544F' : index === 2 ? '#447D78' : '#8BBB92'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Workload vs Fatigue Scatter */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[350px]">
            <h3 className="text-lg font-bold text-primary-navy mb-1">Workload & Fatigue Relationship</h3>
            <p className="text-sm text-slate-500 mb-4">Aggregate pattern — not causal evidence</p>
            
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis type="number" dataKey="workload" name="Workload Indicator" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis type="number" dataKey="fatigue" name="Fatigue Indicator" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <ZAxis type="category" dataKey="unit" name="Unit" />
                  <RechartsTooltip 
                    cursor={{ strokeDasharray: '3 3' }} 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Scatter name="Aggregate Units" data={scatterData} fill="#12544F" opacity={0.6} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Contributing Factors */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[350px]">
            <h3 className="text-lg font-bold text-primary-navy mb-1">Common Contributing Factors</h3>
            <p className="text-sm text-slate-500 mb-4">Prototype aggregated explanation</p>
            
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={factorsData} layout="vertical" margin={{ top: 0, right: 20, left: 30, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#475569', fontWeight: 500 }} width={90} />
                  <RechartsTooltip 
                    cursor={{ fill: '#F1F5F9' }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Bar dataKey="value" fill="#F59E0B" radius={[0, 4, 4, 0]} barSize={16} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Time Period Analysis */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[350px]">
            <h3 className="text-lg font-bold text-primary-navy mb-1">Time Period Analysis</h3>
            <p className="text-sm text-slate-500 mb-4">Weekly distribution</p>
            
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <RechartsTooltip 
                    cursor={{ fill: '#F1F5F9' }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Bar dataKey="workload" name="Workload" fill="#092328" radius={[4, 4, 0, 0]} barSize={12} />
                  <Bar dataKey="fatigue" name="Fatigue" fill="#12544F" radius={[4, 4, 0, 0]} barSize={12} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center gap-6 mt-4">
              <LegendItem color="#092328" label="Workload" />
              <LegendItem color="#12544F" label="Fatigue" />
            </div>
          </div>

          {/* Emerging Trends & AI Panel */}
          <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
              <div className="p-5 border-b border-slate-100 bg-slate-50/50">
                <h3 className="font-bold text-primary-navy">Emerging Trends</h3>
              </div>
              <div className="p-5 space-y-4 flex-1">
                {alerts.map(alert => (
                  <div key={alert.id} className="p-4 rounded-xl border border-slate-100 bg-white shadow-sm hover:shadow-md transition-shadow group">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h4 className="font-bold text-slate-800 text-sm">{alert.title}</h4>
                        <p className="text-sm text-slate-600 mt-1 mb-3">{alert.subtitle}</p>
                        <button className="text-sm font-bold text-secondary-teal hover:text-primary-navy flex items-center gap-1 transition-colors">
                          [ {alert.action} ] <ChevronRight size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-primary-navy to-secondary-teal rounded-xl p-6 text-white shadow-lg relative overflow-hidden flex flex-col justify-center">
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
              <div className="relative z-10 text-center">
                <h3 className="text-xl font-bold mb-3 flex justify-center items-center gap-2">
                  ✨ AI Insights
                </h3>
                <p className="text-white/80 text-sm mb-6 leading-relaxed italic">
                  "Wellness indicators are showing an increasing trend in selected units."
                </p>
                <div className="inline-block bg-black/20 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider mb-6">
                  Confidence: Prototype
                </div>
                <p className="text-xs text-white/60">
                  AI insights will dynamically generate risk trends, personal baseline deviations, and SHAP explanations when the predictive model is connected.
                </p>
              </div>
            </div>

          </div>

        </div>
      )}
    </div>
  );
};

const LegendItem = ({ color, label }: { color: string, label: string }) => (
  <div className="flex items-center gap-2">
    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }}></div>
    <span className="text-xs font-medium text-slate-600">{label}</span>
  </div>
);
