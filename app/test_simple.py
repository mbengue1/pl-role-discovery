"""
Simple test app to debug the deployment issue.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.title("🔍 Premier League Role Discovery - Debug Mode")

st.write("## Testing Basic Functionality")

# Test 1: Check if we can import basic libraries
try:
    import numpy as np
    st.success("✅ NumPy imported successfully")
except Exception as e:
    st.error(f"❌ NumPy import failed: {e}")

try:
    import pandas as pd
    st.success("✅ Pandas imported successfully")
except Exception as e:
    st.error(f"❌ Pandas import failed: {e}")

try:
    import plotly.express as px
    st.success("✅ Plotly imported successfully")
except Exception as e:
    st.error(f"❌ Plotly import failed: {e}")

# Test 2: Check if data files exist
st.write("## Checking Data Files")

data_path = Path("data/processed")
if data_path.exists():
    st.success("✅ Data directory exists")
    
    # List files
    files = list(data_path.glob("*.csv"))
    st.write(f"Found {len(files)} CSV files:")
    for file in files:
        st.write(f"- {file.name}")
        
    # Try to load a simple file
    try:
        df = pd.read_csv("data/processed/player_clusters.csv")
        st.success(f"✅ Successfully loaded player_clusters.csv ({len(df)} rows)")
        st.write("Sample data:")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"❌ Failed to load player_clusters.csv: {e}")
        
else:
    st.error("❌ Data directory does not exist")

# Test 3: Check current working directory
st.write("## Environment Info")
st.write(f"Current working directory: {Path.cwd()}")
st.write(f"Python version: {pd.__version__}")

# Test 4: Simple visualization
st.write("## Test Visualization")
try:
    import plotly.graph_objects as go
    
    # Create a simple chart
    fig = go.Figure(data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
    fig.update_layout(title="Test Chart")
    st.plotly_chart(fig)
    st.success("✅ Plotly visualization works")
except Exception as e:
    st.error(f"❌ Plotly visualization failed: {e}")
