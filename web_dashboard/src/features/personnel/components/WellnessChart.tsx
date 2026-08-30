import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface WellnessChartProps {
  title: string;
  data: number[];
  color: string;
  domain?: [number, number];
}

export const WellnessChart: React.FC<WellnessChartProps> = ({ title, data, color, domain = [0, 10] }) => {
  // Mock data mapping
  const chartData = data.map((val, idx) => ({
    day: `D-${data.length - idx}`,
    value: val.toFixed(1)
  }));

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
      <h3 className="text-lg font-bold text-primary-navy mb-6">{title}</h3>
      <div className="h-48 w-full mt-auto">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
            <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} minTickGap={20} />
            <YAxis domain={domain} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              itemStyle={{ color: '#0F172A', fontWeight: 'bold' }}
              labelStyle={{ color: '#64748B', marginBottom: '4px' }}
              formatter={(value: any) => [value, 'Value']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={color} 
              strokeWidth={3} 
              dot={false}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
