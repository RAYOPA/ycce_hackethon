import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { CheckCircle } from 'lucide-react';

export default function WellnessCheckin() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    sleep_hours: 7,
    mood_score: 5,
    energy_level: 5,
    workload_perception: 5,
    stress_level: 5
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const payload = {
        checkin_date: new Date().toISOString().split('T')[0],
        ...formData
      };
      await apiClient.post('/wellness/checkins', payload);
      setSuccess(true);
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit check-in');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center mt-12">
        <CheckCircle size={64} className="text-green-500 mb-4" />
        <h2 className="text-2xl font-bold text-slate-800">Check-in Complete!</h2>
        <p className="text-slate-500 mt-2">Thank you for updating your wellness data.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mt-4">
      <h2 className="text-xl font-bold text-slate-800 mb-6">Daily Check-in</h2>
      
      {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="flex justify-between text-sm font-medium text-slate-700 mb-2">
            <span>Sleep Hours</span>
            <span className="text-blue-600 font-bold">{formData.sleep_hours}h</span>
          </label>
          <input 
            type="range" min="0" max="14" step="0.5" name="sleep_hours"
            value={formData.sleep_hours} onChange={handleChange}
            className="w-full accent-blue-600"
          />
        </div>

        <div>
          <label className="flex justify-between text-sm font-medium text-slate-700 mb-2">
            <span>Mood Score (1-10)</span>
            <span className="text-blue-600 font-bold">{formData.mood_score}</span>
          </label>
          <input 
            type="range" min="1" max="10" step="1" name="mood_score"
            value={formData.mood_score} onChange={handleChange}
            className="w-full accent-blue-600"
          />
        </div>

        <div>
          <label className="flex justify-between text-sm font-medium text-slate-700 mb-2">
            <span>Energy Level (1-10)</span>
            <span className="text-blue-600 font-bold">{formData.energy_level}</span>
          </label>
          <input 
            type="range" min="1" max="10" step="1" name="energy_level"
            value={formData.energy_level} onChange={handleChange}
            className="w-full accent-blue-600"
          />
        </div>

        <div>
          <label className="flex justify-between text-sm font-medium text-slate-700 mb-2">
            <span>Workload Perception (1-10)</span>
            <span className="text-blue-600 font-bold">{formData.workload_perception}</span>
          </label>
          <input 
            type="range" min="1" max="10" step="1" name="workload_perception"
            value={formData.workload_perception} onChange={handleChange}
            className="w-full accent-blue-600"
          />
        </div>

        <div>
          <label className="flex justify-between text-sm font-medium text-slate-700 mb-2">
            <span>Stress Level (1-10)</span>
            <span className="text-blue-600 font-bold">{formData.stress_level}</span>
          </label>
          <input 
            type="range" min="1" max="10" step="1" name="stress_level"
            value={formData.stress_level} onChange={handleChange}
            className="w-full accent-blue-600"
          />
        </div>

        <button 
          type="submit" disabled={loading}
          className="w-full bg-blue-600 text-white font-medium p-3 rounded-xl hover:bg-blue-700 transition-colors mt-8 disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Submit Check-in'}
        </button>
      </form>
    </div>
  );
}
