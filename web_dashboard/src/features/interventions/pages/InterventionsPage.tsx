import React, { useState, useEffect } from 'react';
import { Search, Download, Filter, X, Plus, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { interventionService } from '../services/interventionService';
import type { Intervention, InterventionStatus } from '../models/intervention';
import { format, isToday } from 'date-fns';
import { CreateInterventionModal } from '../components/CreateInterventionModal';
import { InterventionDetailModal } from '../components/InterventionDetailModal';

export const InterventionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Modals
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [selectedIntervention, setSelectedIntervention] = useState<Intervention | null>(null);

  // Filters
  const [activeTab, setActiveTab] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [unitFilter, setUnitFilter] = useState('All Units');
  const [actionTypeFilter, setActionTypeFilter] = useState('All');

  // Summary counts
  const [counts, setCounts] = useState({ dueToday: 0, upcoming: 0, inProgress: 0, completed: 0 });

  const mockUserRole: string = 'Welfare Officer';

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await interventionService.getInterventions({
        statusTab: activeTab,
        unit: unitFilter,
        actionType: actionTypeFilter,
        searchQuery
      });
      setInterventions(data);

      // Re-calculate counts (without filters applied, just raw numbers for tabs)
      const allData = await interventionService.getInterventions();
      setCounts({
        dueToday: allData.filter(i => i.status === 'Due').length,
        upcoming: allData.filter(i => i.status === 'Upcoming' || i.status === 'Rescheduled').length,
        inProgress: allData.filter(i => i.status === 'In Progress').length,
        completed: allData.filter(i => i.status === 'Completed').length,
      });

      if (selectedIntervention) {
        const updated = await interventionService.getInterventionById(selectedIntervention.id);
        if (updated) setSelectedIntervention(updated);
      }

    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mockUserRole !== 'Commander') {
      loadData();
    }
  }, [activeTab, unitFilter, actionTypeFilter, searchQuery, mockUserRole]);

  const clearFilters = () => {
    setSearchQuery('');
    setUnitFilter('All Units');
    setActionTypeFilter('All');
  };

  const getStatusColor = (s: string) => {
    switch(s) {
      case 'Due': return 'bg-attention-100 text-attention-700';
      case 'Upcoming': return 'bg-positive-light text-secondary-teal';
      case 'In Progress': return 'bg-blue-100 text-blue-700';
      case 'Completed': return 'bg-slate-100 text-slate-600';
      case 'Rescheduled': return 'bg-purple-100 text-purple-700';
      default: return 'bg-slate-100 text-slate-600';
    }
  };

  if (mockUserRole === 'Commander') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
        <ShieldAlert size={64} className="text-attention mb-6" />
        <h1 className="text-3xl font-bold text-primary-navy mb-2">Restricted View</h1>
        <p className="text-slate-600 mb-8 max-w-md">
          Individual welfare actions are restricted to authorized welfare personnel.
        </p>
        <button 
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-primary-navy text-white rounded-lg hover:bg-primary-navy/90 font-medium"
        >
          Return to Overview
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto flex flex-col h-full">
      {/* Privacy Notice */}
      <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 p-3 rounded-lg text-slate-600 mb-6">
        <ShieldCheck size={18} className="mt-0.5 text-secondary-teal shrink-0" />
        <div>
          <p className="font-bold text-slate-800 text-sm">Authorized Welfare Access</p>
          <p className="text-xs mt-0.5">
            Individual welfare information is available only to authorized welfare personnel.
          </p>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Follow-ups & Interventions</h1>
          <p className="text-slate-500 mt-1">Manage welfare support actions and follow-up activities</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white text-slate-700 rounded-lg hover:bg-slate-50 transition-colors">
            <Filter size={18} />
            <span>Filter</span>
          </button>
          <button 
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-secondary-teal text-white rounded-lg hover:bg-secondary-teal/90 transition-colors shadow-sm"
          >
            <Plus size={18} />
            <span className="font-medium">New Intervention</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 w-2 h-full bg-attention"></div>
          <p className="text-sm text-slate-500 font-medium">Due Today</p>
          <p className="text-3xl font-bold text-primary-navy mt-1">{counts.dueToday}</p>
          <p className="text-xs text-slate-400 mt-1">Demo data</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 w-2 h-full bg-positive"></div>
          <p className="text-sm text-slate-500 font-medium">Upcoming</p>
          <p className="text-3xl font-bold text-primary-navy mt-1">{counts.upcoming}</p>
          <p className="text-xs text-slate-400 mt-1">Demo data</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 w-2 h-full bg-blue-500"></div>
          <p className="text-sm text-slate-500 font-medium">In Progress</p>
          <p className="text-3xl font-bold text-primary-navy mt-1">{counts.inProgress}</p>
          <p className="text-xs text-slate-400 mt-1">Demo data</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 w-2 h-full bg-slate-300"></div>
          <p className="text-sm text-slate-500 font-medium">Completed</p>
          <p className="text-3xl font-bold text-primary-navy mt-1">{counts.completed}</p>
          <p className="text-xs text-slate-400 mt-1">Demo data</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 mb-6 space-x-6">
        {['All', 'Due Today', 'Upcoming', 'In Progress', 'Completed'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 font-medium text-sm transition-colors relative ${
              activeTab === tab ? 'text-secondary-teal' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab}
            {activeTab === tab && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-secondary-teal rounded-t-md"></span>
            )}
          </button>
        ))}
      </div>

      {/* Filters & Search */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 mb-6 flex flex-col md:flex-row gap-4 shadow-sm shrink-0">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search Personnel ID..."
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal focus:border-transparent text-sm"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-3">
          <select 
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
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
            className="px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
            value={actionTypeFilter}
            onChange={e => setActionTypeFilter(e.target.value)}
          >
            <option>All</option>
            <option>Workload Review</option>
            <option>Recovery Support</option>
            <option>Wellness Follow-up</option>
            <option>General Welfare Support</option>
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
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 overflow-hidden flex flex-col">
        <div className="overflow-auto flex-1">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-slate-50 z-10">
              <tr className="border-b border-slate-200 text-sm text-slate-500">
                <th className="px-6 py-3 font-medium">Personnel ID</th>
                <th className="px-6 py-3 font-medium">Unit</th>
                <th className="px-6 py-3 font-medium">Action</th>
                <th className="px-6 py-3 font-medium">Assigned</th>
                <th className="px-6 py-3 font-medium">Due Date</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-6 py-4"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
                    <td className="px-6 py-4"><div className="h-8 bg-slate-200 rounded w-16"></div></td>
                  </tr>
                ))
              ) : interventions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-16 text-center text-slate-500">
                    <p className="text-lg font-medium text-slate-700 mb-1">No follow-ups found</p>
                    <p className="mb-4">Try changing your filters or tabs.</p>
                    <button 
                      onClick={clearFilters}
                      className="text-secondary-teal font-medium hover:underline"
                    >
                      Clear Filters
                    </button>
                  </td>
                </tr>
              ) : (
                interventions.map(i => (
                  <tr key={i.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3.5 font-medium text-slate-900">{i.personnelId}</td>
                    <td className="px-6 py-3.5 text-slate-600">{i.unitId}</td>
                    <td className="px-6 py-3.5 text-slate-800 font-medium">{i.actionType}</td>
                    <td className="px-6 py-3.5 text-slate-600">{i.assignedOfficer}</td>
                    <td className="px-6 py-3.5 text-slate-600 font-medium">
                      {isToday(new Date(i.followUpDate)) ? 'Today' : format(new Date(i.followUpDate), 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-3.5">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(i.status)}`}>
                        {i.status}
                      </span>
                    </td>
                    <td className="px-6 py-3.5">
                      <button 
                        onClick={() => setSelectedIntervention(i)}
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

      <CreateInterventionModal 
        isOpen={createModalOpen} 
        onClose={() => setCreateModalOpen(false)} 
        onSuccess={loadData}
      />

      <InterventionDetailModal 
        isOpen={!!selectedIntervention}
        intervention={selectedIntervention}
        onClose={() => setSelectedIntervention(null)}
        onUpdate={loadData}
      />
    </div>
  );
};
