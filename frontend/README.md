# Payslip Frontend

React TypeScript frontend for the HR Platform Payslip Management System.

## Features

- **Modern React**: Built with React 18 and TypeScript
- **Material-UI**: Professional UI components with responsive design
- **Authentication**: JWT-based authentication with role-based access control
- **File Upload**: Drag-and-drop PDF upload with progress tracking
- **Data Management**: React Query for efficient data fetching and caching
- **Responsive Design**: Mobile-friendly interface
- **Role-Based UI**: Different interfaces for employees, HR managers, and administrators

## User Roles

### Employee
- View own payslips
- Upload own payslips (if enabled)
- Dashboard with personal statistics

### HR Manager
- View all employee payslips
- Upload payslips for any employee
- Advanced filtering and search
- Bulk operations

### Administrator
- Full CRUD operations
- User management
- System configuration
- Delete payslips

## Quick Start

### Development Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Docker Development

```bash
# Start with Docker Compose
docker-compose --profile dev up frontend-dev

# Access at http://localhost:3001
```

### Production Build

```bash
# Build for production
npm run build

# Build Docker image
docker build -t payslip-frontend .

# Run production container
docker run -p 3000:80 payslip-frontend
```

## Demo Credentials

For testing purposes, use these demo credentials:

**Employee Account:**
- Email: `demo@company.com`
- Password: `demo123`

**HR Manager Account:**
- Email: `hr@company.com`
- Password: `hr123`

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Layout.tsx     # Main application layout
│   │   └── LoadingSpinner.tsx
│   ├── contexts/          # React contexts
│   │   └── AuthContext.tsx
│   ├── pages/             # Page components
│   │   ├── Dashboard.tsx
│   │   ├── LoginPage.tsx
│   │   ├── PayslipList.tsx
│   │   └── UploadPayslip.tsx
│   ├── services/          # API services
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   └── payslipService.ts
│   ├── App.tsx            # Main app component
│   └── index.tsx          # Entry point
├── Dockerfile             # Production Docker build
├── nginx.conf             # Nginx configuration
└── package.json           # Dependencies and scripts
```

## Key Components

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Role-based route protection
- Secure logout functionality

### File Upload
- Drag-and-drop interface
- PDF file validation
- Upload progress tracking
- File size validation (10MB limit)

### Data Management
- React Query for caching and synchronization
- Optimistic updates
- Error handling and retry logic
- Real-time data updates

### Responsive Design
- Mobile-first approach
- Material-UI breakpoints
- Adaptive navigation
- Touch-friendly interfaces

## API Integration

The frontend integrates with the FastAPI backend through:

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Current user info

### Payslip Endpoints
- `GET /payslips` - List payslips with filtering
- `POST /payslips` - Upload new payslip
- `GET /payslips/{id}` - Get specific payslip
- `DELETE /payslips/{id}` - Delete payslip (admin only)

### Error Handling
- Automatic token refresh on 401 errors
- User-friendly error messages
- Network error recovery
- Validation error display

## Environment Configuration

### Environment Variables

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Feature Flags
REACT_APP_ENABLE_UPLOAD=true
REACT_APP_ENABLE_DELETE=true
```

### Build Configuration

```json
{
  "homepage": "/",
  "proxy": "http://localhost:8000"
}
```

## Testing

### Unit Tests
```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

### E2E Tests
```bash
# Install Cypress
npm install --save-dev cypress

# Run E2E tests
npm run cypress:open
```

## Deployment

### Production Build
```bash
# Create optimized build
npm run build

# Serve build locally
npx serve -s build
```

### Docker Deployment
```bash
# Build production image
docker build -t payslip-frontend .

# Run container
docker run -p 80:80 payslip-frontend
```

### AWS Deployment
The frontend is deployed as a static site with:
- **S3**: Static file hosting
- **CloudFront**: CDN distribution
- **Route 53**: DNS management

## Performance Optimization

### Bundle Optimization
- Code splitting with React.lazy()
- Tree shaking for unused code
- Webpack bundle analysis
- Gzip compression

### Runtime Optimization
- React Query caching
- Memoization with useMemo/useCallback
- Virtual scrolling for large lists
- Image optimization

### Network Optimization
- API request batching
- Optimistic updates
- Background data fetching
- Service worker caching

## Security Features

### Client-Side Security
- XSS protection with Content Security Policy
- CSRF protection
- Secure cookie handling
- Input sanitization

### Authentication Security
- JWT token storage in memory
- Automatic token expiration
- Secure logout
- Role-based access control

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify TypeScript configuration

2. **API Connection Issues**
   - Check REACT_APP_API_URL configuration
   - Verify backend is running
   - Check CORS configuration

3. **Authentication Problems**
   - Clear browser storage
   - Check token expiration
   - Verify API credentials

### Debug Mode
```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start

# View network requests in browser dev tools
# Check console for error messages
```

---

**Built with React, TypeScript, and Material-UI for modern HR solutions**
