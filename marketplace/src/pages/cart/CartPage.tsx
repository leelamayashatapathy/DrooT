import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  ShoppingCart, 
  Trash2, 
  Plus, 
  Minus, 
  Heart, 
  ArrowRight,
  Truck,
  CreditCard,
  Shield,
  RefreshCw,
  X,
  Package
} from 'lucide-react';
import cartService from '../../services/cartService';
import { Cart, CartItem } from '../../types';

const CartPage: React.FC = () => {
  const navigate = useNavigate();
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingItems, setUpdatingItems] = useState<Set<number>>(new Set());
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState<any>(null);
  const [shippingOptions, setShippingOptions] = useState<any[]>([]);
  const [selectedShipping, setSelectedShipping] = useState<any>(null);

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    setIsLoading(true);
    try {
      const cartData = await cartService.getCart();
      setCart(cartData);
      
      // Fetch shipping options if cart has items
      if (cartData.items.length > 0) {
        // For now, use a default address - in a real app, this would come from user's saved addresses
        const defaultAddress = {
          country: 'US',
          state: 'CA',
          city: 'San Francisco',
          zip_code: '94102'
        };
        const shippingData = await cartService.getShippingOptions(defaultAddress);
        setShippingOptions(shippingData);
        if (shippingData.length > 0) {
          setSelectedShipping(shippingData[0]);
        }
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch cart';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const updateItemQuantity = async (itemId: number, quantity: number) => {
    if (quantity < 1) return;
    
    setUpdatingItems(prev => new Set(prev).add(itemId));
    try {
      await cartService.updateCartItem(itemId, { quantity });
      await fetchCart();
      toast.success('Cart updated successfully');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to update item';
      toast.error(errorMessage);
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  const removeItem = async (itemId: number) => {
    try {
      await cartService.removeFromCart(itemId);
      await fetchCart();
      toast.success('Item removed from cart');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to remove item';
      toast.error(errorMessage);
    }
  };

  const moveToWishlist = async (itemId: number) => {
    try {
      await cartService.moveToWishlist(itemId);
      await fetchCart();
      toast.success('Item moved to wishlist');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to move item';
      toast.error(errorMessage);
    }
  };

  const applyCoupon = async () => {
    if (!couponCode.trim()) return;
    
    try {
      const coupon = await cartService.applyCoupon(couponCode);
      setAppliedCoupon(coupon);
      await fetchCart();
      toast.success('Coupon applied successfully');
      setCouponCode('');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to apply coupon';
      toast.error(errorMessage);
    }
  };

  const removeCoupon = async () => {
    try {
      await cartService.removeCoupon();
      setAppliedCoupon(null);
      await fetchCart();
      toast.success('Coupon removed');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to remove coupon';
      toast.error(errorMessage);
    }
  };

  const clearCart = async () => {
    try {
      await cartService.clearCart();
      setCart(null);
      toast.success('Cart cleared');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to clear cart';
      toast.error(errorMessage);
    }
  };

  const handleCheckout = () => {
    navigate('/checkout');
  };

  const continueShopping = () => {
    navigate('/products');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading cart...</p>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
            <p className="text-gray-600 mb-6">
              Looks like you haven't added any items to your cart yet.
            </p>
            <button
              onClick={continueShopping}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Package className="w-5 h-5 mr-2" />
              Start Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-600 mt-2">
            {cart.items.length} item{cart.items.length !== 1 ? 's' : ''} in your cart
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">Cart Items</h2>
                  <button
                    onClick={clearCart}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Clear Cart
                  </button>
                </div>
              </div>

              <div className="divide-y divide-gray-200">
                {cart.items.map((item) => (
                  <div key={item.id} className="p-6">
                    <div className="flex items-start space-x-4">
                      {/* Product Image */}
                      <img
                        src={item.product.images[0]?.image || '/placeholder-product.jpg'}
                        alt={item.product.name}
                        className="w-20 h-20 rounded-lg object-cover"
                      />

                      {/* Product Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-medium text-gray-900">
                              {item.product.name}
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">
                              {item.product.short_description}
                            </p>
                            {item.variant && (
                              <p className="text-sm text-gray-500 mt-1">
                                Variant: {item.variant.name} - {item.variant.value}
                              </p>
                            )}
                            <p className="text-sm text-gray-500 mt-1">
                              Seller: {item.product.seller?.business_name || 'Unknown Seller'}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-lg font-semibold text-gray-900">
                              ${item.total_price.toFixed(2)}
                            </p>
                            <p className="text-sm text-gray-600">
                              ${item.price.toFixed(2)} each
                            </p>
                          </div>
                        </div>

                        {/* Quantity Controls */}
                        <div className="flex items-center justify-between mt-4">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => updateItemQuantity(item.id, item.quantity - 1)}
                              disabled={updatingItems.has(item.id) || item.quantity <= 1}
                              className="p-1 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <span className="w-12 text-center text-gray-900 font-medium">
                              {updatingItems.has(item.id) ? (
                                <RefreshCw className="w-4 h-4 animate-spin mx-auto" />
                              ) : (
                                item.quantity
                              )}
                            </span>
                            <button
                              onClick={() => updateItemQuantity(item.id, item.quantity + 1)}
                              disabled={updatingItems.has(item.id)}
                              className="p-1 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>

                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => moveToWishlist(item.id)}
                              className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                              title="Move to wishlist"
                            >
                              <Heart className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => removeItem(item.id)}
                              className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                              title="Remove item"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Continue Shopping */}
            <div className="mt-6">
              <button
                onClick={continueShopping}
                className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
              >
                <ArrowRight className="w-4 h-4 mr-2" />
                Continue Shopping
              </button>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow sticky top-8">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Order Summary</h2>
              </div>

              <div className="p-6 space-y-4">
                {/* Subtotal */}
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="text-gray-900">${cart.subtotal.toFixed(2)}</span>
                </div>

                {/* Shipping */}
                {selectedShipping && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Shipping</span>
                    <span className="text-gray-900">
                      {selectedShipping.price === 0 ? 'Free' : `$${selectedShipping.price.toFixed(2)}`}
                    </span>
                  </div>
                )}

                {/* Tax */}
                {cart.tax_amount > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Tax</span>
                    <span className="text-gray-900">${cart.tax_amount.toFixed(2)}</span>
                  </div>
                )}

                {/* Coupon Discount */}
                {appliedCoupon && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Discount ({appliedCoupon.code})</span>
                    <span className="text-green-600">-${cart.discount_amount.toFixed(2)}</span>
                  </div>
                )}

                {/* Total */}
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex justify-between text-lg font-semibold">
                    <span className="text-gray-900">Total</span>
                    <span className="text-gray-900">${cart.total_amount.toFixed(2)}</span>
                  </div>
                </div>

                {/* Coupon Code */}
                <div className="border-t border-gray-200 pt-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Coupon Code
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value)}
                        placeholder="Enter coupon code"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <button
                        onClick={applyCoupon}
                        disabled={!couponCode.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Apply
                      </button>
                    </div>
                    {appliedCoupon && (
                      <div className="flex items-center justify-between p-2 bg-green-50 rounded-lg">
                        <span className="text-sm text-green-800">
                          {appliedCoupon.code} applied
                        </span>
                        <button
                          onClick={removeCoupon}
                          className="text-green-600 hover:text-green-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Shipping Options */}
                {shippingOptions.length > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Shipping Method
                    </label>
                    <div className="space-y-2">
                      {shippingOptions.map((option) => (
                        <label key={option.id} className="flex items-center">
                          <input
                            type="radio"
                            name="shipping"
                            value={option.id}
                            checked={selectedShipping?.id === option.id}
                            onChange={() => setSelectedShipping(option)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          />
                          <div className="ml-3 flex-1">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-900">{option.name}</span>
                              <span className="text-sm text-gray-600">
                                {option.price === 0 ? 'Free' : `$${option.price.toFixed(2)}`}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500">{option.description}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                {/* Checkout Button */}
                <button
                  onClick={handleCheckout}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Proceed to Checkout
                </button>

                {/* Security Notice */}
                <div className="flex items-center justify-center text-xs text-gray-500">
                  <Shield className="w-4 h-4 mr-1" />
                  Secure checkout powered by Stripe
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
