import React, { createContext, useContext, ReactNode } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { CartItem, Product, ProductVariant } from '../types';
import { toast } from 'react-hot-toast';

interface CartStore {
  items: CartItem[];
  totalItems: number;
  subtotal: number;
  taxAmount: number;
  shippingAmount: number;
  discountAmount: number;
  totalAmount: number;
  isLoading: boolean;
  error: string | null;

  // Actions
  addToCart: (product: Product, quantity: number, variant?: ProductVariant) => void;
  removeFromCart: (itemId: number) => void;
  updateQuantity: (itemId: number, quantity: number) => void;
  clearCart: () => void;
  calculateTotals: () => void;
  setShippingAmount: (amount: number) => void;
  setDiscountAmount: (amount: number) => void;
  setTaxAmount: (amount: number) => void;
}

const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      totalItems: 0,
      subtotal: 0,
      taxAmount: 0,
      shippingAmount: 0,
      discountAmount: 0,
      totalAmount: 0,
      isLoading: false,
      error: null,

      addToCart: (product: Product, quantity: number, variant?: ProductVariant) => {
        const { items } = get();
        const existingItemIndex = items.findIndex(
          item => item.product.id === product.id && 
          (!variant || item.variant?.id === variant.id)
        );

        if (existingItemIndex > -1) {
          // Update existing item quantity
          const updatedItems = [...items];
          const newQuantity = updatedItems[existingItemIndex].quantity + quantity;
          
          if (newQuantity > (variant?.stock_quantity || product.stock_quantity)) {
            toast.error('Not enough stock available');
            return;
          }
          
          updatedItems[existingItemIndex].quantity = newQuantity;
          updatedItems[existingItemIndex].total_price = 
            (variant ? product.price + variant.price_adjustment : product.price) * newQuantity;
          
          set({ items: updatedItems });
          toast.success('Cart updated successfully');
        } else {
          // Add new item
          if (quantity > (variant?.stock_quantity || product.stock_quantity)) {
            toast.error('Not enough stock available');
            return;
          }

          const price = variant ? product.price + variant.price_adjustment : product.price;
          const newItem: CartItem = {
            id: Date.now(), // Temporary ID for local storage
            product,
            quantity,
            variant,
            price,
            total_price: price * quantity,
            added_at: new Date().toISOString(),
          };

          set({ items: [...items, newItem] });
          toast.success('Added to cart successfully');
        }

        get().calculateTotals();
      },

      removeFromCart: (itemId: number) => {
        const { items } = get();
        const updatedItems = items.filter(item => item.id !== itemId);
        set({ items: updatedItems });
        get().calculateTotals();
        toast.success('Item removed from cart');
      },

      updateQuantity: (itemId: number, quantity: number) => {
        const { items } = get();
        const itemIndex = items.findIndex(item => item.id === itemId);
        
        if (itemIndex > -1) {
          const item = items[itemIndex];
          const maxStock = item.variant?.stock_quantity || item.product.stock_quantity;
          
          if (quantity > maxStock) {
            toast.error('Not enough stock available');
            return;
          }
          
          if (quantity <= 0) {
            get().removeFromCart(itemId);
            return;
          }

          const updatedItems = [...items];
          updatedItems[itemIndex].quantity = quantity;
          updatedItems[itemIndex].total_price = item.price * quantity;
          
          set({ items: updatedItems });
          get().calculateTotals();
        }
      },

      clearCart: () => {
        set({ 
          items: [], 
          totalItems: 0, 
          subtotal: 0, 
          taxAmount: 0, 
          shippingAmount: 0, 
          discountAmount: 0, 
          totalAmount: 0 
        });
        toast.success('Cart cleared successfully');
      },

      calculateTotals: () => {
        const { items, taxAmount, shippingAmount, discountAmount } = get();
        
        const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
        const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);
        const totalAmount = subtotal + taxAmount + shippingAmount - discountAmount;

        set({
          totalItems,
          subtotal,
          totalAmount,
        });
      },

      setShippingAmount: (amount: number) => {
        set({ shippingAmount: amount });
        get().calculateTotals();
      },

      setDiscountAmount: (amount: number) => {
        set({ discountAmount: amount });
        get().calculateTotals();
      },

      setTaxAmount: (amount: number) => {
        set({ taxAmount: amount });
        get().calculateTotals();
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({
        items: state.items,
        totalItems: state.totalItems,
        subtotal: state.subtotal,
        taxAmount: state.taxAmount,
        shippingAmount: state.shippingAmount,
        discountAmount: state.discountAmount,
        totalAmount: state.totalAmount,
      }),
    }
  )
);

// Context for backward compatibility (optional)
const CartContext = createContext<CartStore | null>(null);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const cartStore = useCartStore();

  return (
    <CartContext.Provider value={cartStore}>
      {children}
    </CartContext.Provider>
  );
};

export { useCartStore };
