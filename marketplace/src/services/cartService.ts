import api from './api';
import { Cart, CartItem } from '../types';

export interface AddToCartData {
  product: number;
  variant?: number;
  quantity: number;
}

export interface UpdateCartItemData {
  quantity: number;
}

class CartService {
  // Get user's cart
  async getCart(): Promise<Cart> {
    const response = await api.get('/orders/cart/');
    return response.data;
  }

  // Add item to cart
  async addToCart(cartData: AddToCartData): Promise<CartItem> {
    const response = await api.post('/orders/cart/items/', cartData);
    return response.data;
  }

  // Update cart item quantity
  async updateCartItem(itemId: number, updateData: UpdateCartItemData): Promise<CartItem> {
    const response = await api.put(`/orders/cart/items/${itemId}/`, updateData);
    return response.data;
  }

  // Remove item from cart
  async removeFromCart(itemId: number): Promise<void> {
    await api.delete(`/orders/cart/items/${itemId}/`);
  }

  // Clear entire cart
  async clearCart(): Promise<void> {
    await api.delete('/orders/cart/');
  }

  // Get cart summary (total items, total amount)
  async getCartSummary(): Promise<{
    total_items: number;
    total_amount: number;
  }> {
    const response = await api.get('/orders/cart/summary/');
    return response.data;
  }

  // Apply coupon to cart
  async applyCoupon(couponCode: string): Promise<{
    message: string;
    discount_amount: number;
    total_amount: number;
  }> {
    const response = await api.post('/orders/cart/apply-coupon/', { coupon_code: couponCode });
    return response.data;
  }

  // Remove coupon from cart
  async removeCoupon(): Promise<{
    message: string;
    total_amount: number;
  }> {
    const response = await api.delete('/orders/cart/remove-coupon/');
    return response.data;
  }

  // Get shipping options for cart
  async getShippingOptions(address: {
    country: string;
    state: string;
    city: string;
    zip_code: string;
  }): Promise<any[]> {
    const response = await api.post('/orders/cart/shipping-options/', address);
    return response.data;
  }

  // Calculate shipping cost
  async calculateShipping(shippingMethodId: number): Promise<{
    shipping_cost: number;
    total_amount: number;
  }> {
    const response = await api.post('/orders/cart/calculate-shipping/', { 
      shipping_method: shippingMethodId 
    });
    return response.data;
  }

  // Get cart tax calculation
  async getTaxCalculation(): Promise<{
    tax_amount: number;
    total_amount: number;
  }> {
    const response = await api.get('/orders/cart/tax-calculation/');
    return response.data;
  }

  // Check cart item availability
  async checkAvailability(): Promise<{
    available_items: CartItem[];
    unavailable_items: CartItem[];
    messages: string[];
  }> {
    const response = await api.get('/orders/cart/check-availability/');
    return response.data;
  }

  // Save cart for later
  async saveForLater(): Promise<{
    message: string;
    saved_at: string;
  }> {
    const response = await api.post('/orders/cart/save-for-later/');
    return response.data;
  }

  // Get saved carts
  async getSavedCarts(): Promise<Cart[]> {
    const response = await api.get('/orders/cart/saved/');
    return response.data;
  }

  // Restore saved cart
  async restoreSavedCart(cartId: number): Promise<Cart> {
    const response = await api.post(`/orders/cart/saved/${cartId}/restore/`);
    return response.data;
  }

  // Merge guest cart with user cart (after login)
  async mergeGuestCart(guestCartData: any): Promise<Cart> {
    const response = await api.post('/orders/cart/merge-guest/', guestCartData);
    return response.data;
  }

  // Get cart recommendations
  async getRecommendations(): Promise<any[]> {
    const response = await api.get('/orders/cart/recommendations/');
    return response.data;
  }

  // Add multiple items to cart
  async addMultipleToCart(items: AddToCartData[]): Promise<CartItem[]> {
    const response = await api.post('/orders/cart/items/bulk/', { items });
    return response.data;
  }

  // Move item to wishlist
  async moveToWishlist(itemId: number): Promise<{
    message: string;
    wishlist_item_id: number;
  }> {
    const response = await api.post(`/orders/cart/items/${itemId}/move-to-wishlist/`);
    return response.data;
  }

  // Get cart analytics
  async getCartAnalytics(): Promise<{
    total_items_added: number;
    total_items_removed: number;
    average_cart_value: number;
    most_added_products: any[];
  }> {
    const response = await api.get('/orders/cart/analytics/');
    return response.data;
  }
}

export default new CartService();

