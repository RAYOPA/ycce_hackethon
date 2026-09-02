import type { Intervention, InterventionStatus } from '../models/intervention';
import { fetchWithAuth } from '../../../utils/api';

export class InterventionService {
  async getInterventions(filters?: {
    statusTab?: string;
    unit?: string;
    actionType?: string;
    searchQuery?: string;
  }): Promise<Intervention[]> {
    const params = new URLSearchParams();
    if (filters?.statusTab && filters.statusTab !== 'All') {
      if (filters.statusTab === 'Due Today') params.append('status', 'PENDING');
      else if (filters.statusTab === 'Upcoming') params.append('status', 'PENDING');
      else if (filters.statusTab === 'Completed') params.append('status', 'COMPLETED');
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    
    const res = await fetchWithAuth(`/interventions${query}`);
    if (!res.ok) throw new Error('Failed to fetch interventions');
    const data = await res.json();

    return data.items.map((item: any) => ({
      id: item.id,
      personnelId: item.personnel_id,
      unitId: 'Unknown', // Not returned by API natively, fallback
      actionType: item.action_type,
      assignedOfficer: 'Assigned Officer', 
      createdAt: item.created_at,
      followUpDate: item.follow_up_date,
      status: item.status === 'COMPLETED' ? 'Completed' : 'Due',
      notes: item.notes,
      history: []
    }));
  }

  async getInterventionById(id: string): Promise<Intervention | undefined> {
    const res = await fetchWithAuth(`/interventions/${id}`);
    if (!res.ok) throw new Error('Failed to fetch intervention');
    const item = await res.json();
    return {
      id: item.id,
      personnelId: item.personnel_id,
      unitId: 'Unknown',
      actionType: item.action_type,
      assignedOfficer: 'Assigned Officer',
      createdAt: item.created_at,
      followUpDate: item.follow_up_date,
      status: item.status === 'COMPLETED' ? 'Completed' : 'Due',
      notes: item.notes,
      history: []
    };
  }

  async createIntervention(data: Partial<Intervention>): Promise<Intervention> {
    const res = await fetchWithAuth('/interventions', {
      method: 'POST',
      body: JSON.stringify({
        personnel_id: data.personnelId,
        action_type: data.actionType,
        notes: data.notes,
        follow_up_date: data.followUpDate
      })
    });
    if (!res.ok) throw new Error('Failed to create intervention');
    const item = await res.json();
    return {
      id: item.id,
      personnelId: item.personnel_id,
      unitId: 'Unknown',
      actionType: item.action_type,
      assignedOfficer: '',
      createdAt: item.created_at,
      followUpDate: item.follow_up_date,
      status: 'Upcoming',
      notes: item.notes,
      history: []
    };
  }

  async updateIntervention(id: string, updates: Partial<Intervention>): Promise<void> {
    // Only status and notes are supported in backend PATCH /interventions/{id}
    const payload: any = {};
    if (updates.status === 'Completed') payload.status = 'COMPLETED';
    else if (updates.status === 'Upcoming' || updates.status === 'Rescheduled' || updates.status === 'Due') payload.status = 'PENDING';
    
    if (updates.notes) payload.resolution_notes = updates.notes;

    const res = await fetchWithAuth(`/interventions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to update intervention');
  }

  async completeIntervention(id: string): Promise<void> {
    await this.updateIntervention(id, { status: 'Completed' });
  }

  async rescheduleIntervention(id: string, newDate: string): Promise<void> {
    // Backend doesn't support changing date in PATCH directly currently, just status. 
    // We update status to keep it from failing, ideally we'd update date if backend supports it.
    await this.updateIntervention(id, { status: 'Rescheduled' });
  }
}

export const interventionService = new InterventionService();
