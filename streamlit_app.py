import streamlit as st
import subprocess
import os
import time
import requests
import webbrowser
from datetime import datetime
import pandas as pd
import json

os.environ['DOCKER_USERNAME'] = 'vinay125219'

# Configure Streamlit page
st.set_page_config(
    page_title="MLOps Housing Pipeline Control",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🏠 MLOps Housing Price Prediction Pipeline")
st.markdown("### Service Management Dashboard")

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    page = st.selectbox(
        "Choose a page:",
        ["Service Control", "API Testing", "Model Performance", "Monitoring Links"]
    )

if page == "Service Control":
    st.header("Docker Service Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start All Services", use_container_width=True):
            with st.spinner("Starting services..."):
                try:
                    result = subprocess.run(
                        ['docker-compose', 'up', '-d'], 
                        capture_output=True, text=True, cwd=os.getcwd()
                    )
                    if result.returncode == 0:
                        st.success("✅ All services started successfully!")
                        st.info("Services will be available at:")
                        st.markdown("""
                        - **Housing API**: http://localhost:8000
                        - **Streamlit UI**: http://localhost:8501
                        - **MLflow**: http://localhost:5000
                        - **Grafana**: http://localhost:3001 (admin/admin)
                        - **Prometheus**: http://localhost:9090
                        - **Retraining API**: http://localhost:8002
                        """)
                        # Auto-open browser for Streamlit
                        try:
                            webbrowser.open('http://localhost:8501')
                        except:
                            pass
                    else:
                        st.error(f"Failed to start services: {result.stderr}")
                        st.code(result.stdout)
                except Exception as e:
                    st.error(f"Error starting services: {e}")
    
    with col2:
        if st.button("🛑 Stop All Services", use_container_width=True):
            with st.spinner("Stopping services..."):
                try:
                    result = subprocess.run(
                        ['docker-compose', 'down'], 
                        capture_output=True, text=True, cwd=os.getcwd()
                    )
                    if result.returncode == 0:
                        st.success("✅ All services stopped successfully!")
                    else:
                        st.error(f"Failed to stop services: {result.stderr}")
                except Exception as e:
                    st.error(f"Error stopping services: {e}")
    
    with col3:
        if st.button("🔄 Restart Services", use_container_width=True):
            with st.spinner("Restarting services..."):
                try:
                    # Stop first
                    subprocess.run(['docker-compose', 'down'], capture_output=True, cwd=os.getcwd())
                    time.sleep(2)
                    # Start again
                    result = subprocess.run(
                        ['docker-compose', 'up', '-d'], 
                        capture_output=True, text=True, cwd=os.getcwd()
                    )
                    if result.returncode == 0:
                        st.success("✅ Services restarted successfully!")
                    else:
                        st.error(f"Failed to restart services: {result.stderr}")
                except Exception as e:
                    st.error(f"Error restarting services: {e}")

    st.header("Service Status")
    if st.button("🔍 Check Service Status"):
        try:
            result = subprocess.run(
                ['docker-compose', 'ps'], 
                capture_output=True, text=True, cwd=os.getcwd()
            )
            st.text(result.stdout)
            
            # Check individual service health
            st.subheader("Health Checks")
            services_health = {
                "Housing API": "http://localhost:8000/health",
                "MLflow": "http://localhost:5000",
                "Grafana": "http://localhost:3001/api/health",
                "Prometheus": "http://localhost:9090/-/healthy"
            }
            
            for service_name, health_url in services_health.items():
                try:
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        st.success(f"✅ {service_name}: Healthy")
                    else:
                        st.warning(f"⚠️ {service_name}: Unhealthy (Status: {response.status_code})")
                except requests.exceptions.RequestException:
                    st.error(f"❌ {service_name}: Not responding")
                    
        except Exception as e:
            st.error(f"Error checking status: {e}")

elif page == "API Testing":
    st.header("Housing Price Prediction API Testing")
    
    # API endpoint input
    api_base = st.text_input("API Base URL:", value="http://localhost:8000")
    
    # Prediction form
    st.subheader("Test Prediction")
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            total_rooms = st.number_input("Total Rooms", min_value=1.0, value=4500.0)
            total_bedrooms = st.number_input("Total Bedrooms", min_value=1.0, value=900.0)
            population = st.number_input("Population", min_value=1.0, value=3000.0)
            households = st.number_input("Households", min_value=1.0, value=1000.0)
        
        with col2:
            median_income = st.number_input("Median Income (tens of thousands)", min_value=0.1, value=5.5)
            housing_median_age = st.number_input("Housing Median Age", min_value=0.0, value=26.0)
            latitude = st.number_input("Latitude", min_value=32.0, max_value=42.0, value=37.86)
            longitude = st.number_input("Longitude", min_value=-125.0, max_value=-114.0, value=-122.27)
        
        submitted = st.form_submit_button("🔮 Predict Price")
        
        if submitted:
            prediction_data = {
                "total_rooms": total_rooms,
                "total_bedrooms": total_bedrooms,
                "population": population,
                "households": households,
                "median_income": median_income,
                "housing_median_age": housing_median_age,
                "latitude": latitude,
                "longitude": longitude
            }
            
            try:
                response = requests.post(f"{api_base}/predict", json=prediction_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    predicted_price = result["predicted_price"]
                    st.success(f"🎯 Predicted Price: **${predicted_price * 100000:,.2f}**")
                    st.json(result)
                else:
                    st.error(f"Prediction failed: {response.status_code}")
                    st.json(response.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Error calling API: {e}")
    
    # Model retraining
    st.subheader("Model Retraining")
    if st.button("🔄 Trigger Model Retraining"):
        try:
            retrain_data = {"force": True}
            response = requests.post(f"{api_base}/retrain", json=retrain_data, timeout=60)
            if response.status_code == 200:
                st.success("✅ Model retraining completed!")
                st.json(response.json())
            else:
                st.error(f"Retraining failed: {response.status_code}")
                st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f"Error triggering retraining: {e}")

elif page == "Model Performance":
    st.header("Model Performance Metrics")
    
    try:
        # Get model info
        response = requests.get("http://localhost:8000/model-info", timeout=10)
        if response.status_code == 200:
            model_info = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Model Name", model_info.get("model_name", "N/A"))
                st.metric("Model Type", model_info.get("model_type", "N/A"))
            
            with col2:
                last_trained = model_info.get("last_trained")
                if last_trained:
                    st.metric("Last Trained", last_trained)
                
                model_path = model_info.get("model_path", "N/A")
                st.metric("Model Path", model_path)
            
            # Performance metrics
            if model_info.get("performance_metrics"):
                st.subheader("Performance Metrics")
                metrics = model_info["performance_metrics"]
                
                cols = st.columns(len(metrics))
                for i, (metric, value) in enumerate(metrics.items()):
                    with cols[i]:
                        st.metric(metric.upper(), f"{value:.4f}")
        else:
            st.error("Could not fetch model information")
    except requests.exceptions.RequestException:
        st.warning("Housing API not available. Please start the services first.")

elif page == "Monitoring Links":
    st.header("🔗 Monitoring and Service Links")
    
    # Quick access links
    st.subheader("Service Dashboards")
    
    links = {
        "🏠 Housing API Documentation": "http://localhost:8000/docs",
        "📊 MLflow Tracking": "http://localhost:5000",
        "📈 Grafana Dashboard": "http://localhost:3001",
        "🎯 Prometheus Metrics": "http://localhost:9090",
        "🔄 Retraining API": "http://localhost:8002",
        "📋 API Metrics": "http://localhost:8000/metrics"
    }
    
    cols = st.columns(2)
    for i, (name, url) in enumerate(links.items()):
        col = cols[i % 2]
        with col:
            if st.button(name, use_container_width=True):
                webbrowser.open(url)
                st.info(f"Opening {url}")
    
    st.subheader("Default Credentials")
    st.info("""
    **Grafana Login:**
    - Username: admin
    - Password: admin
    
    **Service Ports:**
    - Housing API: 8000
    - Streamlit: 8501 
    - MLflow: 5000
    - Grafana: 3001
    - Prometheus: 9090
    - Retraining: 8002
    """)

# Footer
st.markdown("---")
st.markdown("### 🚀 MLOps Housing Pipeline Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
