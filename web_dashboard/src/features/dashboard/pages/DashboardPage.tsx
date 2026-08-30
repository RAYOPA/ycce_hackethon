import React, { useState } from 'react';
import { 
  Users, Activity, AlertCircle, TrendingUp, 
  ChevronRight, Calendar, ArrowUpRight, ArrowDownRight,
  ShieldCheck, ShieldAlert, FileText, Bell
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  BarChart, Bar
} from 'recharts';
import { useNavigate } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [dateRange, setDateRange] = useState(30);

  // Mock data for the line chart (Wellness Trend)
  const trendData = Array.from({ length: 12 }, (_, i) => ({
    date: `Week ${i + 1}`,
    stress: 20 + Math.random() * 15,
    fatigue: 15 + Math.random() * 20,
    workload: 30 + Math.random() * 25,
  }));

  // Mock data for Risk Distribution (Donut Chart)
  const distributionData = [
    { name: 'Lower', value: 72, color: '#8BBB92' },
    { name: 'Moderate', value: 21, color: '#F59E0B' },
    { name: 'Elevated', value: 7, color: '#EF4444' },
  ];

  // Mock data for Contributing Factors (Horizontal Bar)
  const factorsData = [
    { name: 'Sleep pattern', value: 85 },
    { name: 'Workload', value: 65 },
    { name: 'Night duty', value: 45 },
    { name: 'Consecutive duty', value: 30 },
    { name: 'Leave gap', value: 20 },
  ];

  const alerts = [
    {
      id: 1,
      title: 'Rising workload trend',
      subtitle: 'Unit A • +14% over previous period',
      type: 'warning',
      action: 'Review',
      link: '/personnel'
    },
    {
      id: 2,
      title: 'Follow-up due',
      subtitle: '3 welfare cases pending review',
      type: 'info',
      action: 'View',
      link: '/interventions'
    },
    {
      id: 3,
      title: 'Increasing fatigue indicators',
      subtitle: 'Unit C',
      type: 'critical',
      action: 'Review',
      link: '/personnel'
    }
  ];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Privacy Notice Banner */}
      <div className="bg-gradient-to-r from-primary-navy to-secondary-teal text-white rounded-xl p-4 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <ShieldCheck size={24} className="text-positive-light" />
          <div>
            <h3 className="font-bold">🔒 Welfare-first system</h3>
            <p className="text-white/80 text-sm">Information is used to support personnel welfare. Individual information is restricted to authorized users.</p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-2">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Wellness Overview</h1>
          <p className="text-slate-500 mt-1">Personnel wellbeing and welfare indicators</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-white border border-slate-200 rounded-lg p-1 shadow-sm">
            {[7, 30, 90].map(days => (
              <button
                key={days}
                onClick={() => setDateRange(days)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  dateRange === days ? 'bg-primary-navy text-white shadow' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                {days} Days
              </button>
            ))}
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg shadow-sm hover:bg-slate-50 transition-colors">
            <Calendar size={18} />
            <span className="font-medium text-sm">Report</span>
          </button>
        </div>
      </div>

      {/* Top Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard 
          title="Total Personnel" 
          value="1,240" 
          icon={<Users size={20} className="text-secondary-teal" />}
          trend="+2 this month"
          trendUp={true}
        />
        <SummaryCard 
          title="Elevated Indicators" 
          value="82" 
          icon={<Activity size={20} className="text-attention-700" />}
          trend="-4 from last week"
          trendUp={false}
          valueColor="text-attention-700"
        />
        <SummaryCard 
          title="Follow-ups Due" 
          value="34" 
          icon={<AlertCircle size={20} className="text-primary-navy" />}
          trend="12 due today"
          trendUp={true}
        />
        <SummaryCard 
          title="Rising Trends" 
          value="21" 
          icon={<TrendingUp size={20} className="text-critical" />}
          trend="+3 from last week"
          trendUp={true}
          valueColor="text-critical"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Chart Section */}
        <div className="lg:col-span-2 space-y-6">
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[400px]">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-lg font-bold text-primary-navy">Wellness Trend</h3>
                <p className="text-sm text-slate-500">Observed aggregate welfare indicators over time</p>
              </div>
              <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded font-medium">Demo data</span>
            </div>
            
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    itemStyle={{ fontWeight: 'bold', fontSize: '14px' }}
                    labelStyle={{ color: '#64748B', marginBottom: '8px', fontSize: '12px', textTransform: 'uppercase' }}
                  />
                  <Line type="monotone" name="Stress Indicator" dataKey="stress" stroke="#092328" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                  <Line type="monotone" name="Fatigue Indicator" dataKey="fatigue" stroke="#12544F" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                  <Line type="monotone" name="Workload Trend" dataKey="workload" stroke="#F59E0B" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="flex items-center justify-center gap-6 mt-4">
              <LegendItem color="#092328" label="Stress Indicator" />
              <LegendItem color="#12544F" label="Fatigue Indicator" />
              <LegendItem color="#F59E0B" label="Workload Trend" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Risk Distribution Donut */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[320px]">
              <h3 className="text-lg font-bold text-primary-navy mb-1">Current Indicator Distribution</h3>
              <p className="text-sm text-slate-500 mb-4">Welfare indicator levels across organization</p>
              
              <div className="flex-1 w-full min-h-0 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={distributionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
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
                {/* Center text for donut */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-3xl font-bold text-primary-navy">100%</span>
                  <span className="text-xs text-slate-500 font-medium uppercase">Total</span>
                </div>
              </div>
              
              <div className="flex justify-center gap-4 mt-2">
                {distributionData.map(item => (
                  <div key={item.name} className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs font-medium text-slate-600">{item.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Contributing Factors Bar Chart */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col h-[320px]">
              <h3 className="text-lg font-bold text-primary-navy mb-1">Common Contributing Factors</h3>
              <p className="text-sm text-slate-500 mb-4">Aggregated prototype indicators</p>
              
              <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={factorsData} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#475569', fontWeight: 500 }} width={90} />
                    <RechartsTooltip 
                      cursor={{ fill: '#F1F5F9' }}
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value: any) => [`${value} occurrences`, 'Frequency']}
                    />
                    <Bar dataKey="value" fill="#12544F" radius={[0, 4, 4, 0]} barSize={16}>
                      {factorsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#092328' : index === 1 ? '#12544F' : index === 2 ? '#447D78' : '#8BBB92'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          
          {/* Action Panel */}
          <div className="bg-primary-navy rounded-xl p-6 text-white shadow-lg relative overflow-hidden">
            {/* Decorative background element */}
            <div className="absolute -right-10 -top-10 w-40 h-40 bg-secondary-teal/30 rounded-full blur-3xl"></div>
            
            <div className="relative z-10">
              <h3 className="text-xl font-bold mb-2">AI-Powered Insights</h3>
              <p className="text-white/80 text-sm mb-6 leading-relaxed">
                Our prototype models continuously analyze aggregate data to surface emerging organizational wellness patterns without compromising individual privacy.
              </p>
              <button 
                onClick={() => navigate('/personnel')}
                className="w-full py-3 bg-secondary-teal hover:bg-secondary-teal/80 text-white rounded-lg font-bold transition-colors flex items-center justify-center gap-2"
              >
                <FileText size={18} />
                View Full Directory
              </button>
            </div>
          </div>

          {/* Welfare Alerts */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[525px]">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <h3 className="font-bold text-primary-navy flex items-center gap-2">
                <Bell size={18} className="text-attention-700" />
                Attention Required
              </h3>
              <span className="bg-slate-200 text-slate-700 text-xs px-2 py-0.5 rounded-full font-bold">3</span>
            </div>
            
            <div className="p-4 space-y-4 overflow-y-auto flex-1">
              {alerts.map(alert => (
                <div key={alert.id} className="p-4 rounded-xl border border-slate-100 bg-white shadow-sm hover:shadow-md transition-shadow group">
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 w-2.5 h-2.5 rounded-full shrink-0 ${
                      alert.type === 'critical' ? 'bg-critical' : 
                      alert.type === 'warning' ? 'bg-attention' : 'bg-primary-navy'
                    }`} />
                    <div className="flex-1">
                      <h4 className="font-bold text-slate-800 text-sm">{alert.title}</h4>
                      <p className="text-xs text-slate-500 mt-1 mb-3">{alert.subtitle}</p>
                      <button 
                        onClick={() => navigate(alert.link)}
                        className="text-xs font-bold text-secondary-teal hover:text-primary-navy flex items-center gap-1 transition-colors"
                      >
                        [ {alert.action} ] <ChevronRight size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-3 border-t border-slate-100 bg-slate-50 text-center">
              <button className="text-xs font-bold text-slate-500 hover:text-slate-800 uppercase tracking-wider">
                View All Alerts
              </button>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

const SummaryCard = ({ title, value, icon, trend, trendUp, valueColor = 'text-primary-navy' }: any) => (
  <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm relative group overflow-hidden">
    <div className="absolute top-0 right-0 w-24 h-24 bg-slate-50 rounded-bl-full -z-0 transition-transform group-hover:scale-110"></div>
    <div className="relative z-10">
      <div className="flex justify-between items-start mb-2">
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <div className="p-2 bg-slate-50 rounded-lg shadow-sm border border-slate-100">
          {icon}
        </div>
      </div>
      <p className={`text-3xl font-bold mb-2 ${valueColor}`}>{value}</p>
      <div className="flex items-center gap-1.5 mt-auto">
        {trendUp ? (
          <ArrowUpRight size={14} className="text-attention-700" />
        ) : (
          <ArrowDownRight size={14} className="text-positive" />
        )}
        <span className={`text-xs font-medium ${trendUp ? 'text-attention-700' : 'text-positive'}`}>
          {trend}
        </span>
      </div>
    </div>
  </div>
);

const LegendItem = ({ color, label }: { color: string, label: string }) => (
  <div className="flex items-center gap-2">
    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }}></div>
    <span className="text-xs font-medium text-slate-600">{label}</span>
  </div>
);
