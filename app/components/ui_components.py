"""
reusable ui components for the premier league player role discovery app.

this module provides streamlit components that can be reused across different
pages of the application for a consistent user experience.
"""

from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import streamlit as st

from app.config.settings import (
    APP_DESCRIPTION,
    APP_ICON,
    APP_TITLE,
    DEFAULT_ROLE_DESCRIPTIONS,
    ROLE_COLORS,
)
from app.utils.data_loader import (
    get_player_data,
    get_player_list,
    get_similar_players,
    load_cluster_metadata,
)
from app.utils.error_handlers import handle_exceptions
from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

def render_header():
    """render the application header with title and description."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown(APP_DESCRIPTION)
    st.divider()

def render_footer():
    """render the application footer with attribution and links."""
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Source:** [FBref](https://fbref.com/)")
        
    with col2:
        st.markdown("**Author:** Mouhamed Mbengue")
    
    st.markdown(
        """
        <div style="text-align: center; color: #888888; font-size: 0.8em;">
        Built with Streamlit • Python • Scikit-learn • Plotly
        </div>
        """,
        unsafe_allow_html=True
    )

def render_role_legend():
    """render the role legend with colors and descriptions."""
    metadata = load_cluster_metadata()
    logger.info(f"Rendering role legend with metadata: {metadata}")
    
    st.subheader("Player Roles")
    
    # Check if metadata contains role information
    role_names = {}
    if metadata:
        for cluster_id, cluster_data in metadata.items():
            if isinstance(cluster_data, dict) and "name" in cluster_data:
                role_names[cluster_id] = cluster_data["name"]
    
    # If no roles found in metadata, use default
    if not role_names:
        logger.warning("No role names found in metadata, using defaults")
        role_names = {"0": "The Enforcers", "1": "The Balanced Players", "2": "The Attackers"}
    
    # Create columns only if we have roles
    if role_names:
        # Create a list of column widths (all equal)
        col_widths = [1] * len(role_names)
        cols = st.columns(col_widths)
        
        for i, (cluster_id, role_name) in enumerate(role_names.items()):
            color = ROLE_COLORS.get(int(cluster_id), "#888888")
            description = DEFAULT_ROLE_DESCRIPTIONS.get(int(cluster_id), "")
            
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        border-left: 5px solid {color}; 
                        padding-left: 10px;
                        margin-bottom: 10px;
                    ">
                    <h4 style="margin: 0;">{role_name}</h4>
                    <p style="font-size: 0.9em; color: #666;">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("No role definitions found")

@handle_exceptions(error_message="Error rendering player search", show_streamlit_error=False)
def render_player_search(key: str = "player_search") -> Optional[str]:
    """
    render a player search box with autocomplete.
    
    args:
        key: unique key for the streamlit component
        
    returns:
        selected player name or None if no selection
    """
    player_list = get_player_list()
    
    if not player_list:
        st.warning("No player data available")
        return None
    
    selected_player = st.selectbox(
        "Search for a player:",
        options=player_list,
        index=None,
        placeholder="Type a player name...",
        key=key
    )
    
    return selected_player

@handle_exceptions(error_message="Error rendering player card", show_streamlit_error=False)
def render_player_card(player_name: str):
    """
    render a card with player information.
    
    args:
        player_name: name of the player to display
    """
    player_data = get_player_data(player_name)
    
    if player_data is None:
        st.warning(f"Player data not found for {player_name}")
        return
    
    logger.info(f"Rendering player card for {player_name}: {player_data}")
    
    # Extract player info
    team = player_data.get("team", "Unknown")
    
    # Get role information - check if directly in player data
    role_name = None
    role_confidence = 0
    
    if "role_name" in player_data:
        role_name = player_data["role_name"]
        role_confidence = player_data.get("role_confidence", 0)
    elif "cluster" in player_data:
        cluster = player_data["cluster"]
        # Get cluster metadata
        metadata = load_cluster_metadata()
        if metadata and str(cluster) in metadata:
            cluster_data = metadata[str(cluster)]
            if isinstance(cluster_data, dict) and "name" in cluster_data:
                role_name = cluster_data["name"]
    
    # Fallback if no role name found
    if not role_name:
        if "cluster" in player_data:
            cluster = player_data["cluster"]
            role_name = f"Cluster {cluster}"
        else:
            role_name = "Unknown Role"
    
    # Get role color
    color = "#888888"  # default color
    if "cluster" in player_data:
        cluster = player_data["cluster"]
        color = ROLE_COLORS.get(int(cluster), "#888888")
    
    # Create player card with better contrast
    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        ">
            <h2 style="margin-top: 0; color: #333;">{player_name}</h2>
            <p><strong style="color: #333;">Team:</strong> <span style="color: #333;">{team}</span></p>
            <p><strong style="color: #333;">Role:</strong> 
                <span style="
                    background-color: {color}; 
                    color: #ffffff;
                    padding: 3px 8px;
                    border-radius: 3px;
                    text-shadow: 0px 0px 2px rgba(0,0,0,0.5);
                ">
                    {role_name}
                </span>
            </p>
            <p><strong style="color: #333;">Role Confidence:</strong> <span style="color: #333;">{role_confidence:.2f}</span></p>
        </div>
        """,
        unsafe_allow_html=True
    )

@handle_exceptions(error_message="Error rendering similar players", show_streamlit_error=False)
def render_similar_players(player_name: str, n: int = 5):
    """
    render a table of players similar to the specified player.
    
    args:
        player_name: name of the player to find similar players for
        n: number of similar players to display
    """
    similar_players = get_similar_players(player_name, n)
    
    if similar_players is None or len(similar_players) == 0:
        st.info(f"No similar players found for {player_name}")
        return
    
    st.subheader(f"Players Similar to {player_name}")
    st.dataframe(
        similar_players,
        hide_index=True,
        width="stretch"  # Updated from use_container_width
    )

@handle_exceptions(error_message="Error rendering role info", show_streamlit_error=False)
def render_role_info(cluster_id: int):
    """
    render information about a specific role/cluster.
    
    args:
        cluster_id: cluster ID to display information for
    """
    # Get cluster metadata
    metadata = load_cluster_metadata()
    logger.info(f"Rendering role info for cluster {cluster_id} with metadata: {metadata}")
    
    role_name = None
    description = None
    
    # Try to get from metadata
    if metadata and str(cluster_id) in metadata:
        cluster_data = metadata[str(cluster_id)]
        if isinstance(cluster_data, dict):
            if "name" in cluster_data:
                role_name = cluster_data["name"]
            if "description" in cluster_data:
                description = cluster_data["description"]
    
    # Fallbacks
    if not role_name:
        role_name = f"Cluster {cluster_id}"
    
    if not description:
        description = DEFAULT_ROLE_DESCRIPTIONS.get(cluster_id, "No description available")
    
    # Get role color
    color = ROLE_COLORS.get(cluster_id, "#888888")
    
    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color}; 
            padding-left: 15px;
            margin-bottom: 20px;
        ">
            <h2 style="margin-top: 0; color: #333;">{role_name}</h2>
            <p style="color: #333;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_info_box(title: str, content: str, icon: str = "ℹ️"):
    """
    render an information box with title and content.
    
    args:
        title: box title
        content: box content
        icon: emoji icon to display
    """
    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f5f5f5;
        ">
            <h3 style="margin-top: 0; color: #333;">{icon} {title}</h3>
            <p style="color: #333;">{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_loading_spinner(text: str = "Loading data..."):
    """
    render a loading spinner with text.
    
    args:
        text: text to display with spinner
    """
    with st.spinner(text):
        # This is a placeholder for actual loading operations
        pass