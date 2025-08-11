import streamlit as st
import subprocess
import os
import time

os.environ['DOCKER_USERNAME'] = 'vinay125219'

st.title("MLOps Service Control")

if st.button("Start All Services"):
    with st.spinner("Starting services..."):
        services = ['housing-api', 'grafana', 'mlflow', 'prometheus', 'retraining']
        for service in services:
            try:
                subprocess.run(['docker-compose', '-f', 'docker-compose.monitoring.yml', 'up', '-d', service], check=True)
                time.sleep(5)  # Wait for service to initialize
            except Exception as e:
                st.error(f"Failed to start {service}: {e}")
        st.success("All services started!")

if st.button("Stop All Services"):
    with st.spinner("Stopping services..."):
        services = ['housing-api', 'grafana', 'mlflow', 'prometheus', 'retraining']
        for service in services:
            try:
                subprocess.run(['docker-compose', '-f', 'docker-compose.monitoring.yml', 'stop', service], check=True)
            except Exception as e:
                st.error(f"Failed to stop {service}: {e}")
        st.success("All services stopped!")

if st.button("Check Status"):
    with st.spinner("Checking status..."):
        result = subprocess.run(['docker-compose', '-f', 'docker-compose.monitoring.yml', 'ps'], capture_output=True, text=True)
        st.text(result.stdout)