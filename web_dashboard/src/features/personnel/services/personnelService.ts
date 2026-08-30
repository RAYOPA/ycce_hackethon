import type { Personnel } from '../models/personnel';
import { MOCK_PERSONNEL_DATA } from './mockData';

export class PersonnelService {
  private data: Personnel[] = [...MOCK_PERSONNEL_DATA];

  async getPersonnel(filters?: {
    unit?: string;
    trend?: string;
    followUp?: string;
    searchQuery?: string;
  }): Promise<Personnel[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));

    let filtered = this.data;

    if (filters) {
      if (filters.unit && filters.unit !== 'All Units') {
        filtered = filtered.filter(p => p.unitId === filters.unit);
      }
      if (filters.trend && filters.trend !== 'All') {
        filtered = filtered.filter(p => p.wellnessTrend === filters.trend);
      }
      if (filters.followUp && filters.followUp !== 'All') {
        filtered = filtered.filter(p => p.followUpStatus === filters.followUp);
      }
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        filtered = filtered.filter(p => p.personnelId.toLowerCase().includes(query));
      }
    }

    return filtered;
  }

  async getPersonnelById(id: string): Promise<Personnel | undefined> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return this.data.find(p => p.id === id);
  }

  async createIntervention(personnelId: string, action: string, notes: string, date: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // In mock, just update the follow-up status to indicate an intervention was created
    const index = this.data.findIndex(p => p.id === personnelId);
    if (index !== -1) {
      this.data[index] = {
        ...this.data[index],
        followUpStatus: 'Completed',
        lastUpdated: new Date().toISOString()
      };
    }
  }
}

export const personnelService = new PersonnelService();
