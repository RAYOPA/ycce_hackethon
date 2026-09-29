import { fetchWithAuth } from '../../../utils/api';

export interface AppNotification {
  id: string;
  type: 'Follow-up' | 'Trend' | 'Support' | 'Report' | 'System';
  title: string;
  description: string;
  time: string;
  read: boolean;
}

export class NotificationService {
  async getNotifications(filters?: { read?: boolean, type?: string }): Promise<AppNotification[]> {
    const params = new URLSearchParams();
    if (filters?.read !== undefined) params.append('is_read', filters.read.toString());
    if (filters?.type && filters.type !== 'All') {
      const typeMap: any = {
        'Follow-ups': 'FOLLOWUP',
        'Trends': 'TREND_ALERT',
        'Support': 'SUPPORT_REQUEST',
        'System': 'SYSTEM_ALERT'
      };
      if (typeMap[filters.type]) params.append('notification_type', typeMap[filters.type]);
    }
    
    const res = await fetchWithAuth(`/notifications?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch notifications');
    const data = await res.json();
    return data.items.map((n: any) => ({
      id: n.id,
      type: this.mapType(n.notification_type),
      title: n.title,
      description: n.message,
      time: new Date(n.created_at).toLocaleString(), // Format appropriately
      read: n.is_read
    }));
  }

  async markAsRead(id: string): Promise<void> {
    const res = await fetchWithAuth(`/notifications/${id}/read`, { method: 'PATCH' });
    if (!res.ok) throw new Error('Failed to mark notification as read');
  }

  async markAllAsRead(): Promise<void> {
    const res = await fetchWithAuth('/notifications/read-all', { method: 'PATCH' });
    if (!res.ok) throw new Error('Failed to mark all as read');
  }

  private mapType(type: string): 'Follow-up' | 'Trend' | 'Support' | 'Report' | 'System' {
    switch (type) {
      case 'FOLLOWUP': return 'Follow-up';
      case 'FOLLOW_UP': return 'Follow-up';
      case 'TREND_ALERT': return 'Trend';
      case 'SUPPORT_REQUEST': return 'Support';
      case 'REPORT_READY': return 'Report';
      case 'SYSTEM_ALERT': return 'System';
      default: return 'System';
    }
  }
}

export const notificationService = new NotificationService();
