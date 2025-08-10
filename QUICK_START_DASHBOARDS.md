# 🚀 Quick Start: Get Your Dashboards Running in 5 Minutes

This is a super simple guide to get your monitoring dashboards up and running quickly.

## ⚡ Step 1: Start Everything (2 minutes)

### Open Terminal/Command Prompt
```bash
# Navigate to your project folder
cd "c:\Users\vinay\OneDrive\Desktop\mlops-housing-pipeline (2) (1)\mlops-housing-pipeline"

# Start all services
docker-compose -f docker-compose.monitoring.yml up -d
```

**Wait for this message**: `✅ All services started successfully`

### Check Everything is Running
```bash
docker-compose -f docker-compose.monitoring.yml ps
```

You should see 6 services running (all showing "Up").

---

## 📊 Step 2: Open Your Dashboard (1 minute)

### 1. Open Your Browser
Go to: **http://localhost:3000**

### 2. Login to Grafana
- **Username**: `admin`
- **Password**: `admin`
- Click **"Log In"**
- Click **"Skip"** when asked to change password (or change it if you want)

### 3. Find Your Dashboard
- Click **"Dashboards"** in the left menu (looks like 📊)
- Click **"MLOps Monitoring Dashboard"**

**🎉 You should now see your monitoring dashboard!**

---

## 🎯 Step 3: Generate Some Data (2 minutes)

Your dashboard might be empty because there's no data yet. Let's fix that!

### Open a New Terminal
```bash
# Navigate to your project (if not already there)
cd "c:\Users\vinay\OneDrive\Desktop\mlops-housing-pipeline (2) (1)\mlops-housing-pipeline"

# Run test samples to generate data
python test_api_samples.py
```

**This will**:
- Make API calls to both housing and iris APIs
- Generate metrics and data
- Populate your dashboard with real information

### Go Back to Your Dashboard
- Refresh your browser (F5 or Ctrl+R)
- You should now see data in the charts!

---

## 📈 What You're Looking At

### Your Dashboard Has 7 Main Panels:

#### 1. **API Request Rate** (Top Left)
- **Shows**: How busy your APIs are
- **Lines going up**: More people using your APIs
- **Flat lines**: No activity

#### 2. **Total Predictions** (Top Right)
- **Big number**: Total predictions made
- **This number grows**: Every time someone uses your API

#### 3. **Model Prediction Latency** (Middle Left)
- **Shows**: How fast your models respond
- **Lower is better**: Faster = better user experience
- **Good**: Under 1 second

#### 4. **Model Accuracy** (Middle Right)
- **Gauge/Speedometer**: Shows how accurate your models are
- **Green**: Good accuracy (above 85%)
- **Yellow/Red**: Needs attention

#### 5. **Validation Error Rate** (Bottom)
- **Shows**: How many bad requests you get
- **Spikes**: Periods with invalid data
- **Lower is better**: Fewer errors = better API

#### 6. **Daily Predictions** (Bottom Left)
- **Numbers**: How many predictions made today
- **Two numbers**: One for housing, one for iris

#### 7. **Database Size** (Bottom Right)
- **Shows**: How much storage your logs use
- **Growing**: Normal as you make more predictions

---

## 🎮 Playing with Your Dashboard

### Change Time Range
- **Top right corner**: Click the time picker
- **Try**: "Last 5 minutes", "Last 1 hour", "Last 24 hours"
- **See**: How your data changes over different periods

### Refresh Data
- **Top right**: Click the refresh button (🔄)
- **Auto-refresh**: Click the dropdown next to refresh, select "5s" for live updates

### Zoom In on Charts
- **Click and drag** on any chart to zoom into a specific time period
- **Double-click** to zoom back out

---

## 🧪 Test Your System

