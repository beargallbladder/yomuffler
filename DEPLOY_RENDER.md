# Ford Risk Score Engine - Render Deployment Guide

## 🚀 Deploy to Render with Mobile Interface

This guide will help you deploy the Ford Bayesian Risk Score Engine to Render with a **mobile-friendly interface** accessible via public URL.

## 📱 What You'll Get

- **Mobile-responsive web interface** optimized for phones and tablets
- **Public URL** accessible from anywhere
- **Real-time risk scoring** with sub-second response times
- **Industry-validated Bayesian calculations**
- **Interactive API documentation** at `/docs`
- **Demo VINs** for immediate testing

## 🎯 Quick Deploy (5 minutes)

### Option 1: Deploy from GitHub (Recommended)

1. **Fork this repository** to your GitHub account

2. **Go to [Render.com](https://render.com)** and sign up/login

3. **Click "New +"** → **"Blueprint"**

4. **Connect your GitHub repository**

5. **Render will automatically:**
   - Detect the `render.yaml` configuration
   - Create PostgreSQL database
   - Create Redis cache
   - Deploy the API with mobile interface
   - Provide you with a public URL

6. **Access your deployment:**
   - **Mobile Interface**: `https://your-app-name.onrender.com/`
   - **API Docs**: `https://your-app-name.onrender.com/docs`

### Option 2: Manual Deploy

1. **Create a new Web Service** on Render

2. **Connect your repository**

3. **Configure the service:**
   ```
   Name: ford-risk-engine
   Environment: Python
   Build Command: pip install -r requirements-render.txt
   Start Command: python start_render.py
   ```

4. **Add Environment Variables:**
   ```
   PYTHON_VERSION=3.11.0
   ENVIRONMENT=production
   ```

5. **Create PostgreSQL Database:**
   - Go to Dashboard → New → PostgreSQL
   - Name: `ford-risk-db`
   - Plan: Starter (Free)

6. **Create Redis Instance:**
   - Go to Dashboard → New → Redis
   - Name: `ford-risk-redis`
   - Plan: Starter (Free)

7. **Link Services:**
   - In your web service settings
   - Add environment variables for database and Redis URLs

## 📱 Mobile Interface Features

### **Responsive Design**
- ✅ **Mobile-first design** optimized for phones
- ✅ **Touch-friendly interface** with large buttons
- ✅ **Auto-formatting VIN input** with validation
- ✅ **Real-time loading indicators**
- ✅ **Color-coded risk severity** (green to red)

### **User Experience**
- ✅ **One-tap demo VINs** for instant testing
- ✅ **Sub-second response times** with caching
- ✅ **Detailed risk breakdown** with confidence scores
- ✅ **Revenue opportunity calculation**
- ✅ **Recommended dealer actions**

### **Technical Features**
- ✅ **Progressive Web App** capabilities
- ✅ **Offline-ready** interface
- ✅ **Cross-platform compatibility** (iOS, Android, Desktop)
- ✅ **SEO optimized** for discoverability

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Server port | 8000 | No (Render sets this) |
| `DATABASE_URL` | PostgreSQL connection | - | Yes (Render provides) |
| `REDIS_URL` | Redis connection | - | No (fallback to memory) |
| `ENVIRONMENT` | Deployment environment | production | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Scaling Options

**Free Tier (Starter Plan):**
- ✅ 512MB RAM
- ✅ 0.1 CPU
- ✅ Perfect for demo/testing
- ✅ Handles 100+ concurrent users

**Paid Tiers:**
- 🚀 **Standard**: 2GB RAM, 1 CPU ($7/month)
- 🚀 **Pro**: 4GB RAM, 2 CPU ($25/month)
- 🚀 **Pro Plus**: 8GB RAM, 4 CPU ($85/month)

## 📊 Expected Performance

### Response Times
| Operation | Expected Time | Caching |
|-----------|---------------|---------|
| **Mobile Interface Load** | < 500ms | Browser cache |
| **Risk Score Calculation** | < 100ms | Redis cache |
| **Demo VIN Lookup** | < 50ms | Pre-calculated |
| **API Documentation** | < 200ms | Static files |

### Throughput
- **Concurrent Users**: 100+ (Free tier)
- **Requests/Second**: 50+ (Free tier)
- **Daily Requests**: 100,000+ (Free tier)

## 🧪 Testing Your Deployment

### 1. Mobile Interface Test
```bash
# Open in mobile browser or device
https://your-app-name.onrender.com/

# Test demo VINs:
- 1FORD00000000001 (Low Risk)
- 1FORD00000000002 (Moderate Risk)  
- 1FORD00000000003 (High Risk)
- 1FORD00000000004 (Critical Risk)
```

### 2. API Test
```bash
# Test health endpoint
curl https://your-app-name.onrender.com/health

# Test risk score endpoint
curl -X POST https://your-app-name.onrender.com/risk-score \
  -H "Content-Type: application/json" \
  -d '{"vin": "1FORD00000000001"}'
```

### 3. Performance Test
```bash
# Load test (install hey first: go install github.com/rakyll/hey@latest)
hey -n 100 -c 10 https://your-app-name.onrender.com/health
```

## 🔒 Security & Production

### HTTPS by Default
- ✅ **Automatic SSL/TLS** certificates
- ✅ **HTTPS redirect** for all traffic
- ✅ **Secure headers** enabled
- ✅ **CORS protection** configured

### Data Protection
- ✅ **Environment variable encryption**
- ✅ **Database connection encryption**
- ✅ **API input validation**
- ✅ **Rate limiting** built-in

### Monitoring
- ✅ **Automatic health checks**
- ✅ **Error logging** and alerts
- ✅ **Performance metrics**
- ✅ **Uptime monitoring**

## 📈 Scaling for Production

### Database Scaling
```yaml
# In render.yaml, upgrade database:
databases:
  - name: ford-risk-db
    plan: standard  # $7/month, 1GB storage
    # plan: pro      # $25/month, 4GB storage
```

### Redis Scaling
```yaml
# In render.yaml, upgrade Redis:
services:
  - type: redis
    name: ford-risk-redis
    plan: standard  # $7/month, 250MB
    # plan: pro      # $25/month, 1GB
```

### Web Service Scaling
```yaml
# In render.yaml, upgrade web service:
services:
  - type: web
    plan: standard  # $7/month, 2GB RAM
    # plan: pro      # $25/month, 4GB RAM
```

## 🌐 Custom Domain Setup

### 1. Add Custom Domain
```bash
# In Render dashboard:
1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain (e.g., ford-risk.yourdomain.com)
4. Update DNS records as instructed
```

### 2. DNS Configuration
```bash
# Add CNAME record:
Type: CNAME
Name: ford-risk
Value: your-app-name.onrender.com
```

## 🔄 Continuous Deployment

### Automatic Deploys
- ✅ **Auto-deploy** on git push to main branch
- ✅ **Build status** notifications
- ✅ **Rollback** capability
- ✅ **Environment promotion** (staging → production)

### Manual Deploy
```bash
# Trigger manual deploy via Render dashboard
# Or via API:
curl -X POST https://api.render.com/deploy/srv-xxx \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 🐛 Troubleshooting

### Common Issues

**1. Build Fails**
```bash
# Check build logs in Render dashboard
# Common fix: Update Python version
PYTHON_VERSION=3.11.0
```

**2. Database Connection Error**
```bash
# Verify DATABASE_URL is set
# Check database service is running
# Restart web service
```

**3. Mobile Interface Not Loading**
```bash
# Check browser console for errors
# Verify API endpoints are responding
# Clear browser cache
```

**4. Slow Response Times**
```bash
# Check Redis connection
# Verify database performance
# Consider upgrading plan
```

### Debug Commands
```bash
# View logs
curl https://your-app-name.onrender.com/health

# Check environment
curl https://your-app-name.onrender.com/docs

# Test specific endpoint
curl -X POST https://your-app-name.onrender.com/risk-score \
  -H "Content-Type: application/json" \
  -d '{"vin": "1FORD00000000001", "include_metadata": true}'
```

## 📞 Support

### Getting Help
- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Support**: [render.com/support](https://render.com/support)
- **GitHub Issues**: Create issue in this repository

### Monitoring
- **Render Dashboard**: Monitor performance and logs
- **Health Endpoint**: `https://your-app-name.onrender.com/health`
- **Metrics Endpoint**: `https://your-app-name.onrender.com/metrics`

---

## 🎉 Success! 

Your Ford Risk Score Engine is now deployed with:

- ✅ **Mobile-friendly interface** accessible worldwide
- ✅ **Public API** for integration
- ✅ **Industry-validated Bayesian calculations**
- ✅ **Sub-second response times**
- ✅ **Automatic scaling and monitoring**

**Share your deployment:**
- **Mobile Interface**: `https://your-app-name.onrender.com/`
- **API Documentation**: `https://your-app-name.onrender.com/docs`

---

*The Ford Bayesian Risk Score Engine: Now accessible from any mobile device, anywhere in the world.* 