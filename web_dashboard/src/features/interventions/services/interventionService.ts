import type { Intervention, InterventionStatus } from '../models/intervention';
import { MOCK_INTERVENTIONS } from './mockInterventionData';

export class InterventionService {
  private data: Intervention[] = [...MOCK_INTERVENTIONS];

  async getInterventions(filters?: {
    statusTab?: string;
    unit?: string;
    actionType?: string;
    searchQuery?: string;
  }): Promise<Intervention[]> {
    await new Promise(resolve => setTimeout(resolve, 500));

    let filtered = this.data;

    if (filters) {
      if (filters.statusTab && filters.statusTab !== 'All') {
        if (filters.statusTab === 'Due Today') {
          filtered = filtered.filter(i => i.status === 'Due');
        } else {
          filtered = filtered.filter(i => i.status === filters.statusTab);
        }
      }
      if (filters.unit && filters.unit !== 'All Units') {
        filtered = filtered.filter(i => i.unitId === filters.unit);
      }
      if (filters.actionType && filters.actionType !== 'All') {
        filtered = filtered.filter(i => i.actionType === filters.actionType);
      }
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        filtered = filtered.filter(i => i.personnelId.toLowerCase().includes(query));
      }
    }

    return filtered.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async getInterventionById(id: string): Promise<Intervention | undefined> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return this.data.find(i => i.id === id);
  }

  async createIntervention(data: Partial<Intervention>): Promise<Intervention> {
    await new Promise(resolve => setTimeout(resolve, 500));
    const newIntervention: Intervention = {
      id: `INT-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
      personnelId: data.personnelId || '',
      unitId: data.unitId || 'Unit A',
      actionType: data.actionType || '',
      assignedOfficer: data.assignedOfficer || '',
      createdAt: new Date().toISOString(),
      followUpDate: data.followUpDate || new Date().toISOString(),
      status: 'Upcoming',
      notes: data.notes || '',
      history: [
        {
          status: 'Created',
          date: new Date().toISOString(),
          note: 'Intervention created'
        }
      ]
    };
    
    this.data = [newIntervention, ...this.data];
    return newIntervention;
  }

  async updateIntervention(id: string, updates: Partial<Intervention>): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 400));
    const index = this.data.findIndex(i => i.id === id);
    if (index !== -1) {
      this.data[index] = { ...this.data[index], ...updates };
      
      if (updates.status) {
        this.data[index].history.push({
          status: updates.status,
          date: new Date().toISOString(),
          note: `Status updated to ${updates.status}`
        });
      }
    }
  }

  async completeIntervention(id: string): Promise<void> {
    await this.updateIntervention(id, { status: 'Completed' });
  }

  async rescheduleIntervention(id: string, newDate: string): Promise<void> {
    await this.updateIntervention(id, { followUpDate: newDate, status: 'Rescheduled' });
  }
}

export const interventionService = new InterventionService();
