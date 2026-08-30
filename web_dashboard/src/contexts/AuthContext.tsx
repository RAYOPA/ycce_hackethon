import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type UserRole = 'Welfare Officer' | 'Commander' | 'Administrator';

export interface AuthUser {
  id: string;
  name: string;
  role: UserRole;
  unit: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (role: UserRole) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    // Load from local storage for demo persistence
    const storedUser = localStorage.getItem('manrakshak_auth_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = (role: UserRole) => {
    // Mock user creation based on role
    const mockUser: AuthUser = {
      id: role === 'Administrator' ? 'A001' : role === 'Commander' ? 'C001' : 'W001',
      name: `Demo ${role}`,
      role,
      unit: role === 'Commander' ? 'All Units' : 'Unit A',
    };
    setUser(mockUser);
    localStorage.setItem('manrakshak_auth_user', JSON.stringify(mockUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('manrakshak_auth_user');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
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
