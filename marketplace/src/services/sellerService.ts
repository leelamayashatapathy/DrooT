import api from './api';
import { Product, Order } from '../types';

export interface SellerProfile {
  id: number;
  user: number;
  business_name: string;
  gst_number?: string;
  is_verified: boolean;
  kyc_document?: string;
  bank_account_number?: string;
  bank_ifsc_code?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country: string;
  zip_code: string;
  phone: string;
  profile_image?: string;
  rating: number;
  total_orders: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateSellerProfileData {
  business_name: string;
  gst_number?: string;
  kyc_document?: File;
  bank_account_number?: string;
  bank_ifsc_code?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country: string;
  zip_code: string;
  phone: string;
  profile_image?: File;
}

export interface SellerAnalytics {
  total_products: number;
  total_orders: number;
  total_revenue: number;
  monthly_revenue: Array<{
    month: string;
    revenue: number;
  }>;
  top_products: Array<{
    product: Product;
    sales_count: number;
    revenue: number;
  }>;
  order_status_distribution: Record<string, number>;
}

class SellerService {
  // Get seller profile
  async getProfile(): Promise<SellerProfile> {
    const response = await api.get('/sellers/profile/');
    return response.data;
  }
  
  async registerSeller(data: any): Promise<any> {
    const response = await api.post('/sellers/register/', data);
    return response.data;
  }
  // Create seller profile
  async createProfile(data: CreateSellerProfileData): Promise<SellerProfile> {
    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        if (value instanceof File) {
          formData.append(key, value);
        } else if (typeof value === 'string') {
          formData.append(key, value);
        }
      }
    });

    const response = await api.post('/sellers/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Update seller profile
  async updateProfile(data: Partial<CreateSellerProfileData>): Promise<SellerProfile> {
    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        if (value instanceof File) {
          formData.append(key, value);
        } else if (typeof value === 'string') {
          formData.append(key, value);
        }
      }
    });

    const response = await api.put('/sellers/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Get seller dashboard
  async getDashboard(): Promise<{
    profile: SellerProfile;
    recent_orders: Order[];
    recent_products: Product[];
    quick_stats: {
      total_products: number;
      total_orders: number;
      total_revenue: number;
      pending_orders: number;
    };
  }> {
    const response = await api.get('/sellers/dashboard/');
    return response.data;
  }

  // Get seller products
  async getProducts(page: number = 1): Promise<{
    results: Product[];
    count: number;
    next: string | null;
    previous: string | null;
  }> {
    const response = await api.get(`/sellers/products/?page=${page}`);
    return response.data;
  }

  // Create product
  async createProduct(data: FormData): Promise<Product> {
    const response = await api.post('/sellers/products/create/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Get product details
  async getProduct(id: number): Promise<Product> {
    const response = await api.get(`/sellers/products/${id}/`);
    return response.data;
  }

  // Update product
  async updateProduct(id: number, data: FormData): Promise<Product> {
    const response = await api.put(`/sellers/products/${id}/update/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Delete product
  async deleteProduct(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/sellers/products/${id}/delete/`);
    return response.data;
  }

  // Get seller orders
  async getOrders(page: number = 1): Promise<{
    results: Order[];
    count: number;
    next: string | null;
    previous: string | null;
  }> {
    const response = await api.get(`/sellers/orders/?page=${page}`);
    return response.data;
  }

  // Get order details
  async getOrder(id: number): Promise<Order> {
    const response = await api.get(`/sellers/orders/${id}/`);
    return response.data;
  }

  // Update order status
  async updateOrderStatus(id: number, status: string): Promise<Order> {
    const response = await api.patch(`/sellers/orders/${id}/`, { status });
    return response.data;
  }

  // Get seller analytics
  async getAnalytics(): Promise<SellerAnalytics> {
    const response = await api.get('/sellers/analytics/');
    return response.data;
  }

  // Get seller statistics
  async getStatistics(): Promise<{
    total_products: number;
    total_orders: number;
    total_revenue: number;
    average_rating: number;
    total_customers: number;
  }> {
    const response = await api.get('/sellers/statistics/');
    return response.data;
  }

  // Verify seller account
  async verifyAccount(): Promise<{ message: string }> {
    const response = await api.post('/sellers/verify-account/');
    return response.data;
  }

  // Upload KYC document
  async uploadKYCDocument(document: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('kyc_document', document);

    const response = await api.post('/sellers/upload-kyc/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Get seller reviews
  async getReviews(page: number = 1): Promise<{
    results: Array<{
      id: number;
      user: {
        id: number;
        name: string;
        avatar?: string;
      };
      rating: number;
      comment: string;
      created_at: string;
    }>;
    count: number;
    next: string | null;
    previous: string | null;
  }> {
    const response = await api.get(`/sellers/reviews/?page=${page}`);
    return response.data;
  }
}

export default new SellerService();

