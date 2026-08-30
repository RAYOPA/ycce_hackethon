import React, { useState } from 'react';
import { X } from 'lucide-react';
import { interventionService } from '../services/interventionService';

interface CreateInterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateInterventionModal: React.FC<CreateInterventionModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [personnelId, setPersonnelId] = useState('P001');
  const [actionType, setActionType] = useState('Workload Review');
  const [assignedOfficer, setAssignedOfficer] = useState('W001');
  const [followUpDate, setFollowUpDate] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    await interventionService.createIntervention({
      personnelId,
      actionType,
      assignedOfficer,
      followUpDate,
      notes,
    });
    setSubmitting(false);
    onSuccess();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b border-slate-100">
          <h2 className="text-xl font-bold text-primary-navy">New Intervention</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Personnel ID</label>
              <select 
                className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                value={personnelId}
                onChange={e => setPersonnelId(e.target.value)}
              >
                <option>P001</option>
                <option>P002</option>
                <option>P003</option>
                <option>P004</option>
                <option>P014</option>
                <option>P021</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Action Type</label>
              <select 
                className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                value={actionType}
                onChange={e => setActionType(e.target.value)}
              >
                <option>Workload Review</option>
                <option>Recovery Support</option>
                <option>Wellness Follow-up</option>
                <option>General Welfare Support</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Assigned Officer</label>
              <select 
                className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                value={assignedOfficer}
                onChange={e => setAssignedOfficer(e.target.value)}
              >
                <option>W001</option>
                <option>W002</option>
                <option>W003</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Follow-up Date</label>
              <input 
                type="date"
                className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                value={followUpDate}
                onChange={e => setFollowUpDate(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
              <textarea 
                className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal min-h-[80px]"
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="Add contextual notes..."
              />
            </div>
          </div>
          
          <div className="mt-8 flex justify-end gap-3">
            <button 
              type="button" 
              onClick={onClose}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium"
            >
              Cancel
            </button>
            <button 
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-secondary-teal text-white rounded-lg hover:bg-secondary-teal/90 font-medium disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Create Intervention'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
