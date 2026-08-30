import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { Calendar, Filter, AlertTriangle, Clock, TrendingUp } from 'lucide-react';

const mockTrendData = [
  { month: 'Jan', avgHours: 42, consecutiveDays: 4, nightShifts: 2 },
  { month: 'Feb', avgHours: 45, consecutiveDays: 5, nightShifts: 3 },
  { month: 'Mar', avgHours: 48, consecutiveDays: 6, nightShifts: 4 },
  { month: 'Apr', avgHours: 52, consecutiveDays: 7, nightShifts: 6 },
  { month: 'May', avgHours: 50, consecutiveDays: 5, nightShifts: 4 },
  { month: 'Jun', avgHours: 54, consecutiveDays: 8, nightShifts: 7 },
];

const mockUnitData = [
  { unit: 'Unit A', avgHours: 45, over50: 12 },
  { unit: 'Unit B', avgHours: 52, over50: 28 },
  { unit: 'Unit C', avgHours: 48, over50: 18 },
  { unit: 'Unit D', avgHours: 41, over50: 5 },
];

export const WorkloadAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState('6M');

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Workload Analytics</h1>
          <p className="text-slate-500 mt-1">Aggregate workload tracking to support organizational planning</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50">
            <Filter size={16} /> Filter Units
          </button>
          <div className="flex bg-white border border-slate-200 rounded-lg p-1 shadow-sm">
            {['1M', '3M', '6M', '1Y'].map(p => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1 text-sm font-medium rounded-md ${
                  period === p ? 'bg-slate-100 text-primary-navy' : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Avg Weekly Hours</p>
              <p className="text-3xl font-black text-slate-800">48.5<span className="text-sm font-normal text-slate-500 ml-1">hrs</span></p>
            </div>
            <div className="p-2 bg-slate-50 rounded-lg">
              <Clock className="text-secondary-teal" size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-xs font-medium text-attention-700">
            <TrendingUp size={14} /> +4.2% from last period
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Personnel &gt;50hrs/wk</p>
              <p className="text-3xl font-black text-slate-800">63</p>
            </div>
            <div className="p-2 bg-amber-50 rounded-lg">
              <AlertTriangle className="text-amber-500" size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-xs font-medium text-amber-600">
            18% of workforce
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500 mb-1">Avg Consecutive Days</p>
              <p className="text-3xl font-black text-slate-800">5.8<span className="text-sm font-normal text-slate-500 ml-1">days</span></p>
            </div>
            <div className="p-2 bg-slate-50 rounded-lg">
              <Calendar className="text-primary-navy" size={20} />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-xs font-medium text-slate-500">
            Stable trend
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Trend Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-6">Aggregate Workload Trends</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAvg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0B4D56" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0B4D56" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend iconType="circle" />
                <Area type="monotone" name="Avg Weekly Hours" dataKey="avgHours" stroke="#0B4D56" strokeWidth={2} fillOpacity={1} fill="url(#colorAvg)" />
                <Area type="monotone" name="Consecutive Days" dataKey="consecutiveDays" stroke="#16A34A" strokeWidth={2} fill="none" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Unit Comparison Chart */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-6">Unit Workload Comparison</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockUnitData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="unit" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                />
                <Legend iconType="circle" />
                <Bar name="Avg Hours" dataKey="avgHours" fill="#1C2E4A" radius={[4, 4, 0, 0]} barSize={30} />
                <Bar name="Personnel >50hrs" dataKey="over50" fill="#F59E0B" radius={[4, 4, 0, 0]} barSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
};
