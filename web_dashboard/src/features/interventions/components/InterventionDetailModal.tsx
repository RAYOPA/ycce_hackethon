import React, { useState } from 'react';
import { X, Calendar, Edit2, CheckCircle, Clock } from 'lucide-react';
import type { Intervention } from '../models/intervention';
import { interventionService } from '../services/interventionService';
import { format } from 'date-fns';

interface InterventionDetailModalProps {
  intervention: Intervention | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export const InterventionDetailModal: React.FC<InterventionDetailModalProps> = ({ intervention, isOpen, onClose, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isRescheduling, setIsRescheduling] = useState(false);
  
  // Edit State
  const [actionType, setActionType] = useState('');
  const [assignedOfficer, setAssignedOfficer] = useState('');
  const [notes, setNotes] = useState('');
  const [newDate, setNewDate] = useState('');
  const [status, setStatus] = useState<any>('');
  
  const [submitting, setSubmitting] = useState(false);

  React.useEffect(() => {
    if (intervention) {
      setActionType(intervention.actionType);
      setAssignedOfficer(intervention.assignedOfficer);
      setNotes(intervention.notes);
      setStatus(intervention.status);
      setNewDate(intervention.followUpDate.split('T')[0]);
      setIsEditing(false);
      setIsRescheduling(false);
    }
  }, [intervention]);

  if (!isOpen || !intervention) return null;

  const handleSaveEdit = async () => {
    setSubmitting(true);
    await interventionService.updateIntervention(intervention.id, {
      actionType,
      assignedOfficer,
      notes,
      status
    });
    setSubmitting(false);
    setIsEditing(false);
    onUpdate();
  };

  const handleMarkComplete = async () => {
    setSubmitting(true);
    await interventionService.completeIntervention(intervention.id);
    setSubmitting(false);
    onUpdate();
    onClose();
  };

  const handleReschedule = async () => {
    setSubmitting(true);
    await interventionService.rescheduleIntervention(intervention.id, new Date(newDate).toISOString());
    setSubmitting(false);
    setIsRescheduling(false);
    onUpdate();
  };

  const getStatusColor = (s: string) => {
    switch(s) {
      case 'Due': return 'text-attention-700 bg-attention-100 border-attention-200';
      case 'Upcoming': return 'text-secondary-teal bg-positive-light border-positive';
      case 'In Progress': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'Completed': return 'text-slate-600 bg-slate-100 border-slate-200';
      case 'Rescheduled': return 'text-purple-700 bg-purple-50 border-purple-200';
      default: return 'text-slate-600 bg-slate-100 border-slate-200';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/50">
      <div className="bg-white shadow-xl h-full w-full max-w-md overflow-y-auto animate-in slide-in-from-right">
        
        {/* Header */}
        <div className="sticky top-0 bg-white z-10 flex justify-between items-center p-6 border-b border-slate-100">
          <div>
            <h2 className="text-xl font-bold text-primary-navy">Intervention Detail</h2>
            <p className="text-sm text-slate-500">{intervention.id}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-2 rounded-full hover:bg-slate-100">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          
          {/* Status Banner */}
          <div className={`p-4 rounded-lg border flex justify-between items-center ${getStatusColor(intervention.status)}`}>
            <span className="font-bold text-sm uppercase tracking-wider">{intervention.status}</span>
            <span className="text-sm font-medium">Due: {format(new Date(intervention.followUpDate), 'MMM d, yyyy')}</span>
          </div>

          {/* Details */}
          {!isEditing ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-500 mb-1">Personnel</p>
                  <p className="font-bold text-slate-800">{intervention.personnelId}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500 mb-1">Unit</p>
                  <p className="font-bold text-slate-800">{intervention.unitId}</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-500 mb-1">Action Type</p>
                <p className="font-bold text-slate-800">{intervention.actionType}</p>
              </div>

              <div>
                <p className="text-sm text-slate-500 mb-1">Assigned Officer</p>
                <p className="font-medium text-slate-800">{intervention.assignedOfficer}</p>
              </div>

              <div>
                <p className="text-sm text-slate-500 mb-1">Created</p>
                <p className="font-medium text-slate-800">{format(new Date(intervention.createdAt), 'MMM d, yyyy')}</p>
              </div>

              <div>
                <p className="text-sm text-slate-500 mb-1">Notes</p>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 text-sm text-slate-700 whitespace-pre-wrap">
                  {intervention.notes || 'No notes provided.'}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 bg-slate-50 p-4 rounded-lg border border-slate-200">
              <h3 className="font-bold text-slate-800 mb-4">Edit Intervention</h3>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
                <select 
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                  value={status}
                  onChange={e => setStatus(e.target.value)}
                >
                  <option>Due</option>
                  <option>Upcoming</option>
                  <option>In Progress</option>
                  <option>Completed</option>
                  <option>Rescheduled</option>
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
                <input 
                  type="text"
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal"
                  value={assignedOfficer}
                  onChange={e => setAssignedOfficer(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
                <textarea 
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-secondary-teal min-h-[100px]"
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                />
              </div>

              <div className="flex justify-end gap-2 mt-4">
                <button onClick={() => setIsEditing(false)} className="px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-200 rounded-md">Cancel</button>
                <button onClick={handleSaveEdit} disabled={submitting} className="px-3 py-1.5 text-sm font-medium bg-primary-navy text-white hover:bg-primary-navy/90 rounded-md">Save Changes</button>
              </div>
            </div>
          )}

          {/* Reschedule Box */}
          {isRescheduling && !isEditing && (
            <div className="space-y-4 bg-purple-50 p-4 rounded-lg border border-purple-200">
              <h3 className="font-bold text-purple-900">Reschedule Follow-up</h3>
              <div>
                <label className="block text-sm font-medium text-purple-800 mb-1">New Date</label>
                <input 
                  type="date"
                  className="w-full px-3 py-2 rounded-lg border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  value={newDate}
                  onChange={e => setNewDate(e.target.value)}
                />
              </div>
              <div className="flex justify-end gap-2 mt-4">
                <button onClick={() => setIsRescheduling(false)} className="px-3 py-1.5 text-sm font-medium text-purple-700 hover:bg-purple-200 rounded-md">Cancel</button>
                <button onClick={handleReschedule} disabled={submitting} className="px-3 py-1.5 text-sm font-medium bg-purple-700 text-white hover:bg-purple-800 rounded-md">Confirm</button>
              </div>
            </div>
          )}

          {/* Actions */}
          {!isEditing && !isRescheduling && intervention.status !== 'Completed' && (
            <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-100">
              <button 
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
              >
                <Edit2 size={16} /> Edit
              </button>
              <button 
                onClick={() => setIsRescheduling(true)}
                className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-slate-700 font-medium hover:bg-slate-50 transition-colors"
              >
                <Calendar size={16} /> Reschedule
              </button>
              <button 
                onClick={handleMarkComplete}
                disabled={submitting}
                className="flex items-center gap-2 px-4 py-2 bg-secondary-teal text-white rounded-lg font-medium hover:bg-secondary-teal/90 transition-colors ml-auto"
              >
                <CheckCircle size={16} /> Mark Complete
              </button>
            </div>
          )}

          {/* History Timeline */}
          <div className="pt-6 mt-6 border-t border-slate-100">
            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Clock size={16} /> Intervention History
            </h3>
            
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
              {intervention.history.map((event, idx) => (
                <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  
                  <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 border-white bg-slate-300 group-[.is-active]:bg-secondary-teal text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 ml-0.5"></div>
                  
                  <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-white p-3 rounded border border-slate-100 shadow-sm ml-4 md:ml-0 md:group-odd:mr-6 md:group-even:ml-6 text-sm">
                    <p className="font-bold text-slate-800">{event.status}</p>
                    <p className="text-xs text-slate-500 mb-1">{format(new Date(event.date), 'MMM d, yyyy h:mm a')}</p>
                    <p className="text-slate-600">{event.note}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
