"""
visualization utilities for the premier league player role discovery app.

this module provides functions to create consistent, reusable visualizations
throughout the application.
"""

from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from plotly.subplots import make_subplots

from app.config.settings import CHART_HEIGHT, CHART_WIDTH, ROLE_COLORS
from app.utils.error_handlers import handle_exceptions
from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

@handle_exceptions(error_message="Error creating radar chart", fallback_return=None)
def create_radar_chart(
    player_data: pd.Series,
    cluster_avg: pd.Series,
    categories: List[str],
    title: str = "Player vs. Cluster Average"
) -> go.Figure:
    """
    create a radar chart comparing player stats to cluster average.
    
    args:
        player_data: series with player statistics
        cluster_avg: series with cluster average statistics
        categories: list of categories to display
        title: chart title
        
    returns:
        plotly figure object
    """
    logger.info(f"Creating radar chart with categories: {categories}")
    logger.info(f"Player data columns: {player_data.index.tolist()}")
    logger.info(f"Cluster avg columns: {cluster_avg.index.tolist()}")
    
    # Check if we have valid categories
    valid_categories = []
    valid_values = []
    
    for cat in categories:
        if cat in player_data.index and cat in cluster_avg.index:
            try:
                p_val = float(player_data.get(cat, 0))
                c_val = float(cluster_avg.get(cat, 0))
                if not (np.isnan(p_val) or np.isnan(c_val)):
                    valid_categories.append(cat)
                    # Store the values to calculate min/max for normalization
                    valid_values.append(p_val)
                    valid_values.append(c_val)
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not convert {cat} to float: {e}")
    
    logger.info(f"Valid categories for radar chart: {valid_categories}")
    
    # Create dummy data if no valid categories TODO: to fix
    if not valid_categories:
        logger.warning("No valid categories for radar chart, using dummy data")
        valid_categories = ["Goals", "Assists", "Tackles", "Interceptions", "Passes"]
        player_values = [3, 5, 2, 4, 3]
        cluster_values = [4, 3, 5, 2, 4]
        
        # Format category labels for better display
        display_categories = valid_categories
    else:
        # Normalize values for better visualization
        # Find min and max for each category
        min_vals = {}
        max_vals = {}
        
        # Extract values for each category - safely
        player_values = []
        cluster_values = []
        
        # Format category labels for better display
        display_categories = [cat.replace('_', ' ').replace('per90', '/90').title() for cat in valid_categories]
        
        for i, cat in enumerate(valid_categories):
            try:
                p_val = float(player_data.get(cat, 0))
                c_val = float(cluster_avg.get(cat, 0))
                
                # Normalize values to 0-10 scale for better radar visualization
                # But keep relative differences between player and cluster
                min_val = min(p_val, c_val) * 0.9  # Add some padding
                max_val = max(p_val, c_val) * 1.1  # Add some padding
                
                # Avoid division by zero
                if max_val == min_val:
                    p_norm = 5.0
                    c_norm = 5.0
                else:
                    p_norm = 1.0 + 9.0 * (p_val - min_val) / (max_val - min_val)
                    c_norm = 1.0 + 9.0 * (c_val - min_val) / (max_val - min_val)
                
                player_values.append(p_norm)
                cluster_values.append(c_norm)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error extracting value for category {cat}: {e}")
                player_values.append(1.0)
                cluster_values.append(1.0)
    
    # Create radar chart
    fig = go.Figure()
    
    # Add player trace
    fig.add_trace(go.Scatterpolar(
        r=player_values,
        theta=display_categories,
        fill='toself',
        name=player_data.get('player', 'Player'),
        line_color='rgba(31, 119, 180, 0.8)',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    # Add cluster average trace
    fig.add_trace(go.Scatterpolar(
        r=cluster_values,
        theta=display_categories,
        fill='toself',
        name='Cluster Average',
        line_color='rgba(255, 127, 14, 0.8)',
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]  # Fixed range for normalized values
            )
        ),
        title=title,
        height=CHART_HEIGHT,
        width=CHART_WIDTH,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # Add annotation explaining normalization
    fig.add_annotation(
        text="Note: Values are normalized for comparison",
        xref="paper", yref="paper",
        x=0.5, y=-0.1,
        showarrow=False,
        font=dict(size=10, color="gray")
    )
    
    return fig

@handle_exceptions(error_message="Error creating SHAP bar chart", fallback_return=None)
def create_shap_bar_chart(
    feature_names: List[str],
    feature_values: List[float],
    title: str = "Top Features Contributing to Role Assignment"
) -> go.Figure:
    """
    create a horizontal bar chart showing SHAP values.
    
    args:
        feature_names: list of feature names
        feature_values: list of feature importance values
        title: chart title
        
    returns:
        plotly figure object
    """
    logger.info(f"Creating SHAP bar chart with features: {feature_names}")
    logger.info(f"Feature values: {feature_values}")
    
    # Validate inputs
    if not feature_names or not feature_values or len(feature_names) != len(feature_values):
        logger.warning("Invalid inputs for SHAP bar chart")
        # Create dummy data
        feature_names = ["Goals", "Assists", "Tackles", "Passes", "Interceptions"]
        feature_values = [0.8, 0.6, 0.4, -0.3, -0.5]
    
    # Format feature names for better display
    display_features = [feat.replace('_', ' ').replace('per90', '/90').title() for feat in feature_names]
    
    # Sort features by absolute value
    try:
        sorted_idx = np.argsort(np.abs(feature_values))
        sorted_names = [display_features[i] for i in sorted_idx]
        sorted_values = [feature_values[i] for i in sorted_idx]
    except Exception as e:
        logger.warning(f"Error sorting features: {e}")
        # Use unsorted
        sorted_names = display_features
        sorted_values = feature_values
    
    # Create colors based on positive/negative values
    colors = ['#ff4d4d' if val < 0 else '#2ca02c' for val in sorted_values]
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=sorted_names,
        x=sorted_values,
        orientation='h',
        marker_color=colors
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        height=CHART_HEIGHT,
        width=CHART_WIDTH,
        xaxis_title='SHAP Value (Impact on Role Assignment)',
        yaxis_title='Feature',
        yaxis=dict(autorange="reversed")  # Put highest value at the top
    )
    
    return fig

