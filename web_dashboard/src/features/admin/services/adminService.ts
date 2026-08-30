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

class AdminService {
  private users: AdminUser[] = [
    { id: 'W001', name: 'Demo Welfare Officer', email: 'welfare@demo.com', role: 'Welfare Officer', unit: 'Unit A', status: 'Active', lastActive: 'Today' },
    { id: 'C001', name: 'Demo Commander', email: 'commander@demo.com', role: 'Commander', unit: 'All Units', status: 'Active', lastActive: 'Today' },
    { id: 'A001', name: 'Demo Administrator', email: 'admin@demo.com', role: 'Administrator', unit: 'Organization', status: 'Active', lastActive: 'Today' },
    { id: 'W002', name: 'Sarah Jenkins', email: 's.jenkins@demo.com', role: 'Welfare Officer', unit: 'Unit B', status: 'Active', lastActive: 'Yesterday' },
    { id: 'W003', name: 'Michael Chen', email: 'm.chen@demo.com', role: 'Welfare Officer', unit: 'Unit C', status: 'Inactive', lastActive: '2 weeks ago' },
  ];

  private units: AdminUnit[] = [
    { id: 'U001', name: 'Unit A', personnelCount: 320, status: 'Active' },
    { id: 'U002', name: 'Unit B', personnelCount: 280, status: 'Active' },
    { id: 'U003', name: 'Unit C', personnelCount: 350, status: 'Active' },
    { id: 'U004', name: 'Unit D', personnelCount: 290, status: 'Active' },
  ];

  private logs: AuditLog[] = [
    { id: 'L1', time: '09:42 PM', user: 'W001', action: 'Viewed welfare dashboard', resource: 'Dashboard', status: 'Success' },
    { id: 'L2', time: '09:30 PM', user: 'A001', action: 'Updated user role', resource: 'User W002', status: 'Success' },
    { id: 'L3', time: '08:52 PM', user: 'C001', action: 'Viewed unit analytics', resource: 'Unit A', status: 'Success' },
    { id: 'L4', time: '08:15 PM', user: 'W002', action: 'Exported report', resource: 'Reports', status: 'Success' },
    { id: 'L5', time: '07:40 PM', user: 'U999', action: 'Failed login attempt', resource: 'Auth', status: 'Failed' },
  ];

  async getUsers(): Promise<AdminUser[]> {
    return [...this.users];
  }

  async createUser(user: Omit<AdminUser, 'id' | 'lastActive'>): Promise<AdminUser> {
    const newUser: AdminUser = {
      ...user,
      id: `${user.role.charAt(0)}${Math.floor(100 + Math.random() * 900)}`,
      lastActive: 'Never',
    };
    this.users = [newUser, ...this.users];
    return newUser;
  }

  async disableUser(id: string): Promise<void> {
    this.users = this.users.map(u => u.id === id ? { ...u, status: 'Inactive' } : u);
  }

  async getUnits(): Promise<AdminUnit[]> {
    return [...this.units];
  }

  async createUnit(unit: Omit<AdminUnit, 'id' | 'personnelCount'>): Promise<AdminUnit> {
    const newUnit: AdminUnit = {
      ...unit,
      id: `U00${this.units.length + 1}`,
      personnelCount: 0,
    };
    this.units = [...this.units, newUnit];
    return newUnit;
  }

  async getAuditLogs(): Promise<AuditLog[]> {
    return [...this.logs];
  }
}

export const adminService = new AdminService();
