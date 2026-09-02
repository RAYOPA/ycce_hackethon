import React, { useState, useEffect } from 'react';
import { 
  Users, Activity, AlertCircle, TrendingUp, 
  ChevronRight, Calendar, ArrowUpRight, ArrowDownRight,
  FileText, Bell, CheckCircle, Loader2
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../../../utils/api';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Overview');
  const [timeRange, setTimeRange] = useState('1M');
  const [loading, setLoading] = useState(true);
  
  const [dashboardData, setDashboardData] = useState<any>({
    totalPersonnel: 0,
    metrics: { elevatedCases: 0, followUps: 0, risingTrends: 0, cleared: 0 },
    riskFactors: [],
    trendData: []
  });

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        // We'll calculate a 'start_date' based on timeRange if we want, but for simplicity we'll just hit the endpoints
        // which default to the last 30 days if no date is provided.
        const resWellness = await fetchWithAuth(`/analytics/wellness`);
        
        let totalPersonnel = 0;
        let trendData: any[] = [];
        
        if (resWellness.ok) {
          const wellnessData = await resWellness.json();
          totalPersonnel = wellnessData.active_personnel_count || 0;
          
          if (!wellnessData.insufficient_cohort) {
             trendData = wellnessData.trend.map((t: any) => ({
                date: t.date,
                stress: (t.average_stress_score || 0) * 1000 // scaling for chart
             }));
          }
        }
        
        setDashboardData({
          totalPersonnel,
          metrics: { elevatedCases: 0, followUps: 0, risingTrends: 0, cleared: 0 },
          riskFactors: [],
          trendData
        });
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [timeRange]);

  const handleTabChange = (tab: string) => {
    if (tab === 'Personnel') navigate('/personnel');
    if (tab === 'Analytics') navigate('/analytics');
    setActiveTab(tab);
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Tabs */}
      <div className="flex items-center gap-3 mb-6">
        {['Overview', 'Personnel', 'Analytics'].map(tab => (
          <button
            key={tab}
            onClick={() => handleTabChange(tab)}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
              activeTab === tab 
                ? 'bg-gradient-to-r from-helios-purple/20 to-helios-pink/10 border border-helios-purple/30 text-white shadow-[0_0_15px_rgba(147,51,234,0.15)]' 
                : 'bg-helios-card border border-white/5 text-helios-muted hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column (Stats + AI Card) */}
        <div className="lg:col-span-4 space-y-6 flex flex-col">
          {/* Main Stat Card */}
          <div className="bg-gradient-to-br from-helios-card to-[#1a1a24] p-6 rounded-3xl border border-white/5 shadow-xl relative overflow-hidden flex-shrink-0">
            <div className="absolute top-0 right-0 w-32 h-32 bg-helios-purple/20 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none"></div>
            <div className="flex justify-between items-center mb-4 relative z-10">
              <h3 className="text-helios-muted font-medium">Total Personnel</h3>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-white/5 rounded-full text-xs text-white border border-white/10">30D</span>
                <button className="p-1.5 bg-white/5 rounded-full text-helios-muted hover:text-white border border-white/10">
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
            <h2 className="text-4xl font-bold text-white relative z-10">
              {loading ? <Loader2 className="animate-spin text-helios-purple" size={36} /> : dashboardData.totalPersonnel.toLocaleString()}
            </h2>
          </div>

          {/* AI Insights Card */}
          <div className="bg-gradient-to-b from-helios-card to-[#1a1a24] p-6 rounded-3xl border border-white/5 shadow-xl relative overflow-hidden flex-1 flex flex-col justify-center items-center text-center">
            <div className="absolute bottom-0 inset-x-0 h-48 bg-gradient-to-t from-helios-pink/20 to-transparent pointer-events-none"></div>
            <div className="absolute bottom-0 inset-x-0 h-24 bg-helios-pink/10 blur-2xl pointer-events-none"></div>
            
            <div className="relative z-10 flex flex-col items-center">
              <h3 className="text-xl font-bold text-white mb-3">Decisions Powered by Data</h3>
              <p className="text-helios-muted text-sm mb-6 leading-relaxed px-4">
                Move beyond guesswork with AI-driven welfare insights tailored to your personnel strategy.
              </p>
              <button className="px-6 py-2.5 bg-gradient-to-r from-helios-purple to-helios-pink rounded-full text-white font-medium text-sm shadow-[0_0_20px_rgba(219,39,119,0.4)] hover:shadow-[0_0_30px_rgba(219,39,119,0.6)] transition-all">
                Explore AI Insights
              </button>
            </div>
          </div>
        </div>

        {/* Middle Column (Watchlist / Factors) */}
        <div className="lg:col-span-4 bg-helios-card p-6 rounded-3xl border border-white/5 shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-white font-medium text-lg">Top Risk Factors</h3>
          </div>
          
          <div className="flex items-center gap-2 mb-6">
            <button className="px-4 py-1.5 bg-white/10 rounded-full text-xs font-medium text-white border border-white/5">Most Viewed</button>
            <button className="px-4 py-1.5 rounded-full text-xs font-medium text-helios-muted hover:bg-white/5 transition-colors">Rising</button>
            <button className="px-4 py-1.5 rounded-full text-xs font-medium text-helios-muted hover:bg-white/5 transition-colors">Stable</button>
          </div>

          <div className="space-y-4">
            {loading ? (
               <div className="flex justify-center p-6"><Loader2 className="animate-spin text-helios-purple" size={24} /></div>
            ) : dashboardData.riskFactors.map((factor: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between p-2 hover:bg-white/5 rounded-xl transition-colors cursor-pointer border-b border-white/5 pb-3">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-helios-muted text-xs border border-white/10">
                    <Activity size={14} />
                  </div>
                  <div>
                    <h4 className="text-white text-sm font-medium">{factor.name}</h4>
                    <p className="text-helios-muted text-xs mt-0.5">Freq: {factor.value}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white text-sm font-medium">{factor.value * 12}</p>
                  <p className="text-helios-green text-xs font-medium mt-0.5">{factor.trend}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column (Metrics Grid) */}
        <div className="lg:col-span-4 bg-helios-card p-6 rounded-3xl border border-white/5 shadow-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-white font-medium text-lg">Welfare Metrics</h3>
            <button className="px-4 py-1.5 border border-white/10 rounded-full text-xs text-white hover:bg-white/5 transition-colors flex items-center gap-1">
              See all <ArrowUpRight size={12} />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {loading ? (
              <div className="col-span-2 flex justify-center py-10"><Loader2 className="animate-spin text-helios-purple" size={24} /></div>
            ) : [
              { label: 'Elevated Cases', value: dashboardData.metrics.elevatedCases, trend: '+12.3%', color: 'text-helios-green', unit: 'Units: All' },
              { label: 'Follow-ups', value: dashboardData.metrics.followUps, trend: '+8.1%', color: 'text-helios-green', unit: 'Units: All' },
              { label: 'Rising Trends', value: dashboardData.metrics.risingTrends, trend: '-2.4%', color: 'text-red-400', unit: 'Units: All' },
              { label: 'Cleared', value: dashboardData.metrics.cleared, trend: '+15.2%', color: 'text-helios-green', unit: 'Units: All' },
            ].map((metric, idx) => (
              <div key={idx} className="bg-[#22222a] p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
                <h4 className="text-white text-lg font-bold">{metric.value}</h4>
                <div className="flex items-center gap-1 mt-1 mb-6">
                  <span className={`text-xs ${metric.color} font-medium`}>{metric.trend}</span>
                  <span className="text-xs text-helios-muted">({metric.label})</span>
                </div>
                <div className="flex items-center justify-between mt-auto">
                  <div className="w-6 h-6 rounded bg-white/10 flex items-center justify-center">
                    <Users size={12} className="text-white/70" />
                  </div>
                  <span className="text-xs text-helios-muted">{metric.unit}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Full Width Chart (Performance) */}
      <div className="bg-helios-card p-6 rounded-3xl border border-white/5 shadow-xl">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-white font-medium text-lg">Trend Performance</h3>
          <div className="flex items-center gap-2 bg-[#1a1a24] p-1 rounded-full border border-white/5">
            {['1D', '1W', '1M', '6M', '1Y'].map((t) => (
              <button
                key={t}
                onClick={() => setTimeRange(t)}
                className={`w-9 h-9 rounded-full text-xs font-medium flex items-center justify-center transition-all ${
                  t === timeRange 
                  ? 'bg-helios-purple/20 text-helios-primary border border-helios-purple/30' 
                  : 'text-helios-muted hover:text-white'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
        
        <div className="h-[300px] w-full relative">
          {loading && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-helios-card/50">
               <Loader2 className="animate-spin text-helios-purple" size={32} />
            </div>
          )}
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dashboardData.trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorStress" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#e9c0e9" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#e9c0e9" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#9ca3af' }} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#9ca3af' }} tickFormatter={(val) => `${val/1000}k`} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#2a2a35', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}
                itemStyle={{ color: '#fff', fontWeight: 'bold' }}
                labelStyle={{ color: '#9ca3af', marginBottom: '4px', fontSize: '12px' }}
              />
              <Line 
                type="monotone" 
                dataKey="stress" 
                stroke="#e9c0e9" 
                strokeWidth={3} 
                dot={false} 
                activeDot={{ r: 6, fill: '#e9c0e9', stroke: '#fff', strokeWidth: 2 }} 
                fillOpacity={1} 
                fill="url(#colorStress)" 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
