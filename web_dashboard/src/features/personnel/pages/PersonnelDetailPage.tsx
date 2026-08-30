import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, ShieldCheck, Activity, BarChart2, ShieldAlert } from 'lucide-react';
import { personnelService } from '../services/personnelService';
import type { Personnel } from '../models/personnel';
import { WellnessChart } from '../components/WellnessChart';
import { InterventionModal } from '../components/InterventionModal';

export const PersonnelDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [personnel, setPersonnel] = useState<Personnel | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(30);
  const [modalOpen, setModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Mocking the logged-in user role (for the "Commander Restriction" requirement)
  // In a real app this would come from an AuthContext
  const mockUserRole = 'Welfare Officer'; 

  useEffect(() => {
    const loadPersonnel = async () => {
      if (id) {
        setLoading(true);
        const data = await personnelService.getPersonnelById(id);
        setPersonnel(data || null);
        setLoading(false);
      }
    };
    loadPersonnel();
  }, [id]);

  const handleCreateIntervention = async (action: string, notes: string, date: string) => {
    if (personnel) {
      await personnelService.createIntervention(personnel.id, action, notes, date);
      setToastMessage('Intervention created successfully.');
      setTimeout(() => setToastMessage(null), 3000);
      
      // Reload personnel data to reflect changes
      const updated = await personnelService.getPersonnelById(personnel.id);
      setPersonnel(updated || null);
    }
  };

  if (mockUserRole === 'Commander') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
        <ShieldAlert size={64} className="text-attention mb-6" />
        <h1 className="text-3xl font-bold text-primary-navy mb-2">Restricted View</h1>
        <p className="text-slate-600 mb-8 max-w-md">
          Individual welfare information is limited to authorized welfare personnel.
        </p>
        <button 
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-primary-navy text-white rounded-lg hover:bg-primary-navy/90 font-medium"
        >
          Back to Overview
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6 animate-pulse">
        <div className="h-8 bg-slate-200 rounded w-48 mb-8"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="h-24 bg-slate-200 rounded-xl"></div>
          <div className="h-24 bg-slate-200 rounded-xl"></div>
          <div className="h-24 bg-slate-200 rounded-xl"></div>
          <div className="h-24 bg-slate-200 rounded-xl"></div>
        </div>
        <div className="h-64 bg-slate-200 rounded-xl"></div>
      </div>
    );
  }

  if (!personnel) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto text-center py-20">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Personnel not found</h2>
        <button onClick={() => navigate('/personnel')} className="text-secondary-teal hover:underline font-medium">
          Back to Personnel List
        </button>
      </div>
    );
  }

  // Filter history based on date range
  const historySlice = (arr: number[]) => arr.slice(-dateRange);

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 right-4 bg-primary-navy text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2 animate-in slide-in-from-top">
          <ShieldCheck size={20} className="text-positive" />
          <span className="font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={() => navigate('/personnel')}
          className="p-2 hover:bg-slate-100 rounded-full text-slate-600 transition-colors"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Personnel {personnel.personnelId}</h1>
          <p className="text-slate-500 mt-1">
            {personnel.unitId} • Last Check-in: Today
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <OverviewCard title="Latest Check-in" value="Today" />
        <OverviewCard 
          title="Wellness Trend" 
          value={personnel.wellnessTrend} 
          valueColor={
            personnel.wellnessTrend === 'Rising' ? 'text-attention-700' :
            personnel.wellnessTrend === 'Improving' ? 'text-secondary-teal' : 'text-slate-700'
          }
        />
        <OverviewCard title="Follow-up" value={personnel.followUpStatus} />
        <OverviewCard title="Data Status" value="Up to date" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Left Column (Charts & Baseline) */}
        <div className="lg:col-span-2 space-y-8">
          
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-primary-navy">Wellness Trends</h2>
            <div className="flex bg-white rounded-lg border border-slate-200 p-1">
              {[7, 30, 90].map(days => (
                <button
                  key={days}
                  onClick={() => setDateRange(days)}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    dateRange === days ? 'bg-primary-navy text-white' : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {days}D
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <WellnessChart title="Sleep Trend" data={historySlice(personnel.sleepHistory)} color="#12544F" domain={[4, 10]} />
            <WellnessChart title="Mood Trend" data={historySlice(personnel.moodHistory)} color="#3B82F6" domain={[1, 5]} />
            <WellnessChart title="Workload Trend" data={historySlice(personnel.workloadHistory)} color="#F59E0B" domain={[1, 5]} />
            <WellnessChart title="Stress Indicator Trend" data={historySlice(personnel.stressHistory)} color="#092328" domain={[1, 5]} />
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-primary-navy">Personal Pattern</h3>
              <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-md font-medium uppercase tracking-wider">
                Prototype baseline analysis
              </span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-500 mb-1">Typical Sleep</p>
                <p className="text-xl font-bold text-primary-navy">{personnel.personalBaseline.typicalSleep.toFixed(1)} h</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-500 mb-1">Typical Workload</p>
                <p className="text-xl font-bold text-primary-navy">{personnel.personalBaseline.typicalWorkload.toFixed(1)} / 5</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-500 mb-1">Typical Mood</p>
                <p className="text-xl font-bold text-primary-navy">{personnel.personalBaseline.typicalMood.toFixed(1)} / 5</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-sm text-slate-500 mb-1">Current Pattern</p>
                <p className={`text-sm font-bold mt-2 ${personnel.personalBaseline.deviationDetected ? 'text-attention-700' : 'text-secondary-teal'}`}>
                  {personnel.personalBaseline.deviationDetected ? 'Deviation detected' : 'Consistent with baseline'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (AI, Factors, Recommendations) */}
        <div className="space-y-6">
          
          {/* AI Analysis Placeholder */}
          <div className="bg-gradient-to-br from-primary-navy to-slate-800 p-6 rounded-xl shadow-lg text-white">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Activity size={20} className="text-secondary-teal" />
                AI Welfare Analysis
              </h3>
              <span className="text-xs bg-white/10 text-white/80 px-2 py-1 rounded-md font-medium uppercase tracking-wider">
                Prototype AI Output
              </span>
            </div>
            
            <div className="space-y-4 mb-6">
              <div className="flex justify-between items-end border-b border-white/10 pb-2">
                <span className="text-white/60 text-sm">Welfare Indicator</span>
                <span className={`font-bold text-lg ${
                  personnel.mockAIAnalysis.indicator === 'Elevated' ? 'text-attention' : 'text-positive'
                }`}>
                  {personnel.mockAIAnalysis.indicator}
                </span>
              </div>
              <div className="flex justify-between items-end border-b border-white/10 pb-2">
                <span className="text-white/60 text-sm">Confidence</span>
                <span className="font-bold text-lg">{personnel.mockAIAnalysis.confidence}%</span>
              </div>
              <div className="flex justify-between items-end">
                <span className="text-white/60 text-sm">Trend</span>
                <span className="font-bold text-lg">{personnel.mockAIAnalysis.trend}</span>
              </div>
            </div>

            <p className="text-xs text-white/50 bg-black/20 p-3 rounded-lg leading-relaxed">
              AI analysis will be connected to the ML engine in a future version. This is not a medical diagnosis.
            </p>
          </div>

          {/* Contributing Factors */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-primary-navy flex items-center gap-2">
                <BarChart2 size={20} className="text-slate-400" />
                Contributing Factors
              </h3>
              <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-md font-medium uppercase tracking-wider">
                Prototype explanation
              </span>
            </div>

            <div className="space-y-4">
              {personnel.mockFactors.map((factor, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">{factor.factor}</span>
                    <span className={factor.impact > 0 ? 'text-attention-700' : 'text-secondary-teal'}>
                      {factor.impact > 0 ? '+' : ''}{factor.impact}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden flex">
                    {/* Hacky mock SHAP visualization */}
                    <div 
                      className={`h-full rounded-full ${factor.impact > 0 ? 'bg-attention' : 'bg-secondary-teal'}`} 
                      style={{ width: `${Math.abs(factor.impact) * 3}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-primary-navy mb-4">Suggested Welfare Actions</h3>
            
            <div className="space-y-3 mb-6">
              <RecommendationCard 
                title="Workload Review" 
                desc="Review recent workload pattern." 
              />
              <RecommendationCard 
                title="Recovery Opportunity" 
                desc="Consider appropriate recovery time." 
              />
              <RecommendationCard 
                title="Wellness Follow-up" 
                desc="Consider a voluntary welfare follow-up." 
              />
            </div>
            
            <button 
              onClick={() => setModalOpen(true)}
              className="w-full py-3 bg-white border-2 border-secondary-teal text-secondary-teal rounded-lg font-bold hover:bg-secondary-teal hover:text-white transition-colors"
            >
              Create Intervention
            </button>
          </div>

        </div>
      </div>

      {/* Privacy Notice */}
      <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 p-4 rounded-xl text-slate-600 mb-10">
        <ShieldCheck size={20} className="mt-0.5 text-secondary-teal shrink-0" />
        <div>
          <p className="font-bold text-slate-800">Authorized Welfare Access</p>
          <p className="text-sm mt-1">
            This information is available only to authorized welfare personnel. Individual welfare information is restricted to authorized users.
          </p>
        </div>
      </div>

      <InterventionModal 
        isOpen={modalOpen} 
        onClose={() => setModalOpen(false)} 
        onSubmit={handleCreateIntervention} 
      />
    </div>
  );
};

const OverviewCard = ({ title, value, valueColor = 'text-primary-navy' }: { title: string, value: string, valueColor?: string }) => (
  <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-center">
    <p className="text-sm text-slate-500 font-medium mb-2">{title}</p>
    <p className={`text-2xl font-bold ${valueColor}`}>{value}</p>
  </div>
);

const RecommendationCard = ({ title, desc }: { title: string, desc: string }) => (
  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-start gap-3">
    <div className="mt-1 w-2 h-2 rounded-full bg-secondary-teal shrink-0" />
    <div>
      <p className="font-bold text-sm text-primary-navy">{title}</p>
      <p className="text-xs text-slate-500 mt-1">{desc}</p>
    </div>
  </div>
);
