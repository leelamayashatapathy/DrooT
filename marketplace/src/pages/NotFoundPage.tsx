import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Search, ShoppingCart, User } from 'lucide-react';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-200">404</h1>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Page Not Found</h2>
          <p className="text-gray-600">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="space-y-4 mb-8">
          <p className="text-sm text-gray-500">Here are some helpful links:</p>
          
          <div className="grid grid-cols-2 gap-4">
            <Link
              to="/"
              className="flex flex-col items-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <Home className="h-8 w-8 text-blue-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Home</span>
            </Link>

            <Link
              to="/products"
              className="flex flex-col items-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <Search className="h-8 w-8 text-green-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Products</span>
            </Link>

            <Link
              to="/cart"
              className="flex flex-col items-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <ShoppingCart className="h-8 w-8 text-orange-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Cart</span>
            </Link>

            <Link
              to="/profile"
              className="flex flex-col items-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <User className="h-8 w-8 text-purple-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Profile</span>
            </Link>
          </div>
        </div>

        <Link
          to="/"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Home className="h-4 w-4 mr-2" />
          Go Back Home
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
