import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Send } from 'lucide-react';

export default function SupportRequests() {
  const [requests, setRequests] = useState<any[]>([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchRequests = async () => {
    try {
      const res = await apiClient.get('/support/me');
      setRequests(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    setLoading(true);
    try {
      await apiClient.post('/support', {
        request_type: 'GENERAL',
        priority: 'MEDIUM',
        message: message,
        preferred_contact_method: 'APP'
      });
      setMessage('');
      fetchRequests();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 mt-4">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800 mb-2">Request Support</h2>
        <p className="text-slate-500 text-sm mb-4">Connect confidentially with a welfare officer or counselor.</p>
        
        <form onSubmit={handleSubmit}>
          <textarea
            className="w-full border border-slate-300 rounded-xl p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all mb-3 text-sm min-h-[100px]"
            placeholder="How can we help you?"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
          ></textarea>
          <button 
            type="submit" disabled={loading}
            className="w-full bg-slate-800 text-white font-medium py-2.5 rounded-lg hover:bg-slate-900 transition-colors flex items-center justify-center gap-2"
          >
            <Send size={16} />
            <span>Send Request</span>
          </button>
        </form>
      </div>

      <div>
        <h3 className="font-semibold text-slate-800 mb-3">Past Requests</h3>
        {requests.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-4">No support requests.</p>
        ) : (
          <div className="space-y-3">
            {requests.map((req, idx) => (
              <div key={idx} className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded">
                    {req.status}
                  </span>
                  <span className="text-xs text-slate-400">
                    {new Date(req.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-slate-700 text-sm">{req.message}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
