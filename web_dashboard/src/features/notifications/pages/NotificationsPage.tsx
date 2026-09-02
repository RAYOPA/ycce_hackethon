import React, { useState, useEffect } from 'react';
import { Bell, Check, Trash2, Calendar, TrendingUp, AlertCircle, FileText, Settings, ShieldCheck } from 'lucide-react';

interface Notification {
  id: string;
  type: 'Follow-up' | 'Trend' | 'Support' | 'Report' | 'System';
  title: string;
  description: string;
  time: string;
  read: boolean;
}

import { notificationService, AppNotification } from '../services/notificationService';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [filter, setFilter] = useState<'All' | 'Unread' | 'Follow-ups' | 'Trends' | 'Support' | 'System'>('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, [filter]);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const data = await notificationService.getNotifications({
        type: filter,
      });
      setNotifications(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationService.markAsRead(id);
      setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
    } catch (e) {
      console.error(e);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications(notifications.map(n => ({ ...n, read: true })));
    } catch (e) {
      console.error(e);
    }
  };



  // Handle Mark All as Read replaced above

  const handleClearRead = () => {
    // Backend doesn't support deleting notifications yet. Just filter them locally.
    if (confirm("Clear read notifications from view?")) {
      setNotifications(notifications.filter(n => !n.read));
    }
  };

  // filteredNotifications replaced by backend filtering and UI local unread filter if 'Unread' is selected
  const filteredNotifications = filter === 'Unread' ? notifications.filter(n => !n.read) : notifications;

  const getIcon = (type: string) => {
    switch (type) {
      case 'Follow-up': return <Calendar className="text-secondary-teal" size={20} />;
      case 'Trend': return <TrendingUp className="text-primary-navy" size={20} />;
      case 'Support': return <AlertCircle className="text-amber-500" size={20} />;
      case 'Report': return <FileText className="text-purple-500" size={20} />;
      case 'System': return <Settings className="text-slate-500" size={20} />;
      default: return <Bell size={20} />;
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary-navy">Notifications</h1>
          <p className="text-slate-500 mt-1">Stay updated on welfare activities and organizational insights</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleClearRead} className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg flex items-center gap-2 hover:bg-slate-50 transition-colors">
            <Trash2 size={16} /> Clear Read
          </button>
          <button onClick={handleMarkAllAsRead} className="px-4 py-2 text-sm font-medium text-white bg-primary-navy rounded-lg flex items-center gap-2 hover:bg-primary-navy/90 transition-colors">
            <Check size={16} /> Mark all as read
          </button>
        </div>
      </div>

      {/* Privacy Notice */}
      <div className="flex items-start gap-3 bg-slate-50 border border-slate-200 p-3 rounded-lg text-slate-600 shadow-sm">
        <ShieldCheck size={18} className="mt-0.5 text-secondary-teal shrink-0" />
        <div>
          <p className="font-bold text-slate-800 text-sm">Privacy-first notifications</p>
          <p className="text-xs mt-0.5">
            Notifications are generated according to your authorized role and access level. Individual welfare information is restricted.
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Unread</p>
          <p className="text-3xl font-black text-attention">{unreadCount}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Follow-ups</p>
          <p className="text-3xl font-black text-secondary-teal">{notifications.filter(n => n.type === 'Follow-up').length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">Support Requests</p>
          <p className="text-3xl font-black text-amber-500">{notifications.filter(n => n.type === 'Support').length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-sm font-medium text-slate-500 mb-1">System</p>
          <p className="text-3xl font-black text-slate-700">{notifications.filter(n => n.type === 'System').length}</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {['All', 'Unread', 'Follow-ups', 'Trends', 'Support', 'System'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f as any)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f ? 'bg-primary-navy text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        {filteredNotifications.length === 0 ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 border border-slate-100">
              <Bell className="text-slate-300" size={32} />
            </div>
            <h3 className="text-lg font-medium text-slate-700 mb-1">No notifications</h3>
            <p>You're all caught up.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredNotifications.map(notification => (
              <div 
                key={notification.id} 
                className={`p-4 flex gap-4 transition-colors hover:bg-slate-50 ${!notification.read ? 'bg-teal-50/30' : ''}`}
              >
                <div className="shrink-0 mt-1 relative">
                  <div className={`p-2 rounded-lg ${!notification.read ? 'bg-white shadow-sm border border-slate-200' : 'bg-slate-100'}`}>
                    {getIcon(notification.type)}
                  </div>
                  {!notification.read && <div className="absolute -top-1 -right-1 w-3 h-3 bg-secondary-teal rounded-full border-2 border-white"></div>}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p className={`text-sm font-bold ${!notification.read ? 'text-primary-navy' : 'text-slate-700'}`}>
                      {notification.title}
                    </p>
                    <span className="text-xs font-medium text-slate-400">{notification.time}</span>
                  </div>
                  <p className="text-sm text-slate-600">{notification.description}</p>
                  
                  <div className="mt-3 flex gap-3">
                    <button className="text-xs font-bold text-secondary-teal hover:text-primary-navy transition-colors">
                      View Details
                    </button>
                    {!notification.read && (
                      <button 
                        onClick={() => handleMarkAsRead(notification.id)}
                        className="text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};
