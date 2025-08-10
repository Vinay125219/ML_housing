# 📊 Complete Dashboard & Monitoring Guide

This guide will walk you through setting up and using the monitoring dashboards for your MLOps pipeline, even if you're completely new to Grafana and Prometheus.

## 🎯 What You'll Learn

1. **What are Dashboards?** - Understanding monitoring concepts
2. **Setting Up the Stack** - Getting everything running
3. **Using Grafana Dashboards** - Step-by-step navigation
4. **Understanding Metrics** - What each chart means
5. **Creating Custom Dashboards** - Building your own views
6. **Troubleshooting** - Common issues and solutions

---

## 📚 Part 1: Understanding Monitoring Concepts

### What is Monitoring?
Monitoring is like having a health checkup for your ML system. Just like doctors use various tests to check your health, we use metrics to check our system's health.

### Key Components:
- **Prometheus** 📈 - Collects and stores metrics (like a data collector)
- **Grafana** 📊 - Creates beautiful charts and dashboards (like a report generator)
- **Metrics** 📏 - Numbers that tell us how our system is performing

### Why Do We Need This?
- **Catch Problems Early**: See issues before users complain
- **Understand Usage**: Know how many people use your API
- **Track Performance**: See if your models are getting worse
- **Make Decisions**: Use data to improve your system

---

## 🚀 Part 2: Setting Up Your Monitoring Stack

### Step 1: Start All Services
```bash
# Navigate to your project directory
cd /path/to/your/mlops-housing-pipeline

# Start the complete monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Check if everything is running
docker-compose -f docker-compose.monitoring.yml ps
```

You should see these services running:
- ✅ `mlops-prometheus` (Port 9090)
- ✅ `mlops-grafana` (Port 3000)
- ✅ `mlops-housing-api` (Port 8000)
- ✅ `mlops-iris-api` (Port 8001)
- ✅ `mlops-retraining` (Port 8002)
- ✅ `mlops-mlflow` (Port 5000)

### Step 2: Verify Services Are Working
```bash
# Test each service
curl http://localhost:8000/health    # Housing API
curl http://localhost:8001/health    # Iris API
curl http://localhost:9090/-/healthy # Prometheus
curl http://localhost:3000/api/health # Grafana
```

### Step 3: Generate Some Data
```bash
# Run test samples to generate metrics
python test_api_samples.py

# This will create predictions and metrics for the dashboard
```

---

## 📊 Part 3: Your First Look at Grafana

### Accessing Grafana
1. **Open your browser** and go to: http://localhost:3000
2. **Login** with:
   - Username: `admin`
   - Password: `admin`
3. **Skip** the password change (or change it if you want)

### Understanding the Grafana Interface

#### Main Navigation (Left Sidebar):
- 🏠 **Home** - Main dashboard list
- 📊 **Dashboards** - All your dashboards
- 🔍 **Explore** - Query metrics directly
- ⚠️ **Alerting** - Set up alerts
- ⚙️ **Configuration** - Settings and data sources

#### Your MLOps Dashboard
1. Click **Dashboards** in the left sidebar
2. Look for **"MLOps Monitoring Dashboard"**
3. Click on it to open

---

## 📈 Part 4: Understanding Your Dashboard Panels

### Panel 1: API Request Rate
**What it shows**: How many requests per second your APIs receive
- **Green line**: Housing API requests
- **Blue line**: Iris API requests
- **Higher is better**: More usage means more users

**How to read it**:
- X-axis: Time
- Y-axis: Requests per second
- Spikes = busy periods
- Flat lines = no activity

### Panel 2: Total Predictions
**What it shows**: Total number of predictions made
- **Big number**: Total predictions since start
- **Color coding**: Green = good, Red = problems

### Panel 3: Model Prediction Latency
**What it shows**: How fast your models respond
- **95th percentile**: 95% of requests are faster than this
- **50th percentile**: Average response time
- **Lower is better**: Faster responses = better user experience

**Good values**:
- < 100ms = Excellent
- 100-500ms = Good
- > 1s = Needs attention

### Panel 4: Model Accuracy
**What it shows**: How accurate your models are
- **Gauge chart**: Like a speedometer
- **Green zone**: Good accuracy (>85%)
- **Yellow zone**: Okay accuracy (70-85%)
- **Red zone**: Poor accuracy (<70%)

### Panel 5: Validation Error Rate
**What it shows**: How many invalid requests you receive
- **Spikes**: Periods with many bad requests
- **Flat line**: All requests are valid
- **Lower is better**: Fewer errors = better API design

### Panel 6: Daily Predictions
**What it shows**: How many predictions made today
- **Housing**: Number for housing predictions
- **Iris**: Number for iris predictions

### Panel 7: Database Size
**What it shows**: How much storage your logs use
- **Bytes**: Size of prediction databases
- **Growing**: Normal as you make more predictions
- **Too large**: May need cleanup

---

## 🎨 Part 5: Customizing Your Dashboard

### Adding a New Panel
1. **Click** the **"+"** icon at the top
2. **Select** "Add Panel"
3. **Choose** "Add a new panel"

### Creating a Simple Panel
1. **In the query box**, try this metric: `mlops_model_predictions_total`
2. **Click** "Run Query"
3. **See the data** appear in the chart
4. **Give it a title**: "My Custom Panel"
5. **Click** "Apply"

