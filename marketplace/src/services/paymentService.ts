import api from './api';

export interface PaymentMethod {
  id: number;
  type: 'card' | 'bank_transfer' | 'digital_wallet';
  name: string;
  last4?: string;
  brand?: string;
  is_default: boolean;
  expiry_month?: number;
  expiry_year?: number;
}

export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'succeeded' | 'failed';
  payment_method: PaymentMethod;
  created_at: string;
}

export interface CreatePaymentIntentData {
  amount: number;
  currency: string;
  payment_method_id: number;
  order_id: number;
  description?: string;
}

export interface AddPaymentMethodData {
  type: 'card' | 'bank_transfer' | 'digital_wallet';
  card_number?: string;
  expiry_month?: number;
  expiry_year?: number;
  cvc?: string;
  name_on_card?: string;
  bank_account_number?: string;
  bank_routing_number?: string;
  account_holder_name?: string;
}

class PaymentService {
  // Get payment methods
  async getPaymentMethods(): Promise<PaymentMethod[]> {
    const response = await api.get('/payments/methods/');
    return response.data;
  }

  // Add payment method
  async addPaymentMethod(data: AddPaymentMethodData): Promise<PaymentMethod> {
    const response = await api.post('/payments/methods/', data);
    return response.data;
  }

  // Update payment method
  async updatePaymentMethod(id: number, data: Partial<AddPaymentMethodData>): Promise<PaymentMethod> {
    const response = await api.put(`/payments/methods/${id}/`, data);
    return response.data;
  }

  // Delete payment method
  async deletePaymentMethod(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/payments/methods/${id}/`);
    return response.data;
  }

  // Set default payment method
  async setDefaultPaymentMethod(id: number): Promise<{ message: string }> {
    const response = await api.patch(`/payments/methods/${id}/set-default/`);
    return response.data;
  }

  // Create payment intent
  async createPaymentIntent(data: CreatePaymentIntentData): Promise<PaymentIntent> {
    const response = await api.post('/payments/intents/', data);
    return response.data;
  }

  // Confirm payment intent
  async confirmPaymentIntent(intentId: string, paymentMethodId: number): Promise<PaymentIntent> {
    const response = await api.post(`/payments/intents/${intentId}/confirm/`, {
      payment_method_id: paymentMethodId,
    });
    return response.data;
  }

  // Get payment intent
  async getPaymentIntent(intentId: string): Promise<PaymentIntent> {
    const response = await api.get(`/payments/intents/${intentId}/`);
    return response.data;
  }

  // Cancel payment intent
  async cancelPaymentIntent(intentId: string): Promise<{ message: string }> {
    const response = await api.post(`/payments/intents/${intentId}/cancel/`);
    return response.data;
  }

  // Get payment history
  async getPaymentHistory(page: number = 1): Promise<{
    results: PaymentIntent[];
    count: number;
    next: string | null;
    previous: string | null;
  }> {
    const response = await api.get(`/payments/history/?page=${page}`);
    return response.data;
  }

  // Process refund
  async processRefund(paymentIntentId: string, amount: number, reason: string): Promise<{
    id: string;
    amount: number;
    status: string;
    reason: string;
  }> {
    const response = await api.post(`/payments/intents/${paymentIntentId}/refund/`, {
      amount,
      reason,
    });
    return response.data;
  }

  // Get payment statistics
  async getPaymentStatistics(): Promise<{
    total_payments: number;
    successful_payments: number;
    failed_payments: number;
    total_amount: number;
    average_amount: number;
  }> {
    const response = await api.get('/payments/statistics/');
    return response.data;
  }
}

export default new PaymentService();
