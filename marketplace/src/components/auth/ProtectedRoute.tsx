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
  const { isAuthenticated, user, sellerProfile, isLoading, getRedirectPath } = useAuthStore();
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
    if (!isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    
    // Check if user has seller role
    if (!user?.is_seller) {
      return <Navigate to="/" replace />;
    }
    
    // If user is seller but no profile, redirect to create profile
    if (!sellerProfile) {
      return <Navigate to="/seller/profile/create" state={{ from: location }} replace />;
    }
  }

  // Check if user needs to be an admin
  if (requireAdmin) {
    if (!isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
    
    if (!user?.is_staff && !user?.is_admin) {
      return <Navigate to="/" replace />;
    }
  }

  // If all checks pass, render the children
  return <>{children}</>;
};

export default ProtectedRoute;
