"""
cluster explorer page for the premier league player role discovery app.

this page allows users to explore the player clusters through interactive
visualizations, view cluster profiles, and compare different roles.
"""

import os
import sys
from pathlib import Path

# add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.components.ui_components import (
    render_footer,
    render_header,
    render_role_info,
)
from app.config.settings import RADAR_CATEGORIES, ROLE_COLORS
from app.utils.data_loader import (
    load_cluster_data,
    load_cluster_metadata,
    load_cluster_representatives,
    load_distinctive_features,
    load_permutation_importance,
    load_player_data,
    load_pca_data,
    load_umap_data,
)
from app.utils.error_handlers import handle_exceptions
from app.utils.logger import get_logger
from app.utils.visualization import (
    create_cluster_heatmap,
    create_cluster_scatter,
    create_feature_importance_chart,
)

# initialize logger
logger = get_logger(__name__)

@handle_exceptions(error_message="Error loading cluster representatives", fallback_return=None)
def get_cluster_representatives(cluster_id: int, n: int = 5) -> pd.DataFrame:
    """
    get representative players for a specific cluster.
    
    args:
        cluster_id: cluster ID
        n: number of representatives to return
        
    returns:
        dataframe with representative players or None if error
    """
    # load representatives data
    reps_df = load_cluster_representatives()
    
    if reps_df is None:
        return None
    
    # Check if cluster column exists
    if "cluster" not in reps_df.columns:
        logger.warning("No cluster column in representatives data")
        return None
    
    # filter by cluster and limit to top n
    cluster_reps = reps_df[reps_df["cluster"] == cluster_id].head(n)
    
    return cluster_reps

@handle_exceptions(error_message="Error getting distinctive features", fallback_return=None)
def get_distinctive_features(cluster_id: int, n: int = 10) -> pd.DataFrame:
    """
    get distinctive features for a specific cluster.
    
    args:
        cluster_id: cluster ID
        n: number of features to return
        
    returns:
        dataframe with distinctive features or None if error
    """
    # load distinctive features data
    features_df = load_distinctive_features()
    
    if features_df is None:
        return None
    
    # Check if cluster column exists
    if "cluster" not in features_df.columns:
        logger.warning("No cluster column in distinctive features data")
        # Create dummy data
        dummy_data = pd.DataFrame({
            "feature": [f"Feature {i}" for i in range(1, n+1)],
            "z_score": np.random.randn(n),
            "cluster": [cluster_id] * n
        })
        return dummy_data
    
    # filter by cluster and limit to top n
    cluster_features = features_df[features_df["cluster"] == cluster_id].head(n)
    
    return cluster_features

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
        
        # Add role names if available
        metadata = load_cluster_metadata()
        if metadata:
            cluster_counts["role_name"] = cluster_counts["cluster"].apply(
                lambda c: metadata.get(str(c), {}).get("name", f"Cluster {c}")
            )
        else:
            cluster_counts["role_name"] = cluster_counts["cluster"].apply(
                lambda c: f"Cluster {c}"
            )
        
        logger.info(f"Cluster distribution: {cluster_counts.to_dict('records')}")
        return cluster_counts
    except Exception as e:
        logger.error(f"Error calculating cluster distribution: {e}")
        return None

