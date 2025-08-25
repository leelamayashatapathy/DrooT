import api from './api';

export interface ShippingZone {
  id: number;
  name: string;
  countries: string[];
  is_active: boolean;
}

export interface ShippingMethod {
  id: number;
  name: string;
  description: string;
  price: number;
  currency: string;
  estimated_days: string;
  is_active: boolean;
  zone: number;
}

export interface ShippingRate {
  id: number;
  method: ShippingMethod;
  price: number;
  currency: string;
  estimated_days: string;
}

export interface Address {
  id: number;
  first_name: string;
  last_name: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country: string;
  zip_code: string;
  phone: string;
  is_default: boolean;
}

export interface Shipment {
  id: number;
  order: number;
  tracking_number: string;
  carrier: string;
  status: 'pending' | 'shipped' | 'delivered' | 'returned';
  shipped_at?: string;
  delivered_at?: string;
  tracking_url?: string;
  address: Address;
  method: ShippingMethod;
}

export interface CalculateShippingData {
  origin_address: Address;
  destination_address: Address;
  items: Array<{
    weight: number;
    dimensions: {
      length: number;
      width: number;
      height: number;
    };
  }>;
}

class ShippingService {
  // Get shipping zones
  async getShippingZones(): Promise<ShippingZone[]> {
    const response = await api.get('/shipping/zones/');
    return response.data;
  }

  // Get shipping methods
  async getShippingMethods(zoneId?: number): Promise<ShippingMethod[]> {
    const url = zoneId ? `/shipping/methods/?zone=${zoneId}` : '/shipping/methods/';
    const response = await api.get(url);
    return response.data;
  }

  // Get shipping rates
  async getShippingRates(): Promise<ShippingRate[]> {
    const response = await api.get('/shipping/rates/');
    return response.data;
  }

  // Calculate shipping cost
  async calculateShipping(data: CalculateShippingData): Promise<ShippingRate[]> {
    const response = await api.post('/shipping/calculate/', data);
    return response.data;
  }

  // Get user addresses
  async getAddresses(): Promise<Address[]> {
    const response = await api.get('/shipping/addresses/');
    return response.data;
  }

  // Add new address
  async addAddress(data: Omit<Address, 'id'>): Promise<Address> {
    const response = await api.post('/shipping/addresses/create/', data);
    return response.data;
  }

  // Update address
  async updateAddress(id: number, data: Partial<Address>): Promise<Address> {
    const response = await api.put(`/shipping/addresses/${id}/update/`, data);
    return response.data;
  }

  // Delete address
  async deleteAddress(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/shipping/addresses/${id}/`);
    return response.data;
  }

  // Set default address
  async setDefaultAddress(id: number): Promise<{ message: string }> {
    const response = await api.patch(`/shipping/addresses/${id}/update/`, { is_default: true });
    return response.data;
  }

  // Get shipments
  async getShipments(page: number = 1): Promise<{
    results: Shipment[];
    count: number;
    next: string | null;
    previous: string | null;
  }> {
    const response = await api.get(`/shipping/shipments/?page=${page}`);
    return response.data;
  }

  // Create shipment
  async createShipment(data: {
    order: number;
    carrier: string;
    tracking_number: string;
    method: number;
    address: number;
  }): Promise<Shipment> {
    const response = await api.post('/shipping/shipments/create/', data);
    return response.data;
  }

  // Update shipment
  async updateShipment(id: number, data: Partial<Shipment>): Promise<Shipment> {
    const response = await api.put(`/shipping/shipments/${id}/update/`, data);
    return response.data;
  }

  // Get shipment details
  async getShipment(id: number): Promise<Shipment> {
    const response = await api.get(`/shipping/shipments/${id}/`);
    return response.data;
  }

  // Track shipment
  async trackShipment(shipmentId: number): Promise<{
    status: string;
    location: string;
    timestamp: string;
    description: string;
  }[]> {
    const response = await api.get(`/shipping/shipments/${shipmentId}/tracking/`);
    return response.data;
  }

  // Get shipping statistics
  async getShippingStatistics(): Promise<{
    total_shipments: number;
    delivered_shipments: number;
    pending_shipments: number;
    average_delivery_time: number;
  }> {
    const response = await api.get('/shipping/admin/statistics/');
    return response.data;
  }

  // Update shipping rates (admin only)
  async updateShippingRates(rates: Array<{
    method_id: number;
    new_price: number;
  }>): Promise<{ message: string }> {
    const response = await api.post('/shipping/admin/update-rates/', { rates });
    return response.data;
  }
}

export default new ShippingService();

