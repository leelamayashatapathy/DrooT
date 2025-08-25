import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import authService from '../services/authService';
import { User, SellerProfile, AuthState } from '../types';
import { toast } from 'react-hot-toast';

interface AuthStore extends AuthState {
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: any) => Promise<boolean>;
  logout: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<boolean>;
  changePassword: (passwordData: any) => Promise<boolean>;
  createSellerProfile: (sellerData: any) => Promise<boolean>;
  getSellerProfile: () => Promise<void>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
}

const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      sellerProfile: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login({ email, password });
          authService.storeUserData(response.user, response.access, response.refresh);
          
          // Set user and auth but keep loading until seller profile is fetched
          set({
            user: response.user,
            isAuthenticated: true,
            error: null,
          });

          try {
            await get().getSellerProfile();
          } catch (error) {
            console.log('No seller profile found');
          }

          set({ isLoading: false });
          toast.success('Login successful!');
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Login failed';
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
            user: null,
          });
          toast.error(errorMessage);
          return false;
        }
      },

      register: async (userData: any) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.register(userData);
          set({
            user: response.user,
            isAuthenticated: false, // User needs to login after registration
            isLoading: false,
            error: null,
          });
          toast.success('Registration successful! Please login.');
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Registration failed';
          set({
            error: errorMessage,
            isLoading: false,
          });
          toast.error(errorMessage);
          return false;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authService.logout();
          set({
            user: null,
            sellerProfile: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
          toast.success('Logged out successfully');
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      updateProfile: async (userData: Partial<User>) => {
        set({ isLoading: true, error: null });
        try {
          const updatedUser = await authService.updateProfile(userData);
          set({
            user: updatedUser,
            isLoading: false,
            error: null,
          });
          toast.success('Profile updated successfully');
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Profile update failed';
          set({
            error: errorMessage,
            isLoading: false,
          });
          toast.error(errorMessage);
          return false;
        }
      },

      changePassword: async (passwordData: any) => {
        set({ isLoading: true, error: null });
        try {
          await authService.changePassword(passwordData);
          set({ isLoading: false, error: null });
          toast.success('Password changed successfully');
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Password change failed';
          set({
            error: errorMessage,
            isLoading: false,
          });
          toast.error(errorMessage);
          return false;
        }
      },

      createSellerProfile: async (sellerData: any) => {
        set({ isLoading: true, error: null });
        try {
          const sellerProfile = await authService.createSellerProfile(sellerData);
          set({
            sellerProfile,
            isLoading: false,
            error: null,
          });
          toast.success('Seller profile created successfully');
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Seller profile creation failed';
          set({
            error: errorMessage,
            isLoading: false,
          });
          toast.error(errorMessage);
          return false;
        }
      },

      getSellerProfile: async () => {
        try {
          const sellerProfile = await authService.getSellerProfile();
          set({ sellerProfile });
        } catch (error) {
          // User might not have a seller profile
          set({ sellerProfile: null });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      initializeAuth: async () => {
        // Keep loading until seller profile fetch (if any) completes
        set({ isLoading: true });
        const storedUser = authService.getStoredUser();
        if (storedUser && authService.isAuthenticated()) {
          set({
            user: storedUser,
            isAuthenticated: true,
          });

          try {
            await get().getSellerProfile();
          } catch (error) {
            console.log('No seller profile found');
          }

          set({ isLoading: false });
        } else {
          set({
            user: null,
            sellerProfile: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        sellerProfile: state.sellerProfile,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Context for backward compatibility (optional)
const AuthContext = createContext<AuthStore | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const authStore = useAuthStore();

  useEffect(() => {
    authStore.initializeAuth();
  }, []);

  return (
    <AuthContext.Provider value={authStore}>
      {children}
    </AuthContext.Provider>
  );
};

export { useAuthStore };
