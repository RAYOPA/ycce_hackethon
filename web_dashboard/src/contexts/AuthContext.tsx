import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_URL } from '../utils/api';

export type UserRole = 'Welfare Officer' | 'Commander' | 'Administrator' | 'Personnel';

export interface AuthUser {
  id: string;
  name: string;
  role: UserRole;
  unit: string;
  email: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (email: string, password?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load from local storage
    const storedUser = localStorage.getItem('manrakshak_auth_user');
    const token = localStorage.getItem('manrakshak_token');
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password = 'demo123') => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      localStorage.setItem('manrakshak_token', data.access_token);
      
      // Fetch current user details
      const userResp = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${data.access_token}` }
      });
      
      const userData = await userResp.json();
      
      // Map backend enums to frontend roles
      const roleMap: Record<string, UserRole> = {
        'ADMINISTRATOR': 'Administrator',
        'COMMANDER': 'Commander',
        'WELFARE_OFFICER': 'Welfare Officer',
        'PERSONNEL': 'Personnel'
      };

      const finalUser: AuthUser = {
        id: userData.id,
        name: userData.name,
        email: userData.email,
        role: roleMap[userData.role] || 'Personnel',
        unit: userData.unit?.unit_name || 'All Units',
      };

      setUser(finalUser);
      localStorage.setItem('manrakshak_auth_user', JSON.stringify(finalUser));
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('manrakshak_auth_user');
    localStorage.removeItem('manrakshak_token');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, isLoading }}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
