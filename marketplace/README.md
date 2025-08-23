# 🛍️ MarketPlace Frontend

A modern, responsive marketplace platform built with React, TypeScript, and Tailwind CSS.

## ✨ Features

- **Modern UI/UX**: Beautiful, responsive design with Tailwind CSS
- **TypeScript**: Full type safety and better development experience
- **JWT Authentication**: Secure user authentication and authorization
- **State Management**: Zustand for lightweight state management
- **Form Handling**: React Hook Form for efficient form management
- **Routing**: React Router for seamless navigation
- **API Integration**: Axios with interceptors for backend communication
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Component Library**: Reusable UI components with consistent styling

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (Django DRF)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd marketplace
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   Create a `.env.local` file in the root directory:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:5173`

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── layout/         # Layout components (Header, Footer)
│   └── ui/             # Generic UI components
├── pages/              # Page components
│   ├── auth/           # Authentication pages
│   ├── products/       # Product-related pages
│   ├── cart/           # Shopping cart pages
│   ├── checkout/       # Checkout pages
│   ├── user/           # User profile pages
│   ├── seller/         # Seller dashboard pages
│   └── admin/          # Admin dashboard pages
├── hooks/              # Custom React hooks
├── services/           # API services
├── store/              # State management (Zustand)
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── assets/             # Static assets
└── styles/             # Global styles and Tailwind config
```

## 🎨 Design System

### Colors
- **Primary**: Blue shades for main actions and branding
- **Secondary**: Gray shades for text and backgrounds
- **Success**: Green shades for positive actions
- **Warning**: Yellow/Orange shades for warnings
- **Error**: Red shades for errors and destructive actions

### Components
- **Buttons**: Multiple variants (primary, secondary, outline, etc.)
- **Forms**: Consistent input styling with validation states
- **Cards**: Flexible card components with headers, bodies, and footers
- **Badges**: Status indicators and labels

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🌐 API Integration

The frontend integrates with the Django DRF backend through:

- **Authentication**: JWT-based authentication
- **Products**: Product catalog and management
- **Orders**: Order processing and management
- **Payments**: Payment processing and management
- **Shipping**: Shipping calculations and tracking
- **User Management**: User profiles and settings

## 📱 Responsive Design

- **Mobile-first approach**
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Flexible grid system**
- **Touch-friendly interactions**

## 🔒 Security Features

- **JWT Token Management**
- **Automatic Token Refresh**
- **Protected Routes**
- **Input Validation**
- **XSS Protection**

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Environment Variables for Production
```env
VITE_API_URL=https://your-api-domain.com/api/v1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
