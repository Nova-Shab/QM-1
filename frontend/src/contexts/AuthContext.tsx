import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, LoginCredentials } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  canReview: boolean;
  canApprove: boolean;
  canEdit: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const response = await authApi.login(credentials);
    setToken(response.access_token);
    setUser(response.user);
    localStorage.setItem('token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  // Role-based permissions
  const reviewerRoles = ['admin', 'qa_reviewer', 'qa_approver', 'qp'];
  const approverRoles = ['admin', 'qa_approver', 'qp'];
  const editorRoles = ['admin', 'author', 'qa_reviewer', 'qa_approver', 'qp', 'ra', 'production'];

  const canReview = user ? reviewerRoles.includes(user.role) : false;
  const canApprove = user ? approverRoles.includes(user.role) : false;
  const canEdit = user ? editorRoles.includes(user.role) : false;
  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
        canReview,
        canApprove,
        canEdit,
        isAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
