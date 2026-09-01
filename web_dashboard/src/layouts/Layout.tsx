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
    <div className="flex h-screen bg-helios-background overflow-hidden">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-helios-card text-white transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 flex flex-col border-r border-white/5 shadow-2xl ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="text-white" size={28} />
            <span className="text-xl font-medium tracking-tight">ManRakshak</span>
          </div>
          <button className="md:hidden text-helios-muted" onClick={() => setSidebarOpen(false)}>
            <X size={24} />
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-2 overflow-y-auto mt-4">
          {filteredNavItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-2xl font-medium transition-all duration-300 ${
                  isActive 
                  ? 'bg-gradient-to-r from-helios-purple/20 to-helios-pink/10 border border-helios-purple/30 text-white shadow-[0_0_15px_rgba(147,51,234,0.15)]' 
                  : 'text-helios-muted hover:bg-white/5 hover:text-white border border-transparent'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon size={20} className={isActive ? "text-helios-primary" : ""} />
                  {item.name}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 space-y-2 border-t border-white/5">
          {filteredBottomItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-2xl font-medium transition-colors ${
                  isActive ? 'bg-white/10 text-white' : 'text-helios-muted hover:bg-white/5 hover:text-white'
                }`
              }
            >
              <item.icon size={20} />
              {item.name}
            </NavLink>
          ))}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 w-full text-left rounded-2xl font-medium text-helios-muted hover:bg-red-500/10 hover:text-red-400 transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Topbar */}
        <header className="h-20 bg-transparent flex items-center justify-between px-8 shrink-0 z-30">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-helios-muted" onClick={() => setSidebarOpen(true)}>
              <Menu size={24} />
            </button>
            <div className="hidden sm:flex flex-col">
              <h2 className="text-2xl font-semibold text-white tracking-wide">Welcome, {user?.name.split(' ')[0]}</h2>
              <p className="text-sm text-helios-muted">Here's your personnel welfare overview</p>
            </div>
          </div>
          
          <div className="flex items-center gap-5">
            {/* Ask AI Search Bar */}
            <div className="hidden lg:flex items-center bg-helios-card/80 border border-white/5 rounded-full px-4 py-2.5 shadow-lg backdrop-blur-md">
               <Shield size={16} className="text-helios-muted mr-2" />
               <input type="text" placeholder="Ask manrakshak.ai anything" className="bg-transparent border-none outline-none text-sm text-white placeholder-helios-muted w-48" />
            </div>

            <NavLink to="/notifications" className="p-3 rounded-full transition-colors relative bg-helios-card border border-white/5 text-helios-muted hover:text-white shadow-lg">
              <Bell size={18} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-helios-pink rounded-full"></span>
            </NavLink>
            <button className="p-3 rounded-full transition-colors bg-helios-card border border-white/5 text-helios-muted hover:text-white shadow-lg hidden sm:block">
              <Settings size={18} />
            </button>
            
            <div className="flex items-center gap-3 pl-2">
              <div className="h-10 w-10 bg-gradient-to-tr from-helios-purple to-helios-pink rounded-full flex items-center justify-center text-white font-bold text-sm shadow-[0_0_15px_rgba(219,39,119,0.3)]">
                {user?.name.charAt(0) || 'U'}
              </div>
              <div className="text-left hidden md:block">
                <p className="text-sm font-medium text-white">{user?.name}</p>
                <p className="text-xs text-helios-muted">{user?.role}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-auto bg-helios-background">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