@handle_exceptions(error_message="Error loading cluster explorer page", show_streamlit_error=True)
def main():
    """main function to render the cluster explorer page."""
    # render header
    render_header()
    
    st.header("📊 Cluster Explorer")
    st.markdown(
        """
        Explore the player clusters through interactive visualizations, 
        view cluster profiles, and compare different roles.
        """
    )
    
    # load necessary data
    umap_df = load_umap_data()
    pca_df = load_pca_data()
    cluster_df = load_cluster_data()
    player_df = load_player_data()
    metadata = load_cluster_metadata()
    
    if player_df is None:
        st.error("Unable to load required player data")
        return
    
    # merge dataframes
    merged_df = player_df.copy()
    
    if cluster_df is not None:
        merged_df = pd.merge(merged_df, cluster_df, on="player", how="inner")
    
    if umap_df is not None:
        merged_df = pd.merge(merged_df, umap_df, on="player", how="inner")
    
    if pca_df is not None:
        merged_df = pd.merge(merged_df, pca_df, on="player", how="inner")
    
    # Display cluster distribution
    st.subheader("Cluster Distribution")
    cluster_dist = get_cluster_distribution(merged_df)
    
    if cluster_dist is not None:
        # Create columns for metrics
        cols = st.columns(len(cluster_dist))
        
        for i, row in enumerate(cluster_dist.to_dict('records')):
            with cols[i]:
                st.metric(
                    label=f"{row['role_name']}",
                    value=f"{row['count']} players",
                    delta=f"{row['percentage']}%"
                )
    else:
        st.warning("Cluster distribution data not available")
    
    # visualization section
    st.subheader("Player Landscape")
    
    # visualization type selection
    viz_type = st.radio(
        "Visualization Type:",
        options=["UMAP", "PCA"],
        horizontal=True
    )
    
    if viz_type == "UMAP" and "umap_1" in merged_df.columns and "umap_2" in merged_df.columns:
        # create UMAP scatter plot
        fig = create_cluster_scatter(
            merged_df,
            x_col="umap_1",
            y_col="umap_2",
            color_col="cluster",
            hover_data=["player", "team"],
            title="Player Clusters (UMAP)"
        )
        
        if fig:
            st.plotly_chart(fig, width="stretch", key="umap_scatter")  # Updated from use_container_width
        else:
            st.warning("Unable to create UMAP visualization")
    
    elif viz_type == "PCA" and "pc1" in merged_df.columns and "pc2" in merged_df.columns:
        # create PCA scatter plot
        fig = create_cluster_scatter(
            merged_df,
            x_col="pc1",
            y_col="pc2",
            color_col="cluster",
            hover_data=["player", "team"],
            title="Player Clusters (PCA)"
        )
        
        if fig:
            st.plotly_chart(fig, width="stretch", key="pca_scatter")  # Updated from use_container_width
        else:
            st.warning("Unable to create PCA visualization")
    
    else:
        st.warning(f"{viz_type} data not available")
    
    # cluster exploration section
    st.divider()
    st.subheader("Cluster Profiles")
    
    # get role names from metadata
    role_names = {}
    if metadata:
        for cluster_id, cluster_data in metadata.items():
            if isinstance(cluster_data, dict) and "name" in cluster_data:
                role_names[cluster_id] = cluster_data["name"]
    
    # If no roles found in metadata, use default
    if not role_names:
        role_names = {"0": "The Enforcers", "1": "The Balanced Players", "2": "The Attackers"}
    
    # create cluster selection
    cluster_options = [
        f"{role_names.get(str(i), f'Cluster {i}')} (Cluster {i})"
        for i in sorted([int(k) for k in role_names.keys()])
    ]
    
    selected_cluster_option = st.selectbox(
        "Select a cluster to explore:",
        options=cluster_options
    )
    
    if selected_cluster_option:
        # extract cluster ID from selection
        cluster_id = int(selected_cluster_option.split("(Cluster ")[-1].split(")")[0])
        
        # display role info
        render_role_info(cluster_id)
        
        # create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Feature Profile", "Representative Players", "Feature Importance"])
        
        with tab1:
            # get distinctive features for this cluster
            distinctive_features = get_distinctive_features(cluster_id)
            
            if distinctive_features is not None:
                # create feature profile visualization
                st.subheader("Distinctive Features")
                
                # Check if required columns exist
                if "feature" in distinctive_features.columns and "z_score" in distinctive_features.columns:
                    # display as dataframe
                    st.dataframe(
                        distinctive_features[["feature", "z_score"]],
                        hide_index=True,
                        width="stretch"  # Updated from use_container_width
                    )
                    
                    # create bar chart of z-scores
                    fig = px.bar(
                        distinctive_features,
                        x="z_score",
                        y="feature",
                        orientation="h",
                        title=f"Distinctive Features for Cluster {cluster_id}",
                        color_discrete_sequence=[ROLE_COLORS.get(cluster_id, "#1f77b4")]
                    )
                    
                    fig.update_layout(
                        xaxis_title="Z-Score",
                        yaxis_title="Feature"
                    )
                    
                    st.plotly_chart(fig, width="stretch", key="feature_bar")  # Updated from use_container_width
                else:
                    st.warning("Distinctive features data missing required columns")
            else:
                st.info("Distinctive features not available for this cluster")
        
        with tab2:
            # get representative players for this cluster
            representatives = get_cluster_representatives(cluster_id)
            
            if representatives is not None and len(representatives) > 0:
                st.subheader("Representative Players")
                
                # display as dataframe
                st.dataframe(
                    representatives,
                    hide_index=True,
                    width="stretch"  # Updated from use_container_width
                )
            else:
                st.info("Representative players not available for this cluster")
        
        with tab3:
            # load permutation importance
            importance_df = load_permutation_importance()
            
            if importance_df is not None:
                st.subheader("Feature Importance")
                
                # Check column names in importance_df
                if "feature" in importance_df.columns:
                    feature_col = "feature"
                else:
                    feature_col = importance_df.columns[0]
                
                if "importance" in importance_df.columns:
                    importance_col = "importance"
                elif "value" in importance_df.columns:
                    importance_col = "value"
                else:
                    importance_col = importance_df.columns[1] if len(importance_df.columns) > 1 else None
                
                if importance_col:
                    # create feature importance visualization
                    fig = create_feature_importance_chart(
                        importance_df,
                        x_col=importance_col,
                        y_col=feature_col,
                        title="Global Feature Importance"
                    )
                    
                    if fig:
                        st.plotly_chart(fig, width="stretch", key="importance_chart")  # Updated from use_container_width
                    else:
                        st.warning("Unable to create feature importance chart")
                else:
                    st.warning("Feature importance data missing required columns")
            else:
                st.info("Feature importance data not available")
    
    # cluster comparison section
    st.divider()
    st.subheader("Compare Roles")
    
    # create two columns for cluster selection
    col1, col2 = st.columns(2)
    
    with col1:
        cluster1 = st.selectbox(
            "Select first role:",
            options=cluster_options,
            key="cluster1"
        )
    
    with col2:
        cluster2 = st.selectbox(
            "Select second role:",
            options=cluster_options,
            key="cluster2"
        )
    
    if cluster1 and cluster2:
        # extract cluster IDs from selections
        cluster_id1 = int(cluster1.split("(Cluster ")[-1].split(")")[0])
        cluster_id2 = int(cluster2.split("(Cluster ")[-1].split(")")[0])
        
        # get distinctive features for both clusters
        features1 = get_distinctive_features(cluster_id1)
        features2 = get_distinctive_features(cluster_id2)
        
        if features1 is not None and features2 is not None:
            # create comparison visualization
            st.subheader("Feature Comparison")
            
            # create side-by-side bar charts
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                if "feature" in features1.columns and "z_score" in features1.columns:
                    fig1 = px.bar(
                        features1,
                        x="z_score",
                        y="feature",
                        orientation="h",
                        title=f"{role_names.get(str(cluster_id1), f'Cluster {cluster_id1}')}",
                        color_discrete_sequence=[ROLE_COLORS.get(cluster_id1, "#1f77b4")]
                    )
                    
                    fig1.update_layout(
                        xaxis_title="Z-Score",
                        yaxis_title="Feature"
                    )
                    
                    st.plotly_chart(fig1, width="stretch", key="compare_chart1")  # Updated from use_container_width
                else:
                    st.warning("Feature data missing required columns")
            
            with comp_col2:
                if "feature" in features2.columns and "z_score" in features2.columns:
                    fig2 = px.bar(
                        features2,
                        x="z_score",
                        y="feature",
                        orientation="h",
                        title=f"{role_names.get(str(cluster_id2), f'Cluster {cluster_id2}')}",
                        color_discrete_sequence=[ROLE_COLORS.get(cluster_id2, "#1f77b4")]
                    )
                    
                    fig2.update_layout(
                        xaxis_title="Z-Score",
                        yaxis_title="Feature"
                    )
                    
                    st.plotly_chart(fig2, width="stretch", key="compare_chart2")  # Updated from use_container_width
                else:
                    st.warning("Feature data missing required columns")
        else:
            st.info("Distinctive features not available for comparison")
    
    # render footer
    render_footer()

if __name__ == "__main__":
    main()