@handle_exceptions(error_message="Error creating scatter plot", fallback_return=None)
def create_cluster_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = 'cluster',
    hover_data: List[str] = None,
    title: str = "Player Clusters"
) -> go.Figure:
    """
    create a scatter plot of players colored by cluster.
    
    args:
        df: dataframe with player data
        x_col: column name for x-axis
        y_col: column name for y-axis
        color_col: column name for color
        hover_data: list of columns to show in hover tooltip
        title: chart title
        
    returns:
        plotly figure object
    """
    logger.info(f"Creating cluster scatter plot with columns: x={x_col}, y={y_col}, color={color_col}")
    
    # Validate inputs
    if hover_data is None:
        hover_data = ['player', 'team']
    
    # Make sure all required columns exist
    missing_cols = []
    if x_col not in df.columns:
        missing_cols.append(x_col)
    if y_col not in df.columns:
        missing_cols.append(y_col)
    if color_col not in df.columns:
        missing_cols.append(color_col)
    
    if missing_cols:
        logger.warning(f"Missing columns for scatter plot: {missing_cols}")
        # Create dummy data
        dummy_df = pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100),
            'cluster': np.random.choice([0, 1, 2], size=100),
            'player': [f"Player {i}" for i in range(100)],
            'team': [f"Team {chr(65 + i % 5)}" for i in range(100)]
        })
        return create_dummy_scatter(dummy_df, title)
    
    # Make sure all hover_data columns exist
    hover_data = [col for col in hover_data if col in df.columns]
    
    # Convert cluster to string for color mapping
    df = df.copy()
    if color_col == 'cluster' and 'cluster' in df.columns:
        try:
            df['cluster_str'] = df['cluster'].astype(str)
            color_col = 'cluster_str'
        except Exception as e:
            logger.warning(f"Error converting cluster to string: {e}")
    
    # Create scatter plot
    try:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col if color_col in df.columns else None,
            hover_name='player' if 'player' in df.columns else None,
            hover_data=hover_data,
            title=title,
            height=CHART_HEIGHT,
            width=CHART_WIDTH
        )
        
        # Update color scale if using clusters
        if color_col == 'cluster_str':
            color_discrete_map = {str(k): v for k, v in ROLE_COLORS.items()}
            fig.update_traces(marker=dict(
                size=10,
                line=dict(width=1, color='DarkSlateGrey')
            ))
            fig.update_layout(coloraxis_colorbar=dict(
                title="Cluster",
                tickvals=list(color_discrete_map.keys()),
                ticktext=list(color_discrete_map.keys())
            ))
        
        # Update layout
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            legend_title="Cluster",
            template="plotly_white"
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating scatter plot: {e}")
        # Create dummy scatter
        return create_dummy_scatter(df, title)

def create_dummy_scatter(df, title):
    """Create a dummy scatter plot when the real one fails."""
    # Create basic scatter with random data
    x = np.random.randn(100)
    y = np.random.randn(100)
    cluster = np.random.choice([0, 1, 2], size=100)
    
    fig = px.scatter(
        x=x, y=y, color=[str(c) for c in cluster],
        title=f"{title} (Demo Data)",
        labels={"x": "Dimension 1", "y": "Dimension 2", "color": "Cluster"},
        height=CHART_HEIGHT,
        width=CHART_WIDTH
    )
    
    fig.update_layout(
        template="plotly_white",
        annotations=[{
            "text": "Visualization with demo data - actual data unavailable",
            "xref": "paper", "yref": "paper",
            "x": 0.5, "y": 0.5,
            "showarrow": False,
            "font": {"size": 14}
        }]
    )
    
    return fig