### Panel Types You Can Create:
- **Time Series**: Line charts over time
- **Stat**: Big numbers
- **Gauge**: Speedometer-style
- **Bar Chart**: Comparing values
- **Table**: Data in rows and columns

---

## 🔧 Part 6: Useful Queries for Your System

### Basic Metrics Queries:
```promql
# Total API requests
sum(mlops_api_requests_total)

# Request rate (per second)
rate(mlops_api_requests_total[5m])

# Average prediction latency
avg(mlops_model_prediction_latency_seconds)

# Error rate
rate(mlops_api_validation_errors_total[5m])

# Daily predictions by model
mlops_daily_predictions

# Model accuracy
mlops_model_accuracy
```

### Advanced Queries:
```promql
# Success rate percentage
(sum(rate(mlops_api_requests_total{status_code="200"}[5m])) / sum(rate(mlops_api_requests_total[5m]))) * 100

# 95th percentile latency
histogram_quantile(0.95, rate(mlops_model_prediction_latency_seconds_bucket[5m]))

# Predictions per hour
increase(mlops_model_predictions_total[1h])
```

---

## 🚨 Part 7: Setting Up Alerts

### Why Set Up Alerts?
Get notified when something goes wrong, like:
- API is down
- Model accuracy drops
- Too many errors
- Response time too slow

### Creating Your First Alert
1. **Go to** Alerting → Alert Rules
2. **Click** "New Rule"
3. **Set conditions**:
   - Query: `mlops_model_accuracy < 0.8`
   - Condition: IS BELOW 0.8
4. **Set notification**: Email, Slack, etc.
5. **Save** the rule

---

## 🔍 Part 8: Exploring Data with Prometheus

### Accessing Prometheus
1. **Open**: http://localhost:9090
2. **Click** "Graph" tab
3. **Try queries** from the examples above

### Useful Prometheus Features:
- **Instant queries**: See current values
- **Range queries**: See data over time
- **Metrics browser**: Discover available metrics
- **Target status**: Check if services are being monitored

---

## 🛠️ Part 9: Troubleshooting Common Issues

### Dashboard Shows No Data
**Possible causes**:
1. **Services not running**: Check `docker-compose ps`
2. **No API calls made**: Run `python test_api_samples.py`
3. **Prometheus not scraping**: Check http://localhost:9090/targets

**Solutions**:
```bash
# Restart services
docker-compose -f docker-compose.monitoring.yml restart

# Check logs
docker-compose -f docker-compose.monitoring.yml logs grafana
docker-compose -f docker-compose.monitoring.yml logs prometheus
```

### Grafana Login Issues
**Default credentials**:
- Username: `admin`
- Password: `admin`

**Reset password**:
```bash
docker-compose -f docker-compose.monitoring.yml exec grafana grafana-cli admin reset-admin-password newpassword
```

### Metrics Not Updating
**Check**:
1. **API endpoints**: http://localhost:8000/mlops-metrics
2. **Prometheus targets**: http://localhost:9090/targets
3. **Make API calls**: Generate some traffic

### Dashboard Panels Empty
**Common fixes**:
1. **Check time range**: Set to "Last 1 hour"
2. **Refresh dashboard**: Click refresh button
3. **Check data source**: Should be "Prometheus"

---

## 📱 Part 10: Mobile and Remote Access

### Accessing from Other Devices
If you want to view dashboards from your phone or another computer:

1. **Find your computer's IP address**:
   ```bash
   # On Windows
   ipconfig
   
   # On Mac/Linux
   ifconfig
   ```

2. **Access from other devices**:
   - Grafana: http://YOUR_IP:3000
   - Prometheus: http://YOUR_IP:9090

### Security Note
Only do this on trusted networks (like your home WiFi).

---

## 🎯 Part 11: Next Steps

### What to Monitor Daily:
1. **Check accuracy**: Are models performing well?
2. **Review errors**: Any validation issues?
3. **Monitor usage**: How many predictions?
4. **Check alerts**: Any notifications?

### Weekly Reviews:
1. **Performance trends**: Getting better or worse?
2. **Usage patterns**: When are peak times?
3. **Error analysis**: What causes most errors?
4. **Capacity planning**: Need more resources?

### Monthly Actions:
1. **Dashboard cleanup**: Remove unused panels
2. **Alert tuning**: Adjust thresholds
3. **Performance optimization**: Based on data
4. **Stakeholder reports**: Share insights

---

## 🎉 Congratulations!

You now have a complete monitoring system for your MLOps pipeline! You can:
- ✅ View real-time metrics
- ✅ Track model performance
- ✅ Monitor API usage
- ✅ Set up alerts
- ✅ Create custom dashboards

Remember: Good monitoring is like having a crystal ball for your ML system - it helps you see problems before they become disasters!

---

## 📞 Quick Reference

### Important URLs:
- **Grafana Dashboard**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Housing API**: http://localhost:8000/docs
- **Iris API**: http://localhost:8001/docs
- **MLflow**: http://localhost:5000

### Quick Commands:
```bash
# Start everything
docker-compose -f docker-compose.monitoring.yml up -d

# Stop everything
docker-compose -f docker-compose.monitoring.yml down

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Generate test data
python test_api_samples.py
```

Happy monitoring! 🚀
