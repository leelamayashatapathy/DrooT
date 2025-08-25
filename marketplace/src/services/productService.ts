import api from './api';
import { Product, Category, Brand, ProductReview } from '../types';

export interface ProductFilters {
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  rating?: number;
  condition?: string;
  seller?: string;
  search?: string;
  is_featured?: boolean;
  deals?: boolean;
}

export interface ProductListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Product[];
}

export interface CreateProductData {
  name: string;
  description: string;
  short_description?: string;
  base_price: number;
  sale_price?: number;
  cost_price?: number;
  stock_quantity: number;
  min_stock_alert: number;
  category: number;
  brand?: number;
  condition: 'new' | 'used' | 'refurbished';
  weight?: number;
  dimensions?: string;
  tags?: string[];
  meta_title?: string;
  meta_description?: string;
}

export interface UpdateProductData extends Partial<CreateProductData> {
  id: number;
}

export interface CreateProductVariantData {
  name: string;
  value: string;
  price_adjustment: number;
  stock_quantity: number;
}

export interface CreateProductImageData {
  image: File;
  alt_text?: string;
  is_primary?: boolean;
  order?: number;
}

class ProductService {
  // Get all products with filters
  async getProducts(filters: ProductFilters = {}, page: number = 1): Promise<ProductListResponse> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    if (page > 1) {
      params.append('page', page.toString());
    }
    
