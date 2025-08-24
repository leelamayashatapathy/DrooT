import api from './api';
import { Order, OrderItem } from '../types';

export interface CreateOrderData {
  shipping_address: {
    first_name: string;
    last_name: string;
    company?: string;
    address_line1: string;
    address_line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
    phone: string;
  };
  billing_address?: {
    first_name: string;
    last_name: string;
    company?: string;
    address_line1: string;
    address_line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
    phone: string;
  };
  payment_method: number;
  shipping_method: number;
  notes?: string;
  coupon_code?: string;
}

export interface OrderFilters {
  status?: string;
  payment_status?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export interface OrderListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Order[];
}

class OrderService {
  // Create new order from cart
  async createOrder(orderData: CreateOrderData): Promise<Order> {
    const response = await api.post('/orders/', orderData);
    return response.data;
  }

  // Get user orders
  async getUserOrders(filters: OrderFilters = {}, page: number = 1): Promise<OrderListResponse> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    if (page > 1) {
      params.append('page', page.toString());
    }
    
    const response = await api.get(`/orders/?${params.toString()}`);
    return response.data;
  }

  // Get order by ID
  async getOrder(orderId: number): Promise<Order> {
    const response = await api.get(`/orders/${orderId}/`);
    return response.data;
  }

  // Get order by order number
  async getOrderByNumber(orderNumber: string): Promise<Order> {
    const response = await api.get(`/orders/number/${orderNumber}/`);
    return response.data;
  }

  // Cancel order
  async cancelOrder(orderId: number, reason: string): Promise<{
    message: string;
    order: Order;
  }> {
    const response = await api.post(`/orders/${orderId}/cancel/`, { reason });
    return response.data;
  }

  // Request order return
  async requestReturn(orderId: number, returnData: {
    reason: string;
    description: string;
    items: Array<{
      order_item: number;
      quantity: number;
      return_reason: string;
    }>;
  }): Promise<{
    message: string;
    return_request_id: number;
  }> {
    const response = await api.post(`/orders/${orderId}/return/`, returnData);
    return response.data;
  }

  // Get order tracking
  async getOrderTracking(orderId: number): Promise<any> {
    const response = await api.get(`/orders/${orderId}/tracking/`);
    return response.data;
  }

  // Get order invoice
  async getOrderInvoice(orderId: number): Promise<{
    invoice_url: string;
    invoice_number: string;
  }> {
    const response = await api.get(`/orders/${orderId}/invoice/`);
    return response.data;
  }

  // Download order invoice
  async downloadOrderInvoice(orderId: number): Promise<Blob> {
    const response = await api.get(`/orders/${orderId}/invoice/download/`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Get order history
  async getOrderHistory(orderId: number): Promise<any[]> {
    const response = await api.get(`/orders/${orderId}/history/`);
    return response.data;
  }

  // Add order note
  async addOrderNote(orderId: number, note: string): Promise<{
    message: string;
    note_id: number;
  }> {
    const response = await api.post(`/orders/${orderId}/notes/`, { note });
    return response.data;
  }

  // Get order notes
  async getOrderNotes(orderId: number): Promise<any[]> {
    const response = await api.get(`/orders/${orderId}/notes/`);
    return response.data;
  }

  // Reorder items from previous order
  async reorderFromOrder(orderId: number, items: number[]): Promise<{
    message: string;
    cart_items: any[];
  }> {
    const response = await api.post(`/orders/${orderId}/reorder/`, { items });
    return response.data;
  }

  // Get order analytics
  async getOrderAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    total_orders: number;
    total_spent: number;
    average_order_value: number;
    orders_by_status: Record<string, number>;
    spending_trend: any[];
  }> {
    const response = await api.get(`/orders/analytics/?period=${period}`);
    return response.data;
  }

  // Get order statistics
  async getOrderStatistics(): Promise<{
    total_orders: number;
    pending_orders: number;
    completed_orders: number;
    cancelled_orders: number;
    total_spent: number;
    average_order_value: number;
  }> {
    const response = await api.get('/orders/statistics/');
    return response.data;
  }

  // Get order recommendations
  async getOrderRecommendations(): Promise<any[]> {
    const response = await api.get('/orders/recommendations/');
    return response.data;
  }

  // Get order disputes
  async getOrderDisputes(orderId: number): Promise<any[]> {
    const response = await api.get(`/orders/${orderId}/disputes/`);
    return response.data;
  }

  // Create order dispute
  async createOrderDispute(orderId: number, disputeData: {
    reason: string;
    description: string;
    evidence_files?: File[];
  }): Promise<{
    message: string;
    dispute_id: number;
  }> {
    const formData = new FormData();
    formData.append('reason', disputeData.reason);
    formData.append('description', disputeData.description);
    
    if (disputeData.evidence_files) {
      disputeData.evidence_files.forEach(file => {
        formData.append('evidence_files', file);
      });
    }
    
    const response = await api.post(`/orders/${orderId}/disputes/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Get order shipping options
  async getOrderShippingOptions(orderId: number): Promise<any[]> {
    const response = await api.get(`/orders/${orderId}/shipping-options/`);
    return response.data;
  }

  // Update order shipping method
  async updateOrderShippingMethod(orderId: number, shippingMethodId: number): Promise<{
    message: string;
    order: Order;
  }> {
    const response = await api.patch(`/orders/${orderId}/shipping-method/`, {
      shipping_method: shippingMethodId,
    });
    return response.data;
  }

  // Get order payment methods
  async getOrderPaymentMethods(orderId: number): Promise<any[]> {
    const response = await api.get(`/orders/${orderId}/payment-methods/`);
    return response.data;
  }

  // Update order payment method
  async updateOrderPaymentMethod(orderId: number, paymentMethodId: number): Promise<{
    message: string;
    order: Order;
  }> {
    const response = await api.patch(`/orders/${orderId}/payment-method/`, {
      payment_method: paymentMethodId,
    });
    return response.data;
  }

  // Get order timeline
  async getOrderTimeline(orderId: number): Promise<any[]> {
    const response = await api.get(`/orders/${orderId}/timeline/`);
    return response.data;
  }

  // Rate order
  async rateOrder(orderId: number, ratingData: {
    overall_rating: number;
    delivery_rating: number;
    product_rating: number;
    comment?: string;
  }): Promise<{
    message: string;
    rating_id: number;
  }> {
    const response = await api.post(`/orders/${orderId}/rate/`, ratingData);
    return response.data;
  }

  // Get order rating
  async getOrderRating(orderId: number): Promise<any> {
    const response = await api.get(`/orders/${orderId}/rating/`);
    return response.data;
  }
}

export default new OrderService();