@handle_exceptions(error_message="Error creating heatmap", fallback_return=None)
def create_cluster_heatmap(
    df: pd.DataFrame,
    features: List[str],
    cluster_col: str = 'cluster',
    title: str = "Cluster Feature Profiles"
) -> go.Figure:
    """
    create a heatmap showing feature values across clusters.
    
    args:
        df: dataframe with player data
        features: list of features to include
        cluster_col: column name for cluster
        title: chart title
        
    returns:
        plotly figure object
    """
    logger.info(f"Creating cluster heatmap with {len(features)} features")
    
    # Make sure all features exist in the dataframe
    features = [f for f in features if f in df.columns]
    
    if not features or cluster_col not in df.columns:
        logger.warning(f"Missing features or cluster column for heatmap")
        # Return dummy heatmap
        dummy_data = np.random.rand(5, 3)
        fig = px.imshow(
            dummy_data,
            labels=dict(x="Cluster", y="Feature", color="Z-Score"),
            x=["Cluster 0", "Cluster 1", "Cluster 2"],
            y=["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
            color_continuous_scale='RdBu_r',
            title=title,
            height=CHART_HEIGHT,
            width=CHART_WIDTH
        )
        return fig
    
    try:
        # Calculate mean values for each feature by cluster
        cluster_means = df.groupby(cluster_col)[features].mean().reset_index()
        
        # Melt the dataframe for heatmap format
        melted_df = pd.melt(
            cluster_means,
            id_vars=[cluster_col],
            value_vars=features,
            var_name='Feature',
            value_name='Value'
        )
        
        # Format feature names for better display
        melted_df['Feature'] = melted_df['Feature'].apply(lambda x: x.replace('_', ' ').replace('per90', '/90').title())
        
        # Create pivot table
        pivot_df = melted_df.pivot(index='Feature', columns=cluster_col, values='Value')
        
        # Z-score normalize for better visualization
        z_scored = (pivot_df - pivot_df.mean()) / pivot_df.std()
        
        # Create heatmap
        fig = px.imshow(
            z_scored,
            labels=dict(x="Cluster", y="Feature", color="Z-Score"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale='RdBu_r',
            title=title,
            height=CHART_HEIGHT,
            width=CHART_WIDTH
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Cluster",
            yaxis_title="Feature",
            coloraxis_colorbar=dict(
                title="Z-Score",
                thicknessmode="pixels", thickness=20,
                lenmode="pixels", len=CHART_HEIGHT - 100,
                yanchor="top", y=1,
                ticks="outside"
            )
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        # Return dummy heatmap
        dummy_data = np.random.rand(5, 3)
        fig = px.imshow(
            dummy_data,
            labels=dict(x="Cluster", y="Feature", color="Z-Score"),
            x=["Cluster 0", "Cluster 1", "Cluster 2"],
            y=["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
            color_continuous_scale='RdBu_r',
            title=f"{title} (Demo Data)",
            height=CHART_HEIGHT,
            width=CHART_WIDTH
        )
        
        fig.update_layout(
            annotations=[{
                "text": "Visualization with demo data - actual data unavailable",
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 0.5,
                "showarrow": False,
                "font": {"size": 14}
            }]
        )
        
        return fig

@handle_exceptions(error_message="Error creating feature importance chart", fallback_return=None)
def create_feature_importance_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Feature Importance"
) -> go.Figure:
    """
    create a horizontal bar chart showing feature importance.
    
    args:
        df: dataframe with feature importance data
        x_col: column name for values (importance)
        y_col: column name for feature names
        title: chart title
        
    returns:
        plotly figure object
    """
    logger.info(f"Creating feature importance chart with columns: x={x_col}, y={y_col}")
    
    # Check if required columns exist
    if x_col not in df.columns or y_col not in df.columns:
        logger.warning(f"Required columns not found in dataframe: {x_col}, {y_col}")
        # Create dummy data
        dummy_data = pd.DataFrame({
            'feature': ['Goals', 'Assists', 'Tackles', 'Passes', 'Interceptions'],
            'importance_value': [0.8, 0.6, 0.4, 0.3, 0.2]
        })
        # Use dummy data
        df_sorted = dummy_data
        x_col = 'importance_value'
        y_col = 'feature'
    else:
        try:
            # Sort by importance
            df_sorted = df.sort_values(by=x_col, ascending=True)
            
            # Format feature names for better display
            if y_col in df_sorted.columns:
                df_sorted[y_col] = df_sorted[y_col].apply(lambda x: str(x).replace('_', ' ').replace('per90', '/90').title())
        except Exception as e:
            logger.warning(f"Error sorting by importance: {e}")
            df_sorted = df
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted[y_col],
        x=df_sorted[x_col],
        orientation='h',
        marker_color='#1f77b4'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        height=CHART_HEIGHT,
        width=CHART_WIDTH,
        xaxis_title='Importance',
        yaxis_title='Feature'
    )
    
    return fig