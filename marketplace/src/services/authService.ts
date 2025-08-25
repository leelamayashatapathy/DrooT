import api from './api';
import { User, LoginCredentials, RegisterData, AuthState } from '../types';

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

class AuthService {
  // Login user
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post('/auth/login/', credentials);
    const data = response.data as any;
    const access = data?.access ?? data?.tokens?.access;
    const refresh = data?.refresh ?? data?.tokens?.refresh;
    const user = data?.user;
    return { access, refresh, user } as LoginResponse;
  }

  // Register user
  async register(userData: RegisterData): Promise<RegisterResponse> {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  }

  // Logout user
  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh_token: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  // Get current user profile
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/profile/');
    return response.data;
  }

  // Update user profile
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await api.put('/auth/profile/', userData);
    return response.data;
  }

  // Change password
  async changePassword(passwordData: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }): Promise<{ message: string }> {
    const response = await api.post('/auth/password/change/', passwordData);
    return response.data;
  }

  // Request password reset
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await api.post('/auth/password/reset/', { email });
    return response.data;
  }

  // Confirm password reset
  async confirmPasswordReset(
    token: string,
    new_password: string,
    new_password_confirm: string
  ): Promise<{ message: string }> {
    const response = await api.post('/auth/password/reset/confirm/', {
      token,
      new_password,
      new_password_confirm,
    });
    return response.data;
  }

  // Verify phone number
  async verifyPhone(phone: string, otp: string): Promise<{ message: string }> {
    const response = await api.post('/auth/verify-phone/', { phone, otp });
    return response.data;
  }

  // Resend OTP
  async resendOTP(phone: string): Promise<{ message: string }> {
    const response = await api.post('/auth/resend-otp/', { phone });
    return response.data;
  }

  // Create seller profile
  async createSellerProfile(sellerData: {
    business_name: string;
    business_description?: string;
    business_address?: string;
    business_phone?: string;
    business_email?: string;
    business_website?: string;
  }): Promise<any> {
    const response = await api.post('/sellers/profile/', sellerData);
    return response.data;
  }

  // Get seller profile
  async getSellerProfile(): Promise<any> {
    const response = await api.get('/sellers/profile/');
    return response.data;
  }

  // Update seller profile
  async updateSellerProfile(sellerData: any): Promise<any> {
    const response = await api.put('/sellers/profile/', sellerData);
    return response.data;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  // Get stored user data
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        return null;
      }
    }
    return null;
  }

  // Store user data
  storeUserData(user: User, accessToken: string, refreshToken: string): void {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  // Clear stored data
  clearStoredData(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export default new AuthService();
