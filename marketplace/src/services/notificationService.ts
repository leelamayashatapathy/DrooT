import api from './api';

export interface Notification {
  id: number;
  user: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  category: 'order' | 'payment' | 'shipping' | 'promotion' | 'system';
  is_read: boolean;
  created_at: string;
  action_url?: string;
  metadata?: Record<string, any>;
}

export interface NotificationPreferences {
  id: number;
  user: number;
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  order_updates: boolean;
  payment_updates: boolean;
  shipping_updates: boolean;
  promotional_emails: boolean;
  newsletter: boolean;
}

export interface CreateNotificationData {
  title: string;
  message: string;
  type: Notification['type'];
  category: Notification['category'];
  action_url?: string;
  metadata?: Record<string, any>;
}

class NotificationService {
  // Get user notifications
  async getNotifications(page: number = 1, unreadOnly: boolean = false): Promise<{
    results: Notification[];
    count: number;
    next: string | null;
    previous: string | null;
  }> {
    const url = unreadOnly 
      ? `/notifications/?page=${page}&unread_only=true`
      : `/notifications/?page=${page}`;
    const response = await api.get(url);
    return response.data;
  }

  // Get notification by ID
  async getNotification(id: number): Promise<Notification> {
    const response = await api.get(`/notifications/${id}/`);
    return response.data;
  }

  // Mark notification as read
  async markAsRead(id: number): Promise<{ message: string }> {
    const response = await api.patch(`/notifications/${id}/mark-read/`);
    return response.data;
  }

  // Mark all notifications as read
  async markAllAsRead(): Promise<{ message: string }> {
    const response = await api.post('/notifications/mark-all-read/');
    return response.data;
  }

  // Delete notification
  async deleteNotification(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/notifications/${id}/`);
    return response.data;
  }

  // Delete all read notifications
  async deleteAllRead(): Promise<{ message: string }> {
    const response = await api.post('/notifications/delete-all-read/');
    return response.data;
  }

  // Get notification preferences
  async getPreferences(): Promise<NotificationPreferences> {
    const response = await api.get('/notifications/preferences/');
    return response.data;
  }

  // Update notification preferences
  async updatePreferences(preferences: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
    const response = await api.put('/notifications/preferences/', preferences);
    return response.data;
  }

  // Subscribe to notifications
  async subscribe(): Promise<{ message: string }> {
    const response = await api.post('/notifications/subscribe/');
    return response.data;
  }

  // Unsubscribe from notifications
  async unsubscribe(): Promise<{ message: string }> {
    const response = await api.post('/notifications/unsubscribe/');
    return response.data;
  }

  // Get unread count
  async getUnreadCount(): Promise<{ count: number }> {
    const response = await api.get('/notifications/unread-count/');
    return response.data;
  }

  // Send test notification
  async sendTestNotification(): Promise<{ message: string }> {
    const response = await api.post('/notifications/send-test/');
    return response.data;
  }

  // Get notification statistics
  async getStatistics(): Promise<{
    total_notifications: number;
    unread_notifications: number;
    read_notifications: number;
    notifications_by_type: Record<string, number>;
    notifications_by_category: Record<string, number>;
  }> {
    const response = await api.get('/notifications/statistics/');
    return response.data;
  }

  // Create notification (admin only)
  async createNotification(data: CreateNotificationData): Promise<Notification> {
    const response = await api.post('/notifications/create/', data);
    return response.data;
  }

  // Send bulk notifications (admin only)
  async sendBulkNotifications(data: {
    user_ids: number[];
    title: string;
    message: string;
    type: Notification['type'];
    category: Notification['category'];
  }): Promise<{ message: string; sent_count: number }> {
    const response = await api.post('/notifications/send-bulk/', data);
    return response.data;
  }
}

export default new NotificationService();
