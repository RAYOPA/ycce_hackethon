import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, Users, Lock, Building, FileText, Settings, 
  Search, Plus, MoreVertical, CheckCircle, XCircle
} from 'lucide-react';
import { adminService } from '../services/adminService';
import type { AdminUser, AdminUnit, AuditLog } from '../services/adminService';
import { useAuth } from '../../../contexts/AuthContext';

// --- Sub Components ---

const AdminOverview = () => (
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
      <p className="text-sm font-medium text-slate-500 mb-1">Total Users</p>
      <p className="text-3xl font-black text-slate-800">48</p>
    </div>
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
      <p className="text-sm font-medium text-slate-500 mb-1">Welfare Officers</p>
      <p className="text-3xl font-black text-secondary-teal">12</p>
    </div>
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
      <p className="text-sm font-medium text-slate-500 mb-1">Commanders</p>
      <p className="text-3xl font-black text-primary-navy">6</p>
    </div>
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
      <p className="text-sm font-medium text-slate-500 mb-1">Active Users</p>
      <p className="text-3xl font-black text-positive">44</p>
    </div>
  </div>
);

const AdminUsers = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [newUser, setNewUser] = useState({ name: '', email: '', role: 'Welfare Officer', unit: 'Unit A', status: 'Active' });

  useEffect(() => {
    adminService.getUsers().then(setUsers);
  }, []);

  const handleCreate = async () => {
    const created = await adminService.createUser(newUser as any);
    setUsers([created, ...users]);
    setShowModal(false);
  };

  const handleDisable = async (id: string) => {
    if (confirm("Disable this user?")) {
      await adminService.disableUser(id);
      const updated = await adminService.getUsers();
      setUsers(updated);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input 
            type="text" 
            placeholder="Search users..." 
            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-secondary-teal"
          />
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-navy text-white rounded-lg text-sm font-medium hover:bg-primary-navy/90 transition-colors"
        >
          <Plus size={16} /> Add User
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">User ID</th>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Role</th>
              <th className="px-4 py-3 font-medium">Unit</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {users.map(user => (
              <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-800">{user.id}</td>
                <td className="px-4 py-3">
                  <p className="font-medium text-slate-800">{user.name}</p>
                  <p className="text-xs text-slate-500">{user.email}</p>
                </td>
                <td className="px-4 py-3 text-slate-600">{user.role}</td>
                <td className="px-4 py-3 text-slate-600">{user.unit}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${
                    user.status === 'Active' ? 'bg-[#E6F4EA] text-[#137333]' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {user.status === 'Active' ? <CheckCircle size={12} /> : <XCircle size={12} />}
                    {user.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <button 
                    onClick={() => handleDisable(user.id)}
                    className="text-xs font-medium text-secondary-teal hover:text-primary-navy"
                  >
                    {user.status === 'Active' ? 'Disable' : 'Enable'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-primary-navy mb-4">Add User</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 mb-1">Name</label>
                <input type="text" className="w-full p-2 border rounded" value={newUser.name} onChange={e => setNewUser({...newUser, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 mb-1">Role</label>
                <select className="w-full p-2 border rounded" value={newUser.role} onChange={e => setNewUser({...newUser, role: e.target.value})}>
                  <option>Welfare Officer</option>
                  <option>Commander</option>
                  <option>Administrator</option>
                </select>
              </div>
              <div className="flex gap-3 justify-end mt-6">
                <button onClick={() => setShowModal(false)} className="px-4 py-2 text-slate-500 font-medium">Cancel</button>
                <button onClick={handleCreate} className="px-4 py-2 bg-primary-navy text-white rounded font-medium">Create User</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const AdminRoles = () => (
  <div className="space-y-4">
    <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-sm text-slate-600 flex gap-2">
      <ShieldCheck size={18} className="text-secondary-teal shrink-0" />
      <p>Role permissions are enforced by the backend in production. This matrix displays the intended access controls.</p>
    </div>
    
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 border-b border-slate-200 text-slate-500">
          <tr>
            <th className="px-4 py-3 font-medium">Feature</th>
            <th className="px-4 py-3 font-medium text-center">Personnel</th>
            <th className="px-4 py-3 font-medium text-center">Welfare Officer</th>
            <th className="px-4 py-3 font-medium text-center">Commander</th>
            <th className="px-4 py-3 font-medium text-center">Administrator</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {[
            { feature: 'Own Wellness', p: '✓', w: '✓', c: '—', a: '✓' },
            { feature: 'Individual Welfare', p: 'Own Only', w: '✓', c: '—', a: '✓' },
            { feature: 'Aggregate Analytics', p: '—', w: '✓', c: '✓', a: '✓' },
            { feature: 'Interventions', p: '—', w: '✓', c: '—', a: '✓' },
            { feature: 'User Management', p: '—', w: '—', c: '—', a: '✓' },
            { feature: 'Audit Log', p: '—', w: 'Limited', c: '—', a: '✓' },
          ].map((row, i) => (
            <tr key={i} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-medium text-slate-800">{row.feature}</td>
              <td className="px-4 py-3 text-center text-slate-500">{row.p}</td>
              <td className="px-4 py-3 text-center text-slate-500">{row.w}</td>
              <td className="px-4 py-3 text-center text-slate-500">{row.c}</td>
              <td className="px-4 py-3 text-center text-slate-500">{row.a}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const AdminAuditLog = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  useEffect(() => { adminService.getAuditLogs().then(setLogs); }, []);

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 border-b border-slate-200 text-slate-500">
          <tr>
            <th className="px-4 py-3 font-medium">Time</th>
            <th className="px-4 py-3 font-medium">User</th>
            <th className="px-4 py-3 font-medium">Action</th>
            <th className="px-4 py-3 font-medium">Resource</th>
            <th className="px-4 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {logs.map(log => (
            <tr key={log.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-slate-500">{log.time}</td>
              <td className="px-4 py-3 font-medium text-slate-800">{log.user}</td>
              <td className="px-4 py-3 text-slate-600">{log.action}</td>
              <td className="px-4 py-3 text-slate-600">{log.resource}</td>
              <td className="px-4 py-3">
                <span className={`text-xs font-bold ${log.status === 'Success' ? 'text-positive' : 'text-attention-700'}`}>
                  {log.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const AdminSystem = () => (
  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
    <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Application</p>
        <p className="font-medium text-slate-800">ManRakshak</p>
      </div>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Environment</p>
        <p className="font-medium text-slate-800">Prototype</p>
      </div>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Version</p>
        <p className="font-medium text-slate-800">0.1.0</p>
      </div>
    </div>
    <hr className="border-slate-100" />
    <div className="grid grid-cols-2 gap-6">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-positive"></div>
        <div>
          <p className="text-sm font-bold text-slate-700">Frontend</p>
          <p className="text-xs text-slate-500">Operational</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-slate-300"></div>
        <div>
          <p className="text-sm font-bold text-slate-700">Backend</p>
          <p className="text-xs text-slate-500">Not connected</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-slate-300"></div>
        <div>
          <p className="text-sm font-bold text-slate-700">Database</p>
          <p className="text-xs text-slate-500">Not connected</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-slate-300"></div>
        <div>
          <p className="text-sm font-bold text-slate-700">AI Engine</p>
          <p className="text-xs text-slate-500">Not connected</p>
        </div>
      </div>
    </div>
  </div>
);

// --- Main Page ---

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Overview');
  const { user } = useAuth();
  const isAdmin = user?.role === 'Administrator';

  const tabs = [
    { id: 'Overview', icon: ShieldCheck },
    { id: 'Users', icon: Users },
    { id: 'Roles & Access', icon: Lock },
    { id: 'Units', icon: Building },
    { id: 'Audit Log', icon: FileText },
    { id: 'System', icon: Settings },
  ];

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="bg-red-50 p-4 rounded-full mb-4">
          <Lock className="text-red-500" size={32} />
        </div>
        <h2 className="text-2xl font-bold text-slate-800">Access Restricted</h2>
        <p className="text-slate-500 mt-2">You do not have permission to access administration settings.</p>
        <button className="mt-6 px-6 py-2 bg-primary-navy text-white rounded-lg font-medium">Return to Dashboard</button>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-primary-navy">Administration</h1>
        <p className="text-slate-500 mt-1">Manage organization access and system configuration</p>
      </div>

      {/* Privacy Notice */}
      <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 p-3 rounded-lg text-slate-600 shadow-sm">
        <ShieldCheck size={18} className="mt-0.5 text-secondary-teal shrink-0" />
        <div>
          <p className="font-bold text-slate-800 text-sm">Privacy-first administration</p>
          <p className="text-xs mt-0.5">
            Administrators manage system access and configuration. Access to personnel welfare information remains controlled by role permissions.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        {/* Sidebar */}
        <div className="md:col-span-3 bg-white border border-slate-200 rounded-xl p-2 shadow-sm sticky top-6">
          <nav className="space-y-1">
            {tabs.map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive ? 'bg-slate-100 text-primary-navy' : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <Icon size={18} className={isActive ? 'text-secondary-teal' : 'text-slate-400'} />
                  {tab.id}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="md:col-span-9">
          {activeTab === 'Overview' && <AdminOverview />}
          {activeTab === 'Users' && <AdminUsers />}
          {activeTab === 'Roles & Access' && <AdminRoles />}
          {activeTab === 'Audit Log' && <AdminAuditLog />}
          {activeTab === 'System' && <AdminSystem />}
          {activeTab === 'Units' && (
            <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm text-center text-slate-500">
              <Building className="mx-auto mb-3 text-slate-300" size={32} />
              <p>Units management interface prototype.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
