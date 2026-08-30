import type { Personnel } from '../models/personnel';
import { addDays, subDays } from 'date-fns';

const generateMockData = (): Personnel[] => {
  const personnel: Personnel[] = [];
  const units = ['Unit A', 'Unit B', 'Unit C', 'Unit D'];
  const trends: ('Improving' | 'Stable' | 'Rising')[] = ['Improving', 'Stable', 'Rising'];
  const followUps: ('Required' | 'Not Required' | 'Completed')[] = ['Required', 'Not Required', 'Completed'];

  for (let i = 1; i <= 50; i++) {
    const pId = `P${i.toString().padStart(3, '0')}`;
    const unit = units[i % units.length];
    
    // Generate trend data (30 days)
    const sleepHistory = Array.from({ length: 30 }, () => 6 + Math.random() * 3);
    const moodHistory = Array.from({ length: 30 }, () => 2 + Math.random() * 3);
    const workloadHistory = Array.from({ length: 30 }, () => 2 + Math.random() * 3);
    const stressHistory = Array.from({ length: 30 }, () => 1 + Math.random() * 4);

    const trend = trends[Math.floor(Math.random() * trends.length)];
    const aiIndicator = trend === 'Rising' ? 'Elevated' : trend === 'Stable' ? 'Moderate' : 'Lower';
    
    personnel.push({
      id: pId,
      personnelId: pId,
      unitId: unit,
      lastCheckIn: subDays(new Date(), Math.floor(Math.random() * 3)).toISOString(),
      wellnessTrend: trend,
      followUpStatus: followUps[Math.floor(Math.random() * followUps.length)],
      lastUpdated: new Date().toISOString(),
      sleepHistory,
      moodHistory,
      workloadHistory,
      stressHistory,
      personalBaseline: {
        typicalSleep: 7.0 + (Math.random() * 1.5 - 0.75),
        typicalWorkload: 3.0 + (Math.random() * 1.0 - 0.5),
        typicalMood: 3.5 + (Math.random() * 1.0 - 0.5),
        deviationDetected: trend === 'Rising',
      },
      mockAIAnalysis: {
        indicator: aiIndicator,
        confidence: 75 + Math.floor(Math.random() * 20),
        trend: trend === 'Rising' ? 'Increasing' : trend === 'Improving' ? 'Decreasing' : 'Stable',
      },
      mockFactors: trend === 'Rising' ? [
        { factor: 'Sleep deviation', impact: 10 + Math.floor(Math.random() * 15) },
        { factor: 'Workload', impact: 5 + Math.floor(Math.random() * 10) },
        { factor: 'Night duty', impact: 3 + Math.floor(Math.random() * 8) },
      ] : [
        { factor: 'Consistent sleep', impact: -10 },
        { factor: 'Balanced workload', impact: -5 },
      ]
    });
  }

  return personnel;
};

export const MOCK_PERSONNEL_DATA = generateMockData();
