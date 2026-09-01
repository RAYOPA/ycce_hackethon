import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { Shield } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/auth/login', {
        email: username,
        password: password
      });
      
      localStorage.setItem('token', response.data.access_token);
      
      // Fetch user info
      const userRes = await apiClient.get('/auth/me');
      if (userRes.data.role === 'PERSONNEL') {
         localStorage.setItem('user', JSON.stringify(userRes.data));
         navigate('/dashboard');
      } else {
         setError('This app is for personnel only. Commanders should use the web dashboard.');
         localStorage.removeItem('token');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="flex justify-center mb-6 text-blue-600">
          <Shield size={64} />
        </div>
        <h2 className="text-2xl font-bold text-center mb-6 text-slate-800">ManRakshak<br/><span className="text-lg font-normal text-slate-500">Personnel Portal</span></h2>
        
        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <input 
              type="text" 
              className="w-full border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input 
              type="password" 
              className="w-full border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button 
            type="submit"
            className="w-full bg-blue-600 text-white font-medium p-2.5 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Sign In
          </button>
          <div className="text-center mt-4">
            <span className="text-sm text-slate-600">Don't have an account? </span>
            <Link to="/register" className="text-sm text-blue-600 hover:underline">Register</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
