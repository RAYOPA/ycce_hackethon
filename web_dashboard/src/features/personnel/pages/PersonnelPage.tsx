import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, Download, Filter, X } from 'lucide-react';
import { personnelService } from '../services/personnelService';
import type { Personnel } from '../models/personnel';
import { format } from 'date-fns';

export const PersonnelPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialFollowUp = searchParams.get('followUp') || 'All';
  const initialTrend = searchParams.get('trend') || 'All';

  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [unitFilter, setUnitFilter] = useState('All Units');
  const [trendFilter, setTrendFilter] = useState(initialTrend);
  const [followUpFilter, setFollowUpFilter] = useState(initialFollowUp);
  const [dateFilter, setDateFilter] = useState('Last 30 days');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await personnelService.getPersonnel({
        unit: unitFilter,
        trend: trendFilter,
        followUp: followUpFilter,
        searchQuery
      });
      setPersonnel(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [unitFilter, trendFilter, followUpFilter, searchQuery]);

  const clearFilters = () => {
    setSearchQuery('');
    setUnitFilter('All Units');
    setTrendFilter('All');
    setFollowUpFilter('All');
    setDateFilter('Last 30 days');
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Personnel</h1>
          <p className="text-slate-500 mt-1">Review authorized personnel wellbeing information</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            <Filter size={18} />
            <span>Filters</span>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-navy text-white rounded-lg hover:bg-primary-navy/90 transition-colors">
            <Download size={18} />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 mb-6 flex flex-col md:flex-row gap-4 shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search by Personnel ID..."
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal focus:border-transparent"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-3">
          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={unitFilter}
            onChange={e => setUnitFilter(e.target.value)}
          >
            <option>All Units</option>
            <option>Unit A</option>
            <option>Unit B</option>
            <option>Unit C</option>
            <option>Unit D</option>
          </select>
          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={trendFilter}
            onChange={e => setTrendFilter(e.target.value)}
          >
            <option>All</option>
            <option>Improving</option>
            <option>Stable</option>
            <option>Rising</option>
          </select>
          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={followUpFilter}
            onChange={e => setFollowUpFilter(e.target.value)}
          >
            <option>All</option>
            <option>Required</option>
            <option>Not Required</option>
            <option>Completed</option>
          </select>
          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={dateFilter}
            onChange={e => setDateFilter(e.target.value)}
          >
            <option>Last 7 days</option>
            <option>Last 30 days</option>
            <option>Last 90 days</option>
          </select>
          <button 
            onClick={clearFilters}
            className="flex items-center gap-1 text-slate-500 hover:text-slate-800 px-2"
          >
            <X size={16} />
            <span className="text-sm font-medium">Clear</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-sm text-slate-500">
                <th className="px-6 py-4 font-medium">Personnel ID</th>
                <th className="px-6 py-4 font-medium">Unit</th>
                <th className="px-6 py-4 font-medium">Last Check-in</th>
                <th className="px-6 py-4 font-medium">Wellness Trend</th>
                <th className="px-6 py-4 font-medium">Follow-up</th>
                <th className="px-6 py-4 font-medium">Last Updated</th>
                <th className="px-6 py-4 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-6 py-4"><div className="h-6 bg-slate-200 rounded-full w-24"></div></td>
                    <td className="px-6 py-4"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-6 py-4"><div className="h-8 bg-slate-200 rounded w-16"></div></td>
                  </tr>
                ))
              ) : personnel.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    <p className="text-lg font-medium text-slate-700 mb-1">No personnel found</p>
                    <p className="mb-4">Try changing your search or filters.</p>
                    <button 
                      onClick={clearFilters}
                      className="text-secondary-teal font-medium hover:underline"
                    >
                      Clear Filters
                    </button>
                  </td>
                </tr>
              ) : (
                personnel.map(p => (
                  <tr 
                    key={p.id} 
                    onClick={() => navigate(`/personnel/${p.id}`)}
                    className="hover:bg-slate-50 transition-colors cursor-pointer"
                  >
                    <td className="px-6 py-4 font-medium text-slate-900">{p.personnelId}</td>
                    <td className="px-6 py-4 text-slate-600">{p.unitId}</td>
                    <td className="px-6 py-4 text-slate-600">{format(new Date(p.lastCheckIn), 'MMM d, yyyy')}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        p.wellnessTrend === 'Improving' ? 'bg-positive-light text-secondary-teal' :
                        p.wellnessTrend === 'Rising' ? 'bg-attention-light text-attention-700' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        {p.wellnessTrend}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        p.followUpStatus === 'Required' ? 'bg-amber-100 text-amber-700' :
                        p.followUpStatus === 'Completed' ? 'bg-slate-100 text-slate-600' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        {p.followUpStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{format(new Date(p.lastUpdated), 'MMM d, yyyy')}</td>
                    <td className="px-6 py-4">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/personnel/${p.id}`);
                        }}
                        className="text-secondary-teal font-medium hover:text-secondary-teal/80 transition-colors"
                      >
                        [ View ]
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
