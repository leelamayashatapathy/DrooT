import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireSeller?: boolean;
  requireAdmin?: boolean;
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requireSeller = false,
  requireAdmin = false,
  redirectTo = '/login',
}) => {
  const { isAuthenticated, user, sellerProfile, isLoading } = useAuthStore();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  if (requireAuth && !isAuthenticated) {
    // Save the attempted URL to redirect back after login
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check if user needs to be a seller
  if (requireSeller) {
    // If authenticated and explicitly marked as seller, allow even if sellerProfile hasn't loaded yet
    if (isAuthenticated && user?.is_seller) {
      return <>{children}</>;
    }
    // If not authenticated, go to login
    if (!isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    // If authenticated but no seller profile and not marked seller yet, redirect to create profile
    if (!sellerProfile) {
      return <Navigate to="/seller/profile/create" state={{ from: location }} replace />;
    }
  }

  // Check if user needs to be an admin
  if (requireAdmin && (!isAuthenticated || !user?.is_staff)) {
    if (!isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    if (!user?.is_staff) {
      return <Navigate to="/" replace />;
    }
  }

  // If all checks pass, render the children
  return <>{children}</>;
};

export default ProtectedRoute;
