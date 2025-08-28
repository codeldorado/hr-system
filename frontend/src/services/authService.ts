import { apiService } from './api';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    employee_id: number;
    name: string;
    email: string;
    role: 'employee' | 'hr_manager' | 'administrator' | 'auditor';
  };
}

interface User {
  id: number;
  employee_id: number;
  name: string;
  email: string;
  role: string;
}

class AuthService {
  async login(email: string, password: string): Promise<LoginResponse> {
    // For demo purposes, simulate authentication
    // In production, this would call the actual auth service
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email === 'demo@company.com' && password === 'demo123') {
          resolve({
            access_token: 'demo-jwt-token-' + Date.now(),
            token_type: 'bearer',
            user: {
              id: 1,
              employee_id: 123,
              name: 'Demo User',
              email: 'demo@company.com',
              role: 'employee',
            },
          });
        } else if (email === 'hr@company.com' && password === 'hr123') {
          resolve({
            access_token: 'hr-jwt-token-' + Date.now(),
            token_type: 'bearer',
            user: {
              id: 2,
              employee_id: 456,
              name: 'HR Manager',
              email: 'hr@company.com',
              role: 'hr_manager',
            },
          });
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 1000);
    });
  }

  async getCurrentUser(): Promise<User> {
    return apiService.get<User>('/auth/me');
  }

  async refreshToken(): Promise<LoginResponse> {
    return apiService.post<LoginResponse>('/auth/refresh');
  }

  logout(): void {
    localStorage.removeItem('auth_token');
  }
}

export const authService = new AuthService();
