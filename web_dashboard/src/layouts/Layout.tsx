import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Shield, LayoutDashboard, Users, Activity, LogOut, Menu, X, Settings, HelpCircle, Bell, User, BarChart2, FileText, ShieldAlert } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Overview', path: '/overview', icon: LayoutDashboard, roles: ['Welfare Officer', 'Commander', 'Administrator'] },
    { name: 'Personnel', path: '/personnel', icon: Users, roles: ['Welfare Officer'] },
    { name: 'Analytics', path: '/analytics', icon: BarChart2, roles: ['Welfare Officer', 'Commander', 'Administrator'] },
    { name: 'Workload', path: '/workload', icon: Activity, roles: ['Welfare Officer', 'Commander', 'Administrator'] },
    { name: 'Reports', path: '/reports', icon: FileText, roles: ['Welfare Officer', 'Commander', 'Administrator'] },
    { name: 'Interventions', path: '/interventions', icon: Shield, roles: ['Welfare Officer'] },
  ];

  const bottomItems = [
    { name: 'Administration', path: '/admin', icon: ShieldAlert, roles: ['Administrator'] },
    { name: 'Settings', path: '/settings', icon: Settings, roles: ['Welfare Officer', 'Commander', 'Administrator'] },
  ];

  const filteredNavItems = navItems.filter(item => user && item.roles.includes(user.role));
  const filteredBottomItems = bottomItems.filter(item => user && item.roles.includes(user.role));

  return (
    <div className="flex h-screen bg-background-light overflow-hidden">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-primary-navy text-white transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 flex flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="text-secondary-teal" size={32} />
            <span className="text-xl font-bold tracking-tight">ManRakshak</span>
          </div>
          <button className="md:hidden text-slate-300" onClick={() => setSidebarOpen(false)}>
            <X size={24} />
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-2 overflow-y-auto mt-4">
          {filteredNavItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                  isActive ? 'bg-secondary-teal text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <item.icon size={20} />
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 space-y-2 border-t border-white/10">
          {filteredBottomItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                  isActive ? 'bg-secondary-teal text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <item.icon size={20} />
              {item.name}
            </NavLink>
          ))}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 w-full text-left rounded-lg font-medium text-slate-300 hover:bg-attention/20 hover:text-attention transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Topbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-30 shadow-sm">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-slate-500" onClick={() => setSidebarOpen(true)}>
              <Menu size={24} />
            </button>
            <div className="hidden sm:flex items-center bg-slate-100 rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 border border-slate-200">
              <span className="text-secondary-teal mr-2">●</span> Unit: {user?.unit || 'Unknown'}
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <NavLink to="/notifications" className={({ isActive }) => `p-2 rounded-full transition-colors relative ${isActive ? 'text-secondary-teal bg-teal-50' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}>
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-critical rounded-full border border-white"></span>
            </NavLink>
            <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-bold text-slate-800">{user?.name}</p>
                <p className="text-xs text-slate-500">{user?.role}</p>
              </div>
              <div className="h-9 w-9 bg-primary-navy rounded-full flex items-center justify-center text-white font-bold text-sm">
                {user?.name.charAt(0) || 'U'}
              </div>
            </div>
          </div>
        </header>

        {/* Demo Indicator */}
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-1.5 flex items-center justify-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
          </span>
          <p className="text-xs font-bold text-amber-700 uppercase tracking-wider">Prototype / Demo Environment</p>
        </div>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-auto bg-background-light">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