### Make Some API Calls
```bash
# Test Housing API
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "total_rooms": 5000.0,
    "total_bedrooms": 1200.0,
    "population": 3000.0,
    "households": 1000.0,
    "median_income": 5.5,
    "housing_median_age": 25.0,
    "latitude": 37.88,
    "longitude": -122.23
  }'

# Test Iris API
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.8,
    "sepal_width": 3.0,
    "petal_length": 4.3,
    "petal_width": 1.3
  }'
```

**Watch your dashboard**: You should see the numbers change!

---

## 🔍 Explore Other Services

### API Documentation
- **Housing API**: http://localhost:8000/docs
- **Iris API**: http://localhost:8001/docs
- **Try the APIs**: Use the interactive documentation

### Prometheus (Raw Metrics)
- **URL**: http://localhost:9090
- **What it is**: The data source for your dashboard
- **Try**: Type `mlops_model_predictions_total` and click "Execute"

### MLflow (Experiment Tracking)
- **URL**: http://localhost:5000
- **What it is**: Tracks your model training experiments
- **See**: Model performance over time

---

## 🚨 Troubleshooting

### Dashboard Shows No Data?
```bash
# Check if services are running
docker-compose -f docker-compose.monitoring.yml ps

# If not all running, restart
docker-compose -f docker-compose.monitoring.yml restart

# Generate some data
python test_api_samples.py
```

### Can't Access Grafana?
1. **Check URL**: Make sure it's http://localhost:3000
2. **Wait**: Services might still be starting (wait 2-3 minutes)
3. **Check Docker**: Make sure Docker Desktop is running

### APIs Not Responding?
```bash
# Check API health
curl http://localhost:8000/health
curl http://localhost:8001/health

# If they don't respond, restart
docker-compose -f docker-compose.monitoring.yml restart housing-api iris-api
```

---

## 🎯 What's Next?

### Daily Monitoring (2 minutes/day)
1. **Open dashboard**: http://localhost:3000
2. **Check accuracy**: Are your models performing well?
3. **Look for errors**: Any red spikes in error charts?
4. **Note usage**: How many predictions today?

### Weekly Deep Dive (10 minutes/week)
1. **Change time range**: Look at "Last 7 days"
2. **Identify patterns**: When are your APIs busiest?
3. **Check trends**: Are models getting better or worse?
4. **Plan improvements**: Based on what you see

### Monthly Review (30 minutes/month)
1. **Export data**: Screenshot interesting charts
2. **Share insights**: With your team or stakeholders
3. **Plan optimizations**: Based on usage patterns
4. **Update alerts**: Adjust thresholds if needed

---

## 📞 Quick Reference Card

### 🔗 Important URLs
- **Dashboard**: http://localhost:3000 (admin/admin)
- **Housing API**: http://localhost:8000/docs
- **Iris API**: http://localhost:8001/docs
- **Prometheus**: http://localhost:9090
- **MLflow**: http://localhost:5000

### 💻 Key Commands
```bash
# Start everything
docker-compose -f docker-compose.monitoring.yml up -d

# Stop everything
docker-compose -f docker-compose.monitoring.yml down

# Check status
docker-compose -f docker-compose.monitoring.yml ps

# Generate test data
python test_api_samples.py

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 🎯 Dashboard Navigation
- **Left sidebar**: Main navigation
- **Top right**: Time range and refresh
- **Click & drag**: Zoom into charts
- **Double-click**: Zoom out

---

## 🎉 You're All Set!

Congratulations! You now have:
- ✅ A running monitoring system
- ✅ Real-time dashboards
- ✅ API performance tracking
- ✅ Model accuracy monitoring
- ✅ Error tracking and alerting

**Your MLOps pipeline is now production-ready with full observability!**

---

## 💡 Pro Tips

1. **Bookmark** http://localhost:3000 for easy access
2. **Set auto-refresh** to 30s for live monitoring
3. **Take screenshots** of interesting patterns
4. **Share dashboards** with your team
5. **Set up alerts** for critical metrics

Happy monitoring! 🚀📊
