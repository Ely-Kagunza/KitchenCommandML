# Kitchen ML Dashboard 🍽️

An intelligent machine learning platform for restaurant operations, providing demand forecasting, kitchen optimization, customer analytics, and inventory management.

![CI Pipeline](https://github.com/YOUR_USERNAME/kitchen-ml/workflows/CI%20Pipeline/badge.svg)
![Backend Tests](https://github.com/YOUR_USERNAME/kitchen-ml/workflows/Backend%20Tests/badge.svg)
![Frontend Tests](https://github.com/YOUR_USERNAME/kitchen-ml/workflows/Frontend%20Tests/badge.svg)

## 🌟 Features

### 📊 Demand Forecasting

- **Hourly & Daily Predictions**: Forecast customer demand for the next 24 hours or 7 days
- **Item-Level Analysis**: Predict demand for specific menu items
- **Category Insights**: Analyze demand patterns by menu category
- **Peak Hours Detection**: Identify top 3 peak hours for optimal staffing

### 🍳 Kitchen Optimization

- **Prep Time Prediction**: Estimate preparation times for menu items at specific stations
- **Batch Processing**: Optimize prep times for multiple orders
- **Bottleneck Detection**: Identify kitchen workflow bottlenecks
- **Station Performance**: Monitor and analyze kitchen station efficiency

### 👥 Customer Analytics

- **Churn Prediction**: Identify customers at risk of leaving
- **Lifetime Value (LTV)**: Calculate and predict customer lifetime value
- **Risk Segmentation**: Categorize customers by churn risk
- **High-Value Identification**: Find and retain your most valuable customers

### 📦 Inventory Management

- **Smart Recommendations**: Get data-driven reorder suggestions
- **Stock Optimization**: Minimize waste while preventing stockouts
- **Reorder Alerts**: Automated notifications for low-stock items
- **Waste Reduction**: Insights to reduce food waste

## 🏗️ Architecture

```
kitchen-ml/
├── backend/              # Python FastAPI backend
│   ├── src/
│   │   ├── api/         # API routes and middleware
│   │   ├── models/      # ML model definitions
│   │   ├── pipelines/   # Data processing pipelines
│   │   ├── services/    # Business logic services
│   │   ├── training/    # Model training scripts
│   │   └── utils/       # Utility functions
│   ├── tests/           # Backend tests
│   └── models/          # Trained ML models
│
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── stores/      # State management (Zustand)
│   │   ├── themes/      # Theme configurations
│   │   └── types/       # TypeScript types
│   └── tests/           # Frontend tests
│
└── .github/
    └── workflows/       # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.9+ with pip
- **Frontend**: Node.js 18+ with npm
- **Database**: PostgreSQL 12+

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the server
python main.py
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables (optional)
cp .env.example .env

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=src               # Run with coverage
pytest -v                      # Verbose output
```

**Test Results**: 17/17 tests passing ✅

### Frontend Tests

```bash
cd frontend
npm test                       # Run tests
npm run test:coverage         # Run with coverage
npm run lint                  # Run linting
npm run type-check            # TypeScript type checking
```

**Test Results**: 7/7 tests passing ✅

See [TEST_SUMMARY.md](TEST_SUMMARY.md) for detailed test information.

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI
- **ML Libraries**: scikit-learn, Prophet, XGBoost
- **Data Processing**: pandas, numpy
- **Database**: PostgreSQL with SQLAlchemy
- **Testing**: pytest, pytest-cov

### Frontend

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Charts**: Recharts
- **Styling**: Tailwind CSS
- **Testing**: Vitest, Testing Library

## 📊 ML Models

### Demand Forecasting

- **Algorithm**: Prophet (Facebook's time series forecasting)
- **Features**: Hour, day of week, holidays, historical patterns
- **Output**: Hourly/daily order predictions with confidence intervals

### Kitchen Optimization

- **Algorithm**: Random Forest Regressor
- **Features**: Station load, item complexity, time of day, staff count
- **Output**: Prep time predictions, bottleneck identification

### Customer Analytics

- **Churn Model**: Gradient Boosting Classifier
- **LTV Model**: XGBoost Regressor
- **Features**: Order frequency, recency, monetary value, engagement metrics

### Inventory Optimization

- **Algorithm**: Linear Regression with constraints
- **Features**: Consumption rate, lead time, seasonality
- **Output**: Optimal reorder points, quantities, and timing

## 🎨 Themes

The dashboard supports multiple themes:

- **Light**: Clean, professional light theme
- **Dark**: Easy on the eyes dark theme
- **Ocean**: Cool blue tones
- **Forest**: Natural green palette
- **Sunset**: Warm orange and purple hues

## 📖 API Documentation

Once the backend is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Demand Forecasting

- `POST /api/predictions/demand` - Get demand forecast
- `POST /api/predictions/demand/items` - Item-level demand
- `POST /api/predictions/demand/category` - Category demand
- `GET /api/predictions/demand/peak-hours` - Peak hours analysis

#### Kitchen Optimization

- `POST /api/predictions/kitchen/prep-time` - Prep time prediction
- `POST /api/predictions/kitchen/batch-prep-time` - Batch predictions
- `GET /api/predictions/kitchen/bottlenecks` - Bottleneck analysis
- `GET /api/predictions/kitchen/station-performance` - Station metrics

#### Customer Analytics

- `POST /api/predictions/customer/churn` - Churn prediction
- `GET /api/predictions/customer/ltv` - Lifetime value
- `POST /api/predictions/customer/batch-analytics` - Batch analytics
- `GET /api/predictions/customer/at-risk` - At-risk customers
- `GET /api/predictions/customer/high-value` - High-value customers

#### Inventory Management

- `GET /api/predictions/inventory/recommendations` - Reorder recommendations
- `POST /api/predictions/inventory/batch-recommendations` - Batch recommendations
- `GET /api/predictions/inventory/reorder-summary` - Reorder summary
- `GET /api/predictions/inventory/status` - Inventory status
- `POST /api/predictions/inventory/optimize` - Optimization analysis

## 🔄 CI/CD

Automated testing and deployment with GitHub Actions:

- **Continuous Integration**: Tests run on every push and pull request
- **Multi-version Testing**: Python 3.9-3.11, Node 18.x-20.x
- **Code Coverage**: Automatic coverage reports with Codecov
- **Linting**: ESLint for frontend, Flake8 for backend
- **Type Checking**: TypeScript validation

See [.github/workflows/README.md](.github/workflows/README.md) for details.

## 📚 Documentation

- [Backend Documentation](backend/docs/README.md)
- [ML Documentation](backend/ML_DOCS/README.md)
- [API Documentation](backend/docs/api/INDEX.md)
- [Frontend Documentation](frontend/README.md)
- [Test Documentation](TEST_SUMMARY.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow existing code style
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Keep commits atomic and well-described

## 📝 Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/kitchen_ml
MODEL_PATH=./models
LOG_LEVEL=INFO
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api/predictions
```

## 🐛 Troubleshooting

### Backend Issues

**Database Connection Error**

```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**Model Not Found**

```bash
# Train models first
cd backend
python -m src.training.train_pipeline
```

### Frontend Issues

**Port Already in Use**

```bash
# Change port in vite.config.ts or kill process
lsof -ti:5173 | xargs kill -9  # macOS/Linux
```

**Module Not Found**

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Performance

- **API Response Time**: < 100ms (average)
- **Prediction Time**: < 500ms (demand forecasting)
- **Frontend Load Time**: < 2s (initial load)
- **Database Queries**: Optimized with indexes

## 🔒 Security

- Environment variables for sensitive data
- API rate limiting
- Input validation and sanitization
- SQL injection prevention with parameterized queries
- CORS configuration for production

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Elly Aseneka** - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the amazing frontend library
- Prophet for time series forecasting
- scikit-learn for ML algorithms
- The open-source community

## 📞 Support

For support, email support@example.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Real-time predictions with WebSocket
- [ ] Mobile app (React Native)
- [ ] Multi-restaurant support
- [ ] Advanced analytics dashboard
- [ ] Export reports to PDF/Excel
- [ ] Integration with POS systems
- [ ] Automated model retraining
- [ ] A/B testing framework
- [ ] Multi-language support
- [ ] Dark mode improvements

---

**Built with ❤️ for restaurant operations optimization**
