# Quick Start Guide

## Get Started in 5 Minutes

This guide will help you get the Stock Market Dashboard running quickly.

## Prerequisites

- Docker 24+ installed
- Docker Compose 2.20+ installed
- 4GB+ RAM available
- 2GB+ disk space available

## Step 1: Clone the Repository

```bash
git clone https://github.com/Chandanraj-123/stockapp.git
cd stockapp
```

## Step 2: Start All Services

```bash
# Start all services in detached mode
docker-compose up -d
```

This will start:
- API Gateway (Port: 8000)
- Authentication Service (Port: 8001)
- User Service (Port: 8002)
- Market Data Service (Port: 8003)
- PostgreSQL Database (Port: 5432)
- Redis Cache (Port: 6379)
- And all other services

## Step 3: Verify Services Are Running

```bash
# Check service status
docker-compose ps

# Or check individual services
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8003/health
```

## Step 4: Access the API

### API Gateway
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)

### Test the API

```bash
# Get market quotes
curl http://localhost:8000/api/v1/market/quotes

# Get market status
curl http://localhost:8000/api/v1/market/status

# Get a specific quote
curl http://localhost:8000/api/v1/market/quotes/RELIANCE
```

## Step 5: Authentication

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Use the Token
```bash
# Get your access token from the login response
ACCESS_TOKEN="your-access-token-here"

# Use it in subsequent requests
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/users/me
```

## Step 6: WebSocket for Live Data

```javascript
// Connect to WebSocket for live quotes
const socket = new WebSocket('ws://localhost:8000/ws/quotes');

socket.onopen = () => {
  console.log('Connected to WebSocket');
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received update:', data);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

## Step 7: View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api-gateway
docker-compose logs -f market-data-service
```

## Step 8: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Common Issues and Solutions

### Issue: Port Already in Use
```bash
# Find and kill the process using the port
lsof -i :8000
kill -9 <PID>

# Or use a different port by editing docker-compose.yml
```

### Issue: Docker Out of Memory
```bash
# Increase Docker memory allocation in Docker Desktop settings
# Or limit services
docker-compose up -d api-gateway auth-service market-data-service postgres redis
```

### Issue: Database Connection Failed
```bash
# Wait for PostgreSQL to initialize
docker-compose logs -f postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: Redis Connection Failed
```bash
# Check Redis logs
docker-compose logs -f redis

# Restart Redis
docker-compose restart redis
```

## Development Workflow

### Run a Single Service Locally

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Run API Gateway locally
cd services/api-gateway
poetry install
poetry run python main.py
```

### Hot Reloading

```bash
# Run with hot reload
poetry run python main.py  # Already has reload enabled in debug mode

# Or with uvicorn
poetry run uvicorn main:app --reload --port 8000
```

### Testing

```bash
# Run tests
poetry run pytest tests/ -v

# With coverage
poetry run pytest tests/ --cov=service_name --cov-report=html
```

## API Endpoints Quick Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Get current user |

### Market Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/market/quotes` | Get all quotes |
| GET | `/api/v1/market/quotes/{symbol}` | Get quote |
| GET | `/api/v1/market/ohlcv` | Get OHLCV data |
| GET | `/api/v1/market/status` | Market status |
| GET | `/api/v1/market/calendar` | Market calendar |
| WS | `/ws/quotes` | Live quotes |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/` | Create user |
| GET | `/api/v1/users/` | List users |
| GET | `/api/v1/users/{id}` | Get user |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

## Service Ports

| Service | Port | Health Check |
|---------|------|--------------|
| API Gateway | 8000 | `/health` |
| Auth Service | 8001 | `/health` |
| User Service | 8002 | `/health` |
| Market Data | 8003 | `/health` |
| Watchlist | 8004 | `/health` |
| Screener | 8005 | `/health` |
| Portfolio | 8006 | `/health` |
| Trading | 8007 | `/health` |
| Alerts | 8008 | `/health` |
| Notifications | 8009 | `/health` |
| News | 8010 | `/health` |
| Scheduler | 8011 | `/health` |
| Reports | 8012 | `/health` |
| AI | 8013 | `/health` |
| Admin | 8014 | `/health` |
| PostgreSQL | 5432 | - |
| Redis | 6379 | - |
| Frontend | 3000 | - |

## Tips

1. **Use Docker Compose for Development**: It's the easiest way to run all services
2. **Check Logs First**: Most issues can be diagnosed by checking logs
3. **Health Checks**: Always check `/health` endpoints to verify services are running
4. **Start Small**: Start with just the services you need, then add more
5. **Clean Up**: Use `docker-compose down -v` to completely reset

## Next Steps

1. **Explore the API**: Use Swagger UI at http://localhost:8000/docs
2. **Try the WebSocket**: Connect to ws://localhost:8000/ws/quotes for live data
3. **Add More Services**: Implement the remaining service stubs
4. **Build the Frontend**: Complete the Next.js frontend application
5. **Add Real Data**: Integrate with TradingView Screener API for real market data

---

**Need Help?**
- Check the full documentation in `README.md`
- Check the implementation summary in `IMPLEMENTATION_SUMMARY.md`
- Open an issue on GitHub: https://github.com/Chandanraj-123/stockapp/issues
