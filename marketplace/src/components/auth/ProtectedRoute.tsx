import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSeller?: boolean;
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireSeller = false, 
  requireAdmin = false 
}) => {
  const { isAuthenticated, user, sellerProfile, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireSeller && !sellerProfile) {
    // Redirect to profile page if seller profile is required but doesn't exist
    return <Navigate to="/profile" replace />;
  }

  if (requireAdmin && user && !user.is_staff) {
    // Redirect to home page if admin access is required but user is not staff
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
