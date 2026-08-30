import type { Intervention, InterventionStatus } from '../models/intervention';
import { addDays, subDays } from 'date-fns';

const generateMockInterventions = (): Intervention[] => {
  const interventions: Intervention[] = [];
  const units = ['Unit A', 'Unit B', 'Unit C', 'Unit D'];
  const actions = ['Workload Review', 'Recovery Support', 'Wellness Follow-up', 'General Welfare Support'];
  const officers = ['W001', 'W002', 'W003'];
  const statuses: InterventionStatus[] = ['Due', 'Upcoming', 'In Progress', 'Completed', 'Rescheduled'];

  const now = new Date();

  for (let i = 1; i <= 30; i++) {
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    let followUpDate = now;
    
    if (status === 'Due') {
      followUpDate = now;
    } else if (status === 'Upcoming' || status === 'Rescheduled') {
      followUpDate = addDays(now, Math.floor(Math.random() * 5) + 1);
    } else if (status === 'Completed') {
      followUpDate = subDays(now, Math.floor(Math.random() * 5) + 1);
    }

    const createdDate = subDays(followUpDate, Math.floor(Math.random() * 7) + 1);

    interventions.push({
      id: `INT-${i.toString().padStart(3, '0')}`,
      personnelId: `P${Math.floor(Math.random() * 50 + 1).toString().padStart(3, '0')}`,
      unitId: units[Math.floor(Math.random() * units.length)],
      actionType: actions[Math.floor(Math.random() * actions.length)],
      assignedOfficer: officers[Math.floor(Math.random() * officers.length)],
      createdAt: createdDate.toISOString(),
      followUpDate: followUpDate.toISOString(),
      status: status,
      notes: `Generated mock intervention note for ${status.toLowerCase()} status.`,
      history: [
        {
          status: 'Created',
          date: createdDate.toISOString(),
          note: 'Intervention created'
        },
        {
          status: status,
          date: new Date().toISOString(),
          note: `Status updated to ${status}`
        }
      ]
    });
  }

  return interventions;
};

export const MOCK_INTERVENTIONS = generateMockInterventions();
