// User and Authentication Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  is_verified: boolean;
  is_active: boolean;
  is_staff?: boolean;
  is_admin?: boolean;
  is_seller?: boolean;
  date_joined: string;
  last_login?: string;
  avatar?: string;
}

export interface SellerProfile {
  id: number;
  user: User;
  business_name: string;
  business_description?: string;
  business_address?: string;
  business_phone?: string;
  business_email?: string;
  business_website?: string;
  business_logo?: string;
  is_verified: boolean;
  is_active: boolean;
  commission_rate: number;
  total_sales: number;
  rating: number;
  review_count: number;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  sellerProfile: SellerProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Product Types
export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  parent?: Category;
  children: Category[];
  product_count: number;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  logo?: string;
  website?: string;
  product_count: number;
}

export interface ProductImage {
  id: number;
  image: string;
  alt_text?: string;
  is_primary: boolean;
  order: number;
}

export interface ProductVariant {
  id: number;
  name: string;
  value: string;
  price_adjustment: number;
  stock_quantity: number;
  sku: string;
}

export interface ProductReview {
  id: number;
  product: number;
  user: User;
  rating: number;
  title?: string;
  comment?: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  short_description?: string;
  price: number;
  compare_price?: number;
  cost_price?: number;
  sku: string;
  barcode?: string;
  weight?: number;
  dimensions?: string;
  category: Category;
  brand?: Brand;
  seller: SellerProfile;
  status: 'draft' | 'pending' | 'active' | 'inactive' | 'rejected';
  condition: 'new' | 'used' | 'refurbished';
  is_featured: boolean;
  is_approved: boolean;
  stock_quantity: number;
  min_stock_alert: number;
  max_purchase_quantity?: number;
  tags: string[];
  meta_title?: string;
  meta_description?: string;
  images: ProductImage[];
  variants: ProductVariant[];
  reviews: ProductReview[];
  average_rating: number;
  review_count: number;
  view_count: number;
  sold_count: number;
  created_at: string;
  updated_at: string;
}

// Cart and Order Types
export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  variant?: ProductVariant;
  price: number;
  total_price: number;
  added_at: string;
}

export interface Cart {
  id: number;
  user: User;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  discount_amount: number;
  total_amount: number;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id: number;
  order: number;
  product: Product;
  variant?: ProductVariant;
  quantity: number;
  unit_price: number;
  total_price: number;
  seller: SellerProfile;
}

export interface OrderStatus {
  id: number;
  order: number;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'returned';
  comment?: string;
  created_at: string;
}

export interface Order {
  id: number;
  order_number: string;
  user: User;
  items: OrderItem[];
  status: string;
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  discount_amount: number;
  total_amount: number;
  shipping_address: Address;
  billing_address: Address;
  payment_method: string;
  notes?: string;
  estimated_delivery?: string;
  created_at: string;
  updated_at: string;
}

// Address Types
export interface Address {
  id: number;
  user: User;
  type: 'shipping' | 'billing';
  first_name: string;
  last_name: string;
  company?: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// Payment Types
export interface PaymentMethod {
  id: number;
  user: User;
  type: 'card' | 'bank_account' | 'paypal';
  provider: string;
  last_four?: string;
  expiry_month?: number;
  expiry_year?: number;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

export interface Payment {
  id: number;
  order: Order;
  amount: number;
  currency: string;
  payment_method: PaymentMethod;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  transaction_id?: string;
  gateway_response?: any;
  created_at: string;
  updated_at: string;
}

// Shipping Types
export interface ShippingZone {
  id: number;
  name: string;
  countries: string[];
  states?: string[];
  postal_codes?: string[];
  is_active: boolean;
}

export interface ShippingMethod {
  id: number;
  name: string;
  description?: string;
  zone: ShippingZone;
  is_active: boolean;
  handling_fee: number;
  min_order_amount?: number;
  max_order_amount?: number;
}

export interface ShippingRate {
  id: number;
  method: ShippingMethod;
  zone: ShippingZone;
  weight_min?: number;
  weight_max?: number;
  price: number;
  is_active: boolean;
}

export interface Shipment {
  id: number;
  order: Order;
  tracking_number: string;
  carrier: string;
  method: ShippingMethod;
  status: 'pending' | 'shipped' | 'in_transit' | 'delivered' | 'failed';
  shipped_at?: string;
  delivered_at?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Notification Types
export interface Notification {
  id: number;
  user: User;
  type: 'order' | 'payment' | 'shipping' | 'promotion' | 'system';
  title: string;
  message: string;
  is_read: boolean;
  data?: any;
  created_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
}

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select' | 'checkbox' | 'radio';
  placeholder?: string;
  required?: boolean;
  options?: { value: string; label: string }[];
  validation?: {
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    custom?: (value: any) => string | true;
  };
}

// Component Props Types
export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface InputProps {
  name: string;
  label?: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface CardProps {
  children: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

// Store Types
export interface CartState {
  items: CartItem[];
  totalItems: number;
  subtotal: number;
  taxAmount: number;
  shippingAmount: number;
  discountAmount: number;
  totalAmount: number;
  isLoading: boolean;
  error: string | null;
}

export interface RootState {
  auth: AuthState;
  cart: CartState;
}