    const response = await api.get(`/products/?${params.toString()}`);
    return response.data;
  }

  // Get featured products
  async getFeaturedProducts(limit: number = 8): Promise<Product[]> {
    const response = await api.get(`/products/?is_featured=true&page_size=${limit}`);
    return response.data.results;
  }

  // Get deals of the day
  async getDealsOfTheDay(limit: number = 4): Promise<Product[]> {
    const response = await api.get(`/products/?deals=true&page_size=${limit}`);
    return response.data.results;
  }

  // Get product by ID
  async getProduct(id: number): Promise<Product> {
    const response = await api.get(`/products/${id}/`);
    return response.data;
  }

  // Get product by slug
  async getProductBySlug(slug: string): Promise<Product> {
    const response = await api.get(`/products/slug/${slug}/`);
    return response.data;
  }

  // Get categories
  async getCategories(): Promise<Category[]> {
    const response = await api.get('/products/categories/');
    return response.data;
  }

  // Get brands
  async getBrands(): Promise<Brand[]> {
    const response = await api.get('/products/brands/');
    return response.data;
  }

  // Get products by category
  async getProductsByCategory(categorySlug: string, page: number = 1): Promise<ProductListResponse> {
    const response = await api.get(`/products/categories/${categorySlug}/products/?page=${page}`);
    return response.data;
  }

  // Get products by brand
  async getProductsByBrand(brandSlug: string, page: number = 1): Promise<ProductListResponse> {
    const response = await api.get(`/products/brands/${brandSlug}/products/?page=${page}`);
    return response.data;
  }

  // Search products
  async searchProducts(query: string, page: number = 1): Promise<ProductListResponse> {
    const response = await api.get(`/products/search/?q=${encodeURIComponent(query)}&page=${page}`);
    return response.data;
  }

  // Get related products
  async getRelatedProducts(productId: number, limit: number = 4): Promise<Product[]> {
    const response = await api.get(`/products/${productId}/related/?limit=${limit}`);
    return response.data;
  }

  // Get product reviews
  async getProductReviews(productId: number, page: number = 1): Promise<any> {
    const response = await api.get(`/products/${productId}/reviews/?page=${page}`);
    return response.data;
  }

  // Create product review
  async createProductReview(productId: number, reviewData: {
    rating: number;
    title?: string;
    comment: string;
  }): Promise<ProductReview> {
    const response = await api.post(`/products/${productId}/reviews/`, reviewData);
    return response.data;
  }

  // Update product review
  async updateProductReview(productId: number, reviewId: number, reviewData: {
    rating?: number;
    title?: string;
    comment?: string;
  }): Promise<ProductReview> {
    const response = await api.put(`/products/${productId}/reviews/${reviewId}/`, reviewData);
    return response.data;
  }

  // Delete product review
  async deleteProductReview(productId: number, reviewId: number): Promise<void> {
    await api.delete(`/products/${productId}/reviews/${reviewId}/`);
  }

  // Seller: Create product
  async createProduct(productData: CreateProductData): Promise<Product> {
    const formData = new FormData();
    
    Object.entries(productData).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(item => formData.append(key, item));
        } else {
          formData.append(key, value.toString());
        }
      }
    });
    
    const response = await api.post('/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Seller: Update product
  async updateProduct(productData: UpdateProductData): Promise<Product> {
    const { id, ...data } = productData;
    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(item => formData.append(key, item));
        } else {
          formData.append(key, value.toString());
        }
      }
    });
    
    const response = await api.put(`/products/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Seller: Delete product
  async deleteProduct(productId: number): Promise<void> {
    await api.delete(`/products/${productId}/`);
  }

  // Seller: Get seller products
  async getSellerProducts(page: number = 1): Promise<ProductListResponse> {
    const response = await api.get(`/products/seller/?page=${page}`);
    return response.data;
  }

  // Seller: Add product variant
  async addProductVariant(productId: number, variantData: CreateProductVariantData): Promise<any> {
    const response = await api.post(`/products/${productId}/variants/`, variantData);
    return response.data;
  }

  // Seller: Update product variant
  async updateProductVariant(productId: number, variantId: number, variantData: Partial<CreateProductVariantData>): Promise<any> {
    const response = await api.put(`/products/${productId}/variants/${variantId}/`, variantData);
    return response.data;
  }

  // Seller: Delete product variant
  async deleteProductVariant(productId: number, variantId: number): Promise<void> {
    await api.delete(`/products/${productId}/variants/${variantId}/`);
  }

  // Seller: Add product image
  async addProductImage(productId: number, imageData: CreateProductImageData): Promise<any> {
    const formData = new FormData();
    formData.append('image', imageData.image);
    if (imageData.alt_text) formData.append('alt_text', imageData.alt_text);
    if (imageData.is_primary !== undefined) formData.append('is_primary', imageData.is_primary.toString());
    if (imageData.order !== undefined) formData.append('order', imageData.order.toString());
    
    const response = await api.post(`/products/${productId}/images/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Seller: Update product image
  async updateProductImage(productId: number, imageId: number, imageData: Partial<CreateProductImageData>): Promise<any> {
    const formData = new FormData();
    
    if (imageData.image) formData.append('image', imageData.image);
    if (imageData.alt_text !== undefined) formData.append('alt_text', imageData.alt_text);
    if (imageData.is_primary !== undefined) formData.append('is_primary', imageData.is_primary.toString());
    if (imageData.order !== undefined) formData.append('order', imageData.order.toString());
    
    const response = await api.put(`/products/${productId}/images/${imageId}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Seller: Delete product image
  async deleteProductImage(productId: number, imageId: number): Promise<void> {
    await api.delete(`/products/${productId}/images/${imageId}/`);
  }

  // Seller: Update product status
  async updateProductStatus(productId: number, status: string): Promise<Product> {
    const response = await api.patch(`/products/${productId}/status/`, { status });
    return response.data;
  }

  // Seller: Update product stock
  async updateProductStock(productId: number, stockData: {
    stock_quantity: number;
    min_stock_alert?: number;
  }): Promise<Product> {
    const response = await api.patch(`/products/${productId}/stock/`, stockData);
    return response.data;
  }

  // Get product analytics
  async getProductAnalytics(productId: number): Promise<any> {
    const response = await api.get(`/products/${productId}/analytics/`);
    return response.data;
  }

  // Get trending products
  async getTrendingProducts(limit: number = 8): Promise<Product[]> {
    const response = await api.get(`/products/trending/?limit=${limit}`);
    return response.data;
  }

  // Get recently viewed products
  async getRecentlyViewedProducts(limit: number = 8): Promise<Product[]> {
    const response = await api.get(`/products/recently-viewed/?limit=${limit}`);
    return response.data;
  }

  // Mark product as viewed
  async markProductAsViewed(productId: number): Promise<void> {
    await api.post(`/products/${productId}/view/`);
  }
}

export default new ProductService();


