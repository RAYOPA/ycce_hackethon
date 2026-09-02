export interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: 'Welfare Officer' | 'Commander' | 'Administrator';
  unit: string;
  status: 'Active' | 'Inactive';
  lastActive: string;
}

export interface AdminUnit {
  id: string;
  name: string;
  personnelCount: number;
  status: 'Active' | 'Inactive';
}

export interface AuditLog {
  id: string;
  time: string;
  user: string;
  action: string;
  resource: string;
  status: 'Success' | 'Failed';
}

import { fetchWithAuth } from '../../../utils/api';

class AdminService {

  async getUsers(): Promise<AdminUser[]> {
    const res = await fetchWithAuth('/admin/users');
    if (!res.ok) throw new Error('Failed to fetch users');
    const data = await res.json();
    return data.items.map((u: any) => ({
      id: u.user_code,
      name: u.name,
      email: u.email,
      role: u.role === 'WELFARE_OFFICER' ? 'Welfare Officer' : (u.role === 'COMMANDER' ? 'Commander' : (u.role === 'ADMINISTRATOR' ? 'Administrator' : 'Personnel')),
      unit: u.unit_id || 'All Units',
      status: u.status === 'ACTIVE' ? 'Active' : 'Inactive',
      lastActive: u.last_login_at || 'Never'
    }));
  }

  async createUser(user: Omit<AdminUser, 'id' | 'lastActive'>): Promise<AdminUser> {
    const res = await fetchWithAuth('/admin/users', {
      method: 'POST',
      body: JSON.stringify({
        user_code: `U${Math.floor(1000 + Math.random() * 9000)}`,
        name: user.name,
        email: user.email,
        password: 'ChangeMe123!', // default password for new users
        role: user.role === 'Welfare Officer' ? 'WELFARE_OFFICER' : (user.role === 'Commander' ? 'COMMANDER' : 'ADMINISTRATOR'),
        unit_id: user.unit === 'All Units' ? null : user.unit
      })
    });
    if (!res.ok) throw new Error('Failed to create user');
    const data = await res.json();
    return {
      id: data.user_code,
      name: data.name,
      email: data.email,
      role: user.role,
      unit: data.unit_id || 'All Units',
      status: 'Active',
      lastActive: 'Never'
    };
  }

  async disableUser(id: string): Promise<void> {
    const res = await fetchWithAuth(`/admin/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: 'INACTIVE' })
    });
    if (!res.ok) throw new Error('Failed to disable user');
  }

  async getUnits(): Promise<AdminUnit[]> {
    const res = await fetchWithAuth('/admin/units');
    if (!res.ok) throw new Error('Failed to fetch units');
    const data = await res.json();
    return data.items.map((u: any) => ({
      id: u.id,
      name: u.unit_name,
      personnelCount: 0, // Need extra query or analytics for this if needed
      status: u.status === 'ACTIVE' ? 'Active' : 'Inactive'
    }));
  }

  async createUnit(unit: Omit<AdminUnit, 'id' | 'personnelCount'>): Promise<AdminUnit> {
    const res = await fetchWithAuth('/admin/units', {
      method: 'POST',
      body: JSON.stringify({
        unit_code: `U${Math.floor(100 + Math.random() * 900)}`,
        unit_name: unit.name
      })
    });
    if (!res.ok) throw new Error('Failed to create unit');
    const data = await res.json();
    return {
      id: data.id,
      name: data.unit_name,
      personnelCount: 0,
      status: 'Active'
    };
  }

  async getAuditLogs(): Promise<AuditLog[]> {
    const res = await fetchWithAuth('/admin/audit-logs');
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    const data = await res.json();
    return data.items.map((log: any) => ({
      id: log.id,
      time: log.timestamp,
      user: log.user_id,
      action: log.action,
      resource: log.resource_type,
      status: 'Success' // assuming success since it's recorded
    }));
  }
}

export const adminService = new AdminService();
