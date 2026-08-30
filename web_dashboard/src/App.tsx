import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './features/auth/pages/LoginPage';
import { PersonnelPage } from './features/personnel/pages/PersonnelPage';
import { PersonnelDetailPage } from './features/personnel/pages/PersonnelDetailPage';
import { InterventionsPage } from './features/interventions/pages/InterventionsPage';
import { DashboardPage } from './features/dashboard/pages/DashboardPage';
import { AnalyticsPage } from './features/analytics/pages/AnalyticsPage';
import { WorkloadAnalyticsPage } from './features/workload/pages/WorkloadAnalyticsPage';
import { ReportsPage } from './features/reports/pages/ReportsPage';
import { NotificationsPage } from './features/notifications/pages/NotificationsPage';
import { SettingsPage } from './features/settings/pages/SettingsPage';
import { AdminPage } from './features/admin/pages/AdminPage';
import { Layout } from './layouts/Layout';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/" element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route index element={<Navigate to="/overview" replace />} />
              <Route path="overview" element={<DashboardPage />} />
              
              {/* Welfare Officer Only */}
              <Route element={<ProtectedRoute allowedRoles={['Welfare Officer']} />}>
                <Route path="personnel" element={<PersonnelPage />} />
                <Route path="personnel/:id" element={<PersonnelDetailPage />} />
                <Route path="interventions" element={<InterventionsPage />} />
              </Route>
              
              {/* Welfare Officer & Commander & Admin */}
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="workload" element={<WorkloadAnalyticsPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="settings" element={<SettingsPage />} />

              {/* Admin Only */}
              <Route element={<ProtectedRoute allowedRoles={['Administrator']} />}>
                <Route path="admin" element={<AdminPage />} />
              </Route>

              <Route path="*" element={<Navigate to="/overview" replace />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
