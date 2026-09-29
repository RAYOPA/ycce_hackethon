import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Activity, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWellness = async () => {
      try {
        const res = await apiClient.get('/wellness/me');
        setHistory(res.data.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWellness();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mt-4">
        <h2 className="text-lg font-semibold text-slate-800 mb-2">Welcome back!</h2>
        <p className="text-slate-500 mb-4 text-sm">How are you feeling today? Don't forget to complete your daily check-in.</p>
        <Link 
          to="/wellness"
          className="bg-blue-600 text-white font-medium py-3 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors w-full"
        >
          <Activity size={20} />
          <span>New Check-in</span>
        </Link>
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-800">Recent Check-ins</h3>
          <Calendar size={18} className="text-slate-400" />
        </div>
        
        {loading ? (
          <p className="text-slate-500 text-center py-4">Loading...</p>
        ) : history.length === 0 ? (
          <div className="bg-slate-100 rounded-xl p-8 text-center border border-dashed border-slate-300">
            <p className="text-slate-500 text-sm">No check-ins yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.slice(0, 5).map((entry, idx) => (
              <div key={idx} className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex justify-between items-center">
                <div>
                  <p className="font-medium text-slate-800">{new Date(entry.checkin_date).toLocaleDateString()}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    Sleep: {entry.sleep_hours}h | Mood: {entry.mood_score}/10
                  </p>
                </div>
                <div className={`w-3 h-3 rounded-full ${entry.risk_flag ? 'bg-red-500' : 'bg-green-500'}`}></div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
