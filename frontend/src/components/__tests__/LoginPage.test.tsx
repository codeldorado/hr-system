import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import LoginPage from '../../pages/LoginPage';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock the auth service
jest.mock('../../services/authService', () => ({
  authService: {
    login: jest.fn(),
  },
}));

const theme = createTheme();
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </QueryClientProvider>
);

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByText('HR Platform')).toBeInTheDocument();
    expect(screen.getByText('Payslip Management System')).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('displays demo credentials', () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    expect(screen.getByText('Demo Credentials:')).toBeInTheDocument();
    expect(screen.getByText('Employee: demo@company.com / demo123')).toBeInTheDocument();
    expect(screen.getByText('HR Manager: hr@company.com / hr123')).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    // HTML5 validation should prevent submission
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    expect(emailInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  test('handles form submission', async () => {
    const mockLogin = require('../../services/authService').authService.login;
    mockLogin.mockResolvedValueOnce({
      access_token: 'test-token',
      user: { id: 1, name: 'Test User', role: 'employee' }
    });

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  test('displays error message on login failure', async () => {
    const mockLogin = require('../../services/authService').authService.login;
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  test('shows loading state during login', async () => {
    const mockLogin = require('../../services/authService').authService.login;
    mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // Should show loading spinner
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Form fields should be disabled
    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });

  test('disables form during loading', async () => {
    const mockLogin = require('../../services/authService').authService.login;
    mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <TestWrapper>
        <LoginPage />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
  });
});
