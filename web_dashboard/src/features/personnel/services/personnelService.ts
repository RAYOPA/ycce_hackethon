import type { Personnel } from '../models/personnel';
import { fetchWithAuth } from '../../../utils/api';

export class PersonnelService {
  async getPersonnel(filters?: {
    unit?: string;
    trend?: string;
    followUp?: string;
    searchQuery?: string;
  }): Promise<Personnel[]> {
    const params = new URLSearchParams();
    if (filters?.unit && filters.unit !== 'All Units') params.append('unit_id', filters.unit);
    if (filters?.searchQuery) params.append('query', filters.searchQuery);
    // trend and followUp can be added if backend supports, otherwise ignored for now

    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await fetchWithAuth(`/personnel${query}`);
    if (!res.ok) throw new Error('Failed to fetch personnel');
    const data = await res.json();
    
    // Map backend array to Personnel[]
    return data.items.map((item: any) => ({
      id: item.id,
      personnelId: item.user_code || item.id,
      unitId: item.unit_id || 'Unknown',
      lastCheckIn: item.last_checkin_date || new Date().toISOString(),
      wellnessTrend: 'Stable', // Placeholder unless backend provides
      followUpStatus: item.is_active ? 'Not Required' : 'Required',
      lastUpdated: item.updated_at || new Date().toISOString(),
    }));
  }

  async getPersonnelById(id: string): Promise<Personnel | undefined> {
    const res = await fetchWithAuth(`/personnel/${id}`);
    if (!res.ok) throw new Error('Failed to fetch personnel');
    const item = await res.json();
    
    // Fetch wellness history
    const wellnessRes = await fetchWithAuth(`/wellness/${id}`);
    let sleepHistory: number[] = [];
    let moodHistory: number[] = [];
    let workloadHistory: number[] = [];
    let stressHistory: number[] = [];
    
    if (wellnessRes.ok) {
      const wellnessData = await wellnessRes.json();
      if (Array.isArray(wellnessData)) {
        // Assume ordered by date ascending for charts
        sleepHistory = wellnessData.map(w => w.sleep_hours);
        moodHistory = wellnessData.map(w => w.mental_score);
        workloadHistory = wellnessData.map(w => w.physical_score); // fallback for workload
        stressHistory = wellnessData.map(w => w.stress_level === 'HIGH' ? 5 : (w.stress_level === 'MODERATE' ? 3 : 1));
      }
    }

    return {
      id: item.id,
      personnelId: item.user_code || item.id,
      unitId: item.unit_id || 'Unknown',
      lastCheckIn: item.last_checkin_date || new Date().toISOString(),
      wellnessTrend: 'Stable',
      followUpStatus: item.is_active ? 'Not Required' : 'Required',
      lastUpdated: item.updated_at || new Date().toISOString(),
      sleepHistory,
      moodHistory,
      workloadHistory,
      stressHistory,
      personalBaseline: { typicalSleep: 0, typicalWorkload: 0, typicalMood: 0, deviationDetected: false },
      mockAIAnalysis: { indicator: 'Moderate', confidence: 0, trend: 'Stable' },
      mockFactors: []
    };
  }

  async createIntervention(personnelId: string, action: string, notes: string, date: string): Promise<void> {
    const res = await fetchWithAuth('/interventions', {
      method: 'POST',
      body: JSON.stringify({
        personnel_id: personnelId,
        action_type: action,
        notes: notes,
        follow_up_date: date
      })
    });
    if (!res.ok) throw new Error('Failed to create intervention');
  }
}

export const personnelService = new PersonnelService();
