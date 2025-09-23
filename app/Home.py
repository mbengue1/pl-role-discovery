"""
home page for the premier league player role discovery app.

this is the main entry point for the streamlit application, providing an
overview of the project and navigation to other pages.
"""

import os
import sys
from pathlib import Path

# add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import streamlit as st

from app.components.ui_components import render_footer, render_header, render_role_legend
from app.utils.data_loader import load_cluster_data, load_player_data
from app.utils.error_handlers import handle_exceptions
from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

@handle_exceptions(error_message="Error getting cluster distribution", fallback_return=None)
def get_cluster_distribution(player_df: pd.DataFrame) -> pd.DataFrame:
    """
    calculate the distribution of players across clusters.
    
    args:
        player_df: dataframe with player data
        
    returns:
        dataframe with cluster distribution or None if error
    """
    if player_df is None or "cluster" not in player_df.columns:
        logger.warning("No cluster column in player data")
        return None
    
    try:
        # Count players in each cluster
        cluster_counts = player_df["cluster"].value_counts().reset_index()
        cluster_counts.columns = ["cluster", "count"]
        
        # Calculate percentages
        total_players = len(player_df)
        cluster_counts["percentage"] = (cluster_counts["count"] / total_players * 100).round(1)
        
        logger.info(f"Cluster distribution: {cluster_counts.to_dict('records')}")
        return cluster_counts
    except Exception as e:
        logger.error(f"Error calculating cluster distribution: {e}")
        return None

@handle_exceptions(error_message="Error loading home page", show_streamlit_error=True)
def main():
    """main function to render the home page."""
    # render header
    render_header()
    
    # introduction section
    st.markdown("""
    ## Welcome to the Premier League Player Role Discovery App
    
    This application uses unsupervised machine learning to discover natural player roles
    based on statistical performance, rather than traditional positions. Explore how players
    cluster together based on their playing style and discover insights about player profiles.
    """)
    
    # role legend
    render_role_legend()
    
    # Display cluster distribution
    st.subheader("Cluster Distribution")
    
    # Load player data
    player_df = load_player_data()
    
    if player_df is not None:
        # Get cluster distribution
        cluster_dist = get_cluster_distribution(player_df)
        
        if cluster_dist is not None and not cluster_dist.empty:
            # Create columns for metrics
            cols = st.columns(len(cluster_dist))
            
            for i, row in enumerate(cluster_dist.to_dict('records')):
                cluster_id = row['cluster']
                # Get role name based on cluster ID (0, 1, 2)
                if cluster_id == 0:
                    role_name = "The Enforcers"
                elif cluster_id == 1:
                    role_name = "The Balanced Players"
                elif cluster_id == 2:
                    role_name = "The Attackers"
                else:
                    role_name = f"Cluster {cluster_id}"
                
                with cols[i]:
                    st.metric(
                        label=f"{role_name}",
                        value=f"{row['count']} players",
                        delta=f"{row['percentage']}%"
                    )
        else:
            st.warning("Cluster distribution data not available")
    
    # methodology overview
    st.markdown("""
    ## Methodology Overview
    
    1. **Data Collection:** Player statistics from FBref for the 2024/25 Premier League season
    2. **Feature Engineering:** Per-90 normalization, composite indices, standardization
    3. **Dimensionality Reduction:** PCA capturing 90% of variance with 3 components
    4. **Clustering:** K-Means algorithm with k=3 clusters
    5. **Explainability:** SHAP values and RandomForest surrogate model
    
    ## Model Performance
    """)
    
    # model performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Silhouette Score", "0.2455", "+22.8% vs threshold")
    
    with col2:
        st.metric("Stability (ARI)", "0.9143", "+30.6% vs threshold")
    
    with col3:
        st.metric("Davies-Bouldin", "1.5658", "+11.8% vs threshold")
    
    # PCA performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("PCA Components", "3", "from 266 features")
    
    with col2:
        st.metric("Variance Explained", "90%", "of original information")
    
    # navigation section
    st.markdown("""
    ## Explore the App
    
    * **Player Explorer:** Search for any player to see their assigned role and statistics
    * **Cluster Explorer:** Visualize player clusters and explore role characteristics
    * **Methodology & FAQ:** Learn more about the approach and data sources
    """)
    
    # render footer
    render_footer()

if __name__ == "__main__":
    main()