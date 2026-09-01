import { Outlet, useNavigate, useLocation, Link } from 'react-router-dom';
import { Home, HeartPulse, MessageSquare, LogOut } from 'lucide-react';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Home' },
    { path: '/wellness', icon: HeartPulse, label: 'Wellness' },
    { path: '/support', icon: MessageSquare, label: 'Support' }
  ];

  return (
    <div className="min-h-screen bg-slate-50 pb-16 md:pb-0">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-md mx-auto px-4 py-3 flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-600">ManRakshak</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-slate-700">{user.full_name || 'User'}</span>
            <button onClick={handleLogout} className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors">
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-md mx-auto p-4">
        <Outlet />
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-10 pb-safe">
        <div className="max-w-md mx-auto flex justify-around">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center py-3 px-6 ${
                  isActive ? 'text-blue-600' : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                <Icon size={24} className={isActive ? 'mb-1' : 'mb-1 opacity-75'} />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
