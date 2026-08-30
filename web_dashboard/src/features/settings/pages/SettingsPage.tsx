import React, { useState } from 'react';
import { Settings, Bell, Lock, User, Palette } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [notifications, setNotifications] = useState(true);

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary-navy">Settings</h1>
        <p className="text-slate-500 mt-1">Manage your dashboard preferences</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden divide-y divide-slate-100">
        
        {/* Profile */}
        <div className="p-6 flex flex-col md:flex-row gap-6">
          <div className="w-48 shrink-0">
            <div className="flex items-center gap-2 text-primary-navy font-bold">
              <User size={20} />
              Profile
            </div>
            <p className="text-sm text-slate-500 mt-1">Update your personal information.</p>
          </div>
          <div className="flex-1 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
              <input type="text" className="w-full max-w-md p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary-teal focus:outline-none" defaultValue="Demo User" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
              <input type="email" className="w-full max-w-md p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary-teal focus:outline-none" defaultValue="demo@manrakshak.org" />
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="p-6 flex flex-col md:flex-row gap-6">
          <div className="w-48 shrink-0">
            <div className="flex items-center gap-2 text-primary-navy font-bold">
              <Bell size={20} />
              Notifications
            </div>
            <p className="text-sm text-slate-500 mt-1">Manage how you receive alerts.</p>
          </div>
          <div className="flex-1 space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={notifications} 
                onChange={() => setNotifications(!notifications)} 
                className="w-4 h-4 text-secondary-teal rounded border-slate-300 focus:ring-secondary-teal" 
              />
              <span className="text-slate-700 font-medium">Enable Desktop Notifications</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                defaultChecked 
                className="w-4 h-4 text-secondary-teal rounded border-slate-300 focus:ring-secondary-teal" 
              />
              <span className="text-slate-700 font-medium">Weekly Email Summary</span>
            </label>
          </div>
        </div>

        {/* Security */}
        <div className="p-6 flex flex-col md:flex-row gap-6">
          <div className="w-48 shrink-0">
            <div className="flex items-center gap-2 text-primary-navy font-bold">
              <Lock size={20} />
              Security
            </div>
            <p className="text-sm text-slate-500 mt-1">Update your password.</p>
          </div>
          <div className="flex-1 space-y-4">
            <button className="px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition-colors">
              Change Password
            </button>
            <p className="text-xs text-slate-400">Password management will be available in production.</p>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3">
        <button className="px-6 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition-colors">
          Cancel
        </button>
        <button className="px-6 py-2 bg-primary-navy text-white rounded-lg font-medium hover:bg-primary-navy/90 transition-colors" onClick={() => alert('Settings saved! (Mock)')}>
          Save Settings
        </button>
      </div>
    </div>
  );
};
