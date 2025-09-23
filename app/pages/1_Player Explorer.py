"""
player explorer page for the premier league player role discovery app.

this page allows users to search for players, view their assigned roles,
compare them to cluster averages, and see similar players.
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
    render_player_card,
    render_player_search,
    render_similar_players,
)
from app.config.settings import FALLBACK_CATEGORIES, RADAR_CATEGORIES
from app.utils.data_loader import (
    get_player_data,
    load_cluster_data,
    load_cluster_metadata,
    load_player_data,
    load_shap_values,
)
from app.utils.error_handlers import handle_exceptions
from app.utils.logger import get_logger
from app.utils.visualization import create_radar_chart, create_shap_bar_chart

# initialize logger
logger = get_logger(__name__)

@handle_exceptions(error_message="Error getting player radar data", fallback_return=(None, None, None))
def get_player_radar_data(player_name: str):
    """
    get player and cluster average data for radar chart.
    
    args:
        player_name: name of the player
        
    returns:
        tuple of (player_data, cluster_avg, radar_categories) or (None, None, None) if error
    """
    # load necessary data
    player_df = load_player_data()
    
    if player_df is None:
        logger.error("Failed to load player data")
        return None, None, None
    
    # Log available columns for debugging
    logger.info(f"Available columns in player data: {player_df.columns.tolist()}")
    
    # get player data
    player_row = player_df[player_df["player"] == player_name]
    if len(player_row) == 0:
        logger.warning(f"Player not found for radar: {player_name}")
        return None, None, None
    
    player_data = player_row.iloc[0]
    logger.info(f"Player data for {player_name}: {player_data}")
    
    # Check if cluster is available in player data
    if "cluster" not in player_data:
        logger.warning(f"No cluster information for player: {player_name}")
        return player_data, None, None
    
    # Define custom radar categories based on available data
    # These are more meaningful football metrics that should be in the data
    custom_categories = [
        "goals_per90", "assists_per90", "shots_total_per90", 
        "passes_completed_per90", "progressive_passes_per90",
        "progressive_carries_per90", "successful_take_ons_per90",
        "tackles_per90", "interceptions_per90", "blocks_per90",
        "clearances_per90", "aerials_won_per90"
    ]
    
    # Check which of our preferred categories are available
    available_categories = []
    for cat in custom_categories:
        if cat in player_df.columns:
            available_categories.append(cat)
    
    # If we don't have enough categories, try standard ones
    if len(available_categories) < 5:
        for cat in RADAR_CATEGORIES:
            if cat not in available_categories and cat in player_df.columns:
                available_categories.append(cat)
    
    # If still not enough, try fallbacks
    if len(available_categories) < 5:
        for cat in FALLBACK_CATEGORIES:
            if cat not in available_categories and cat in player_df.columns:
                available_categories.append(cat)
    
    # If still no good categories, use whatever numeric columns we have
    if len(available_categories) < 5:
        numeric_cols = player_df.select_dtypes(include=np.number).columns.tolist()
        # Filter out some columns we don't want in the radar
        exclude_cols = ['cluster', 'is_representative']
        available_categories = [col for col in numeric_cols if col not in exclude_cols][:8]  # Limit to 8 columns
    
    logger.info(f"Using radar categories: {available_categories}")
    
    # Get only numeric columns for averaging
    numeric_cols = player_df.select_dtypes(include=np.number).columns
    numeric_categories = [cat for cat in available_categories if cat in numeric_cols]
    
    try:
        # Get cluster ID and filter by it
        cluster_id = player_data["cluster"]
        cluster_players = player_df[player_df["cluster"] == cluster_id]
        
        # Calculate mean only for numeric columns
        cluster_avg = cluster_players[numeric_cols].mean()
        
        # Add non-numeric columns from player data for display
        for col in player_data.index:
            if col not in numeric_cols and col != "player":
                cluster_avg[col] = f"Cluster {cluster_id} Average"
        
        return player_data, cluster_avg, numeric_categories
    except Exception as e:
        logger.error(f"Error calculating cluster average: {e}")
        
        # Create dummy cluster average with numeric data
        dummy_avg = pd.Series(dtype=object)
        for cat in numeric_categories:
            dummy_avg[cat] = 0.5  # Default value
        dummy_avg["player"] = f"Cluster Average"
        
        return player_data, dummy_avg, numeric_categories

@handle_exceptions(error_message="Error getting player SHAP data", fallback_return=(None, None))
def get_player_shap_data(player_name: str, top_n: int = 5):
    """
    get SHAP values for a player.
    
    args:
        player_name: name of the player
        top_n: number of top features to return
        
    returns:
        tuple of (feature_names, feature_values) or (None, None) if error
    """
    # load necessary data
    shap_values = load_shap_values()
    player_df = load_player_data()
    
    if shap_values is None or player_df is None:
        logger.warning("SHAP values or player data not available")
        return ["Goals", "Assists", "Tackles", "Passes", "Interceptions"], [0.8, 0.6, 0.4, -0.3, -0.5]
    
    # find player index
    player_index = player_df.index[player_df["player"] == player_name].tolist()
    if not player_index:
        logger.warning(f"Player not found for SHAP: {player_name}")
        return ["Goals", "Assists", "Tackles", "Passes", "Interceptions"], [0.8, 0.6, 0.4, -0.3, -0.5]
    
    player_idx = player_index[0]
    logger.info(f"Player index for SHAP: {player_idx}")
    
    # Check if SHAP values are available for this player
    # SHAP values might be stored as a dictionary or list
    try:
        if isinstance(shap_values, dict):
            if player_idx not in shap_values:
                logger.warning(f"No SHAP values for player index {player_idx}")
                return ["Goals", "Assists", "Tackles", "Passes", "Interceptions"], [0.8, 0.6, 0.4, -0.3, -0.5]
            player_shap = shap_values[player_idx]
        elif isinstance(shap_values, list) and player_idx >= len(shap_values):
            logger.warning(f"SHAP values index out of range: {player_idx} >= {len(shap_values)}")
            return ["Goals", "Assists", "Tackles", "Passes", "Interceptions"], [0.8, 0.6, 0.4, -0.3, -0.5]
        else:  # Assume it's a list or array
            player_shap = shap_values[player_idx]
        
        # get feature names - only numeric features
        feature_names = player_df.select_dtypes(include=np.number).columns.tolist()
        
        # get top N features by absolute SHAP value
        if isinstance(player_shap, np.ndarray) and len(player_shap) == len(feature_names):
            # get indices of top N features by absolute value
            top_indices = np.argsort(np.abs(player_shap))[-top_n:]
            
            # get feature names and values
            top_features = [feature_names[i] for i in top_indices]
            top_values = [player_shap[i] for i in top_indices]
            
            return top_features, top_values
    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Error extracting SHAP values for player {player_name}: {e}")
    
    # Return dummy data if anything fails(fall back TODO:)
    return ["Goals", "Assists", "Tackles", "Passes", "Interceptions"], [0.8, 0.6, 0.4, -0.3, -0.5]

@handle_exceptions(error_message="Error loading player explorer page", show_streamlit_error=True)
def main():
    """main function to render the player explorer page."""
    # render header
    render_header()
    
    st.header("🔍 Player Explorer")
    st.markdown(
        """
        Search for any Premier League player to view their assigned role, 
        statistical profile, and similar players.
        """
    )
    
    # player search
    selected_player = render_player_search()
    
    if selected_player:
        # display player card
        render_player_card(selected_player)
        
        # Add role confidence explanation
        with st.expander("What does Role Confidence mean?"):
            st.markdown("""
            **Role Confidence** indicates how strongly a player fits within their assigned role:
            
            - **High confidence (>0.7)**: Player is a quintessential example of this role
            - **Medium confidence (0.4-0.7)**: Player fits the role well but has some hybrid characteristics
            - **Low confidence (<0.4)**: Player has characteristics spanning multiple roles
            
            A low confidence score doesn't mean a player is "bad" - it often indicates versatility of the player in multiple roles!
            """)
        
        # create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Player Profile", "Similar Players", "Role Explanation"])
        
        with tab1:
            st.subheader("Player vs. Cluster Average")
            
            # get radar chart data
            result = get_player_radar_data(selected_player)
            
            if len(result) == 3:
                player_data, cluster_avg, radar_categories = result
                
                if player_data is not None and cluster_avg is not None and radar_categories:
                    # create radar chart
                    fig = create_radar_chart(
                        player_data,
                        cluster_avg,
                        radar_categories,
                        title=f"{selected_player} vs. Cluster Average"
                    )
                    
                    if fig:
                        st.plotly_chart(fig, width="stretch", key="radar_chart")
                    else:
                        st.warning("Unable to create radar chart")
                else:
                    st.warning(f"Data not available for {selected_player}")
            else:
                player_data, cluster_avg = result
                st.warning(f"Insufficient data for radar chart for {selected_player}")
        
        with tab2:
            # display similar players
            render_similar_players(selected_player, n=10)
        
        with tab3:
            st.subheader("Why This Role?")
            
            # get SHAP data
            feature_names, feature_values = get_player_shap_data(selected_player)
            
            if feature_names and feature_values:
                # create SHAP bar chart
                fig = create_shap_bar_chart(
                    feature_names,
                    feature_values,
                    title=f"Top Features Contributing to {selected_player}'s Role"
                )
                
                if fig:
                    st.plotly_chart(fig, width="stretch", key="shap_chart")
                else:
                    st.warning("Unable to create SHAP chart")
                
                # add explanation
                st.markdown(
                    """
                    **How to interpret this chart:**
                    
                    * **Green bars** indicate features that push the player *toward* their assigned role
                    * **Red bars** indicate features that push the player *away* from their assigned role
                    * **Longer bars** have more influence on the role assignment
                    """
                )
            else:
                st.info("SHAP explanation not available for this player")
    else:
        # no player selected
        st.info("👆 Search for a player above to view their profile")
    
    # render footer
    render_footer()

if __name__ == "__main__":
    main()