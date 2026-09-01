import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import { ShieldCheck, User, Users, ShieldAlert } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (email: string) => {
    try {
      setLoading(true);
      setError('');
      await login(email, 'demo123'); // Using the seeded password
      navigate('/overview');
    } catch (e) {
      setError('Failed to login. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center text-primary-navy mb-6">
          <div className="w-16 h-16 bg-white rounded-2xl shadow-sm border border-slate-200 flex items-center justify-center">
            <ShieldCheck size={32} className="text-secondary-teal" />
          </div>
        </div>
        <h2 className="text-center text-3xl font-extrabold text-primary-navy">
          ManRakshak
        </h2>
        <p className="mt-2 text-center text-sm text-slate-500">
          Organization Dashboard Prototype
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-sm border border-slate-200 sm:rounded-xl sm:px-10">
          
          <div className="space-y-6">
            <div className="text-center">
              <p className="text-sm font-medium text-slate-700 mb-4">Select a role to login securely (seeded demo data):</p>
              {error && <p className="text-sm text-red-500 mb-4">{error}</p>}
            </div>

            <button
              onClick={() => handleLogin('welfare@demo.com')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-4 border border-slate-200 rounded-lg shadow-sm bg-white hover:bg-slate-50 hover:border-secondary-teal transition-colors group disabled:opacity-50"
            >
              <div className="flex items-center gap-3">
                <div className="bg-slate-100 p-2 rounded-lg group-hover:bg-teal-50">
                  <User className="text-secondary-teal" size={20} />
                </div>
                <div className="text-left">
                  <p className="text-sm font-bold text-slate-800">Welfare Officer</p>
                  <p className="text-xs text-slate-500 mt-0.5">welfare@demo.com</p>
                </div>
              </div>
            </button>

            <button
              onClick={() => handleLogin('commander@demo.com')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-4 border border-slate-200 rounded-lg shadow-sm bg-white hover:bg-slate-50 hover:border-primary-navy transition-colors group disabled:opacity-50"
            >
              <div className="flex items-center gap-3">
                <div className="bg-slate-100 p-2 rounded-lg group-hover:bg-slate-200">
                  <Users className="text-primary-navy" size={20} />
                </div>
                <div className="text-left">
                  <p className="text-sm font-bold text-slate-800">Commander</p>
                  <p className="text-xs text-slate-500 mt-0.5">commander@demo.com</p>
                </div>
              </div>
            </button>

            <button
              onClick={() => handleLogin('admin@demo.com')}
              disabled={loading}
              className="w-full flex items-center justify-between px-4 py-4 border border-slate-200 rounded-lg shadow-sm bg-white hover:bg-slate-50 hover:border-amber-500 transition-colors group disabled:opacity-50"
            >
              <div className="flex items-center gap-3">
                <div className="bg-slate-100 p-2 rounded-lg group-hover:bg-amber-50">
                  <ShieldAlert className="text-amber-600" size={20} />
                </div>
                <div className="text-left">
                  <p className="text-sm font-bold text-slate-800">Administrator</p>
                  <p className="text-xs text-slate-500 mt-0.5">admin@demo.com</p>
                </div>
              </div>
            </button>
          </div>

          <div className="mt-8 pt-6 border-t border-slate-100">
            <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
              <ShieldCheck size={14} className="text-positive" />
              <span>Full-Stack Prototype: Connecting to Python API.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
