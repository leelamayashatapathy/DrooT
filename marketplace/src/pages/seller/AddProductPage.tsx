import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { 
  Package, 
  Upload, 
  X, 
  Plus, 
  Save, 
  ArrowLeft,
  Image as ImageIcon
} from 'lucide-react';
import productService from '../../services/productService';
import { CreateProductData, CreateProductVariantData, CreateProductImageData } from '../../services/productService';
import { Category, Brand } from '../../types';

interface AddProductForm extends CreateProductData {
  variants: CreateProductVariantData[];
  images: File[];
}

const AddProductPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [imagePreviewUrls, setImagePreviewUrls] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors, isValid },
    setValue,
    reset,
  } = useForm<AddProductForm>({
    mode: 'onChange',
    defaultValues: {
      variants: [],
      images: [],
      condition: 'new',
      is_featured: false,
      min_stock_alert: 5,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'variants',
  });

  const watchedImages = watch('images');

  useEffect(() => {
    loadFormData();
  }, []);

  useEffect(() => {
    if (watchedImages) {
      const urls = Array.from(watchedImages).map(file => URL.createObjectURL(file));
      setImagePreviewUrls(urls);
      return () => urls.forEach(url => URL.revokeObjectURL(url));
    }
  }, [watchedImages]);

  const loadFormData = async () => {
    try {
      const [categoriesData, brandsData] = await Promise.all([
        productService.getCategories(),
        productService.getBrands(),
      ]);
      setCategories(categoriesData);
      setBrands(brandsData);
    } catch (error) {
      toast.error('Failed to load form data');
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setValue('images', files);
  };

  const removeImage = (index: number) => {
    const currentImages = watch('images');
    const newImages = currentImages.filter((_, i) => i !== index);
    setValue('images', newImages);
  };

  const addVariant = () => {
    append({
      name: '',
      value: '',
      price_adjustment: 0,
      stock_quantity: 0,
    });
  };

  const removeVariant = (index: number) => {
    remove(index);
  };

  const onSubmit = async (data: AddProductForm) => {
    setIsLoading(true);
    try {
      // Create product first
      const productData: CreateProductData = {
        name: data.name,
        description: data.description,
        short_description: data.short_description,
        base_price: data.base_price,
        sale_price: data.sale_price,
        cost_price: data.cost_price,
        stock_quantity: data.stock_quantity,
        min_stock_alert: data.min_stock_alert,
        category: data.category,
        brand: data.brand,
        condition: data.condition,
        weight: data.weight,
        dimensions: data.dimensions,
        tags: data.tags ? data.tags.split(',').map(tag => tag.trim()) : [],
        meta_title: data.meta_title,
        meta_description: data.meta_description,
      };

      const product = await productService.createProduct(productData);

      // Add variants if any
      if (data.variants.length > 0) {
        for (const variant of data.variants) {
          if (variant.name && variant.value) {
            await productService.addProductVariant(product.id, variant);
          }
        }
      }

      // Add images if any
      if (data.images.length > 0) {
        for (let i = 0; i < data.images.length; i++) {
          const imageData: CreateProductImageData = {
            image: data.images[i],
            alt_text: `${data.name} - Image ${i + 1}`,
            is_primary: i === 0,
            order: i,
          };
          await productService.addProductImage(product.id, imageData);
        }
      }

      toast.success('Product created successfully!');
      navigate('/seller/products');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to create product';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/seller/dashboard')}
            className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Add New Product</h1>
          <p className="text-gray-600 mt-2">
            Create a new product listing for your customers
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name *
                </label>
                <input
                  type="text"
                  {...register('name', { required: 'Product name is required' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter product name"
                />
                {errors.name && (
                  <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category *
                </label>
                <select
                  {...register('category', { required: 'Category is required' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="text-red-500 text-sm mt-1">{errors.category.message}</p>
                )}
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                {...register('description', { required: 'Description is required' })}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe your product in detail"
              />
              {errors.description && (
                <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
              )}
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Short Description
              </label>
              <input
                type="text"
                {...register('short_description')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Brief product summary"
                maxLength={500}
              />
            </div>
          </div>

          {/* Pricing & Inventory */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Pricing & Inventory</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Base Price (₹) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  {...register('base_price', { 
                    required: 'Base price is required',
                    min: { value: 0, message: 'Price must be positive' }
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0.00"
                />
                {errors.base_price && (
                  <p className="text-red-500 text-sm mt-1">{errors.base_price.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sale Price (₹)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  {...register('sale_price')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cost Price (₹)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  {...register('cost_price')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stock Quantity *
                </label>
                <input
                  type="number"
                  min="0"
                  {...register('stock_quantity', { 
                    required: 'Stock quantity is required',
                    min: { value: 0, message: 'Stock must be positive' }
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0"
                />
                {errors.stock_quantity && (
                  <p className="text-red-500 text-sm mt-1">{errors.stock_quantity.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Min Stock Alert
                </label>
                <input
                  type="number"
                  min="0"
                  {...register('min_stock_alert')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Condition *
                </label>
                <select
                  {...register('condition', { required: 'Condition is required' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="new">New</option>
                  <option value="used">Used</option>
                  <option value="refurbished">Refurbished</option>
                </select>
                {errors.condition && (
                  <p className="text-red-500 text-sm mt-1">{errors.condition.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Product Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Product Details</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brand
                </label>
                <select
                  {...register('brand')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select brand</option>
                  {brands.map((brand) => (
                    <option key={brand.id} value={brand.id}>
                      {brand.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Weight (kg)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  {...register('weight')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dimensions
              </label>
              <input
                type="text"
                {...register('dimensions')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., 10 x 5 x 2 cm"
              />
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <input
                type="text"
                {...register('tags')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Separate tags with commas"
              />
              <p className="text-sm text-gray-500 mt-1">
                Use tags to help customers find your product
              </p>
            </div>
          </div>

          {/* Product Variants */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Product Variants</h2>
              <button
                type="button"
                onClick={addVariant}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Variant
              </button>
            </div>

            {fields.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No variants added yet. Click "Add Variant" to create product variations.
              </p>
            ) : (
              <div className="space-y-4">
                {fields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-medium text-gray-900">Variant {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeVariant(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Name *
                        </label>
                        <input
                          type="text"
                          {...register(`variants.${index}.name` as const, { required: 'Variant name is required' })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., Size, Color"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Value *
                        </label>
                        <input
                          type="text"
                          {...register(`variants.${index}.value` as const, { required: 'Variant value is required' })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="e.g., Large, Red"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Price Adjustment (₹)
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          {...register(`variants.${index}.price_adjustment` as const)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="0.00"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Stock Quantity
                        </label>
                        <input
                          type="number"
                          min="0"
                          {...register(`variants.${index}.stock_quantity` as const)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="0"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Product Images */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Product Images</h2>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                id="product-images"
              />
              <label htmlFor="product-images" className="cursor-pointer">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Upload Product Images
                </p>
                <p className="text-gray-500">
                  Drag and drop images here, or click to select files
                </p>
                <p className="text-sm text-gray-400 mt-2">
                  PNG, JPG, GIF up to 10MB each
                </p>
              </label>
            </div>

            {imagePreviewUrls.length > 0 && (
              <div className="mt-6">
                <h4 className="font-medium text-gray-900 mb-4">Selected Images</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {imagePreviewUrls.map((url, index) => (
                    <div key={index} className="relative group">
                      <img
                        src={url}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-4 h-4" />
                      </button>
                      {index === 0 && (
                        <span className="absolute top-2 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* SEO & Marketing */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">SEO & Marketing</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Meta Title
                </label>
                <input
                  type="text"
                  {...register('meta_title')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="SEO title for search engines"
                  maxLength={60}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Recommended: 50-60 characters
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Meta Description
                </label>
                <textarea
                  {...register('meta_description')}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="SEO description for search engines"
                  maxLength={160}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Recommended: 150-160 characters
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  {...register('is_featured')}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm text-gray-700">
                  Feature this product on homepage
                </label>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/seller/dashboard')}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !isValid}
              className="px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating Product...
                </div>
              ) : (
                <div className="flex items-center">
                  <Save className="w-4 h-4 mr-2" />
                  Create Product
                </div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProductPage;


