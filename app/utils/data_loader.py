"""
data loading utilities for the premier league player role discovery app.

this module provides functions to load data from files with proper caching,
validation, and error handling.
"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import streamlit as st

from app.config.settings import (
    CLUSTER_METADATA_PATH,
    CLUSTER_REPRESENTATIVES_PATH,
    DISTINCTIVE_FEATURES_PATH,
    PERMUTATION_IMPORTANCE_PATH,
    PLAYER_CLUSTERS_PATH,
    PLAYER_DATA_PATH,
    PLAYER_PCA_PATH,
    PLAYER_UMAP_PATH,
    ROLE_CLASSIFIER_PATH,
    SHAP_VALUES_PATH,
)
from app.utils.error_handlers import handle_exceptions, validate_dataframe
from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading player data", fallback_return=None)
def load_player_data() -> Optional[pd.DataFrame]:
    """
    load the main player data with caching.
    
    returns:
        dataframe with player statistics or None if loading fails
    """
    logger.info(f"Loading player data from {PLAYER_DATA_PATH}")
    
    try:
        # Try to load with explicit data types to avoid conversion issues
        df = pd.read_csv(
            PLAYER_DATA_PATH,
            dtype={
                'player': str,
                'team': str,
                'role_name': str,
                'is_representative': bool,
                # Let numeric columns be inferred
            }
        )
    except Exception as e:
        logger.error(f"Error loading player data with dtypes: {e}")
        # Fallback to default loading
        df = pd.read_csv(PLAYER_DATA_PATH)
    
    if not validate_dataframe(df, required_columns=["player", "team"]):
        return None
    
    # Ensure cluster is numeric if present
    if "cluster" in df.columns:
        try:
            df["cluster"] = pd.to_numeric(df["cluster"])
        except Exception as e:
            logger.warning(f"Could not convert cluster column to numeric: {e}")
    
    logger.info(f"Successfully loaded player data: {len(df)} players")
    return df

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading cluster data", fallback_return=None)
def load_cluster_data() -> Optional[pd.DataFrame]:
    """
    load the player cluster assignments with caching.
    
    returns:
        dataframe with player cluster assignments or None if loading fails
    """
    logger.info(f"Loading cluster data from {PLAYER_CLUSTERS_PATH}")
    
    try:
        df = pd.read_csv(
            PLAYER_CLUSTERS_PATH,
            dtype={
                'player': str,
                'team': str,
                'position': str,
                # Let cluster be inferred
            }
        )
    except Exception as e:
        logger.error(f"Error loading cluster data with dtypes: {e}")
        # Fallback to default loading
        df = pd.read_csv(PLAYER_CLUSTERS_PATH)
    
    if not validate_dataframe(df, required_columns=["player"]):
        return None
    
    # Ensure cluster is numeric if present
    if "cluster" in df.columns:
        try:
            df["cluster"] = pd.to_numeric(df["cluster"])
        except Exception as e:
            logger.warning(f"Could not convert cluster column to numeric: {e}")
    
    logger.info(f"Successfully loaded cluster data: {len(df)} players")
    return df

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading PCA projections", fallback_return=None)
def load_pca_data() -> Optional[pd.DataFrame]:
    """
    load the PCA projections with caching.
    
    returns:
        dataframe with PCA projections or None if loading fails
    """
    logger.info(f"Loading PCA data from {PLAYER_PCA_PATH}")
    
    try:
        df = pd.read_csv(PLAYER_PCA_PATH)
    except Exception as e:
        logger.error(f"Error loading PCA data: {e}")
        return None
    
    if not validate_dataframe(df):
        return None
    
    logger.info(f"Successfully loaded PCA data: {len(df)} players")
    return df

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading UMAP projections", fallback_return=None)
def load_umap_data() -> Optional[pd.DataFrame]:
    """
    load the UMAP projections with caching.
    
    returns:
        dataframe with UMAP projections or None if loading fails
    """
    logger.info(f"Loading UMAP data from {PLAYER_UMAP_PATH}")
    
    try:
        df = pd.read_csv(PLAYER_UMAP_PATH)
    except Exception as e:
        logger.error(f"Error loading UMAP data: {e}")
        return None
    
    if not validate_dataframe(df):
        return None
    
    logger.info(f"Successfully loaded UMAP data: {len(df)} players")
    return df

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading cluster metadata", fallback_return={})
def load_cluster_metadata() -> Dict[str, Any]:
    """
    load the cluster metadata with caching.
    
    returns:
        dictionary with cluster metadata or empty dict if loading fails
    """
    logger.info(f"Loading cluster metadata from {CLUSTER_METADATA_PATH}")
    
    try:
        with open(CLUSTER_METADATA_PATH, "r") as f:
            metadata = json.load(f)
    except Exception as e:
        logger.error(f"Error loading cluster metadata: {e}")
        return {}
    
    logger.info(f"Successfully loaded cluster metadata")
    return metadata

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading cluster representatives", fallback_return=None)
def load_cluster_representatives() -> Optional[pd.DataFrame]:
    """
    load the cluster representative players with caching.
    
    returns:
        dataframe with representative players or None if loading fails
    """
    logger.info(f"Loading cluster representatives from {CLUSTER_REPRESENTATIVES_PATH}")
    
    try:
        df = pd.read_csv(CLUSTER_REPRESENTATIVES_PATH)
    except Exception as e:
        logger.error(f"Error loading cluster representatives: {e}")
        return None
    
    if not validate_dataframe(df):
        return None
    
    # Ensure cluster is numeric if present
    if "cluster" in df.columns:
        try:
            df["cluster"] = pd.to_numeric(df["cluster"])
        except Exception as e:
            logger.warning(f"Could not convert cluster column to numeric: {e}")
    
    logger.info(f"Successfully loaded cluster representatives")
    return df

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading distinctive features", fallback_return=None)
def load_distinctive_features() -> Optional[pd.DataFrame]:
    """
    load the distinctive features for each cluster with caching.
    
    returns:
        dataframe with distinctive features or None if loading fails
    """
    logger.info(f"Loading distinctive features from {DISTINCTIVE_FEATURES_PATH}")
    
    try:
        df = pd.read_csv(DISTINCTIVE_FEATURES_PATH)
    except Exception as e:
        logger.error(f"Error loading distinctive features: {e}")
        return None
    
    if not validate_dataframe(df):
        return None
    
    # Ensure cluster is numeric if present
    if "cluster" in df.columns:
        try:
            df["cluster"] = pd.to_numeric(df["cluster"])
        except Exception as e:
            logger.warning(f"Could not convert cluster column to numeric: {e}")
    
    logger.info(f"Successfully loaded distinctive features")
    return df

@st.cache_resource
@handle_exceptions(error_message="Error loading role classifier model", fallback_return=None)
def load_role_classifier():
    """
    load the role classifier model with caching.
    
    returns:
        trained classifier model or None if loading fails
    """
    logger.info(f"Loading role classifier from {ROLE_CLASSIFIER_PATH}")
    
    try:
        with open(ROLE_CLASSIFIER_PATH, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        logger.error(f"Error loading role classifier: {e}")
        return None
    
    logger.info(f"Successfully loaded role classifier model")
    return model

@st.cache_resource
@handle_exceptions(error_message="Error loading SHAP values", fallback_return=None)
def load_shap_values():
    """
    load the SHAP values with caching.
    
    returns:
        SHAP values or None if loading fails
    """
    logger.info(f"Loading SHAP values from {SHAP_VALUES_PATH}")
    
    try:
        with open(SHAP_VALUES_PATH, "rb") as f:
            shap_values = pickle.load(f)
    except Exception as e:
        logger.error(f"Error loading SHAP values: {e}")
        return None
    
    logger.info(f"Successfully loaded SHAP values")
    return shap_values

@st.cache_data(ttl=3600)
@handle_exceptions(error_message="Error loading permutation importance", fallback_return=None)
def load_permutation_importance() -> Optional[pd.DataFrame]:
    """
    load the permutation importance values with caching.
    
    returns:
        dataframe with permutation importance or None if loading fails
    """
    logger.info(f"Loading permutation importance from {PERMUTATION_IMPORTANCE_PATH}")
    
    try:
        df = pd.read_csv(PERMUTATION_IMPORTANCE_PATH)
    except Exception as e:
        logger.error(f"Error loading permutation importance: {e}")
        return None
    
    if not validate_dataframe(df):
        return None
    
    logger.info(f"Successfully loaded permutation importance")
    return df

def get_player_list() -> List[str]:
    """
    get a sorted list of all player names.
    
    returns:
        list of player names sorted alphabetically
    """
    df = load_player_data()
    if df is None or "player" not in df.columns:
        logger.warning("Unable to get player list, returning empty list")
        return []
    
    try:
        # Ensure player names are strings
        player_names = df["player"].astype(str).unique().tolist()
        return sorted(player_names)
    except Exception as e:
        logger.error(f"Error getting player list: {e}")
        return []

def get_player_data(player_name: str) -> Optional[pd.Series]:
    """
    get data for a specific player.
    
    args:
        player_name: name of the player to retrieve
        
    returns:
        series with player data or None if player not found
    """
    df = load_player_data()
    if df is None:
        return None
    
    try:
        player_data = df[df["player"] == player_name]
        if len(player_data) == 0:
            logger.warning(f"Player not found: {player_name}")
            return None
        
        return player_data.iloc[0]
    except Exception as e:
        logger.error(f"Error getting player data: {e}")
        return None

def get_similar_players(player_name: str, n: int = 5) -> Optional[pd.DataFrame]:
    """
    find players similar to the specified player.
    
    args:
        player_name: name of the player to find similar players for
        n: number of similar players to return
        
    returns:
        dataframe with similar players or None if player not found
    """
    # Load the main player data
    player_df = load_player_data()
    if player_df is None:
        return None
    
    try:
        # Find player's data
        player_row = player_df[player_df["player"] == player_name]
        if len(player_row) == 0:
            logger.warning(f"Player not found for similarity: {player_name}")
            return None
        
        player_data = player_row.iloc[0]
        
        # Check if cluster is available
        if "cluster" not in player_data:
            logger.warning(f"No cluster information for player: {player_name}")
            # Create dummy similar players
            dummy_data = {
                "player": [f"Similar Player {i+1}" for i in range(n)],
                "team": ["Team A", "Team B", "Team C", "Team A", "Team B"],
                "role_name": ["Same Role"] * n
            }
            return pd.DataFrame(dummy_data).head(n)
        
        # Get cluster ID
        cluster_id = player_data["cluster"]
        
        # Get other players in the same cluster
        similar_players = player_df[
            (player_df["cluster"] == cluster_id) & 
            (player_df["player"] != player_name)
        ]
        
        # If no similar players found, return None
        if len(similar_players) == 0:
            logger.warning(f"No similar players found for: {player_name}")
            return None
        
        # Select columns to display
        display_cols = ["player", "team"]
        if "role_name" in similar_players.columns:
            display_cols.append("role_name")
        
        return similar_players[display_cols].head(n)
    except Exception as e:
        logger.error(f"Error finding similar players: {e}")
        return None