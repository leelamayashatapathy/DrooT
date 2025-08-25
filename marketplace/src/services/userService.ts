import api from './api';
import { User, Address } from '../types';

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  avatar?: File;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface AddressData {
  first_name: string;
  last_name: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country: string;
  zip_code: string;
  phone: string;
  is_default?: boolean;
}

class UserService {
  // Get user profile
  async getProfile(): Promise<User> {
    const response = await api.get('/auth/profile/');
    return response.data;
  }

  // Update user profile
  async updateProfile(data: UpdateProfileData): Promise<User> {
    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        if (key === 'avatar' && value instanceof File) {
          formData.append(key, value);
        } else if (typeof value === 'string') {
          formData.append(key, value);
        }
      }
    });

    const response = await api.put('/auth/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Change password
  async changePassword(data: ChangePasswordData): Promise<{ message: string }> {
    const response = await api.post('/auth/password/change/', data);
    return response.data;
  }

  // Request password reset
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await api.post('/auth/password/reset/', { email });
    return response.data;
  }

  // Confirm password reset
  async confirmPasswordReset(token: string, new_password: string): Promise<{ message: string }> {
    const response = await api.post('/auth/password/reset/confirm/', {
      token,
      new_password,
    });
    return response.data;
  }

  // Get user addresses
  async getAddresses(): Promise<Address[]> {
    const response = await api.get('/auth/addresses/');
    return response.data;
  }

  // Add new address
  async addAddress(data: AddressData): Promise<Address> {
    const response = await api.post('/auth/addresses/', data);
    return response.data;
  }

  // Update address
  async updateAddress(id: number, data: Partial<AddressData>): Promise<Address> {
    const response = await api.put(`/auth/addresses/${id}/`, data);
    return response.data;
  }

  // Delete address
  async deleteAddress(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/auth/addresses/${id}/`);
    return response.data;
  }

  // Set default address
  async setDefaultAddress(id: number): Promise<{ message: string }> {
    const response = await api.patch(`/auth/addresses/${id}/set-default/`);
    return response.data;
  }

  // Get user preferences
  async getPreferences(): Promise<any> {
    const response = await api.get('/auth/preferences/');
    return response.data;
  }

  // Update user preferences
  async updatePreferences(preferences: any): Promise<any> {
    const response = await api.put('/auth/preferences/', preferences);
    return response.data;
  }

  // Delete user account
  async deleteAccount(password: string): Promise<{ message: string }> {
    const response = await api.post('/auth/delete-account/', { password });
    return response.data;
  }
}

export default new UserService();

