"""
application-wide settings and constants.

module provides centralized configuration for the premier league
player role discovery app.
"""

# app settings
APP_TITLE = "premier league player role discovery"
APP_SUBTITLE = "unsupervised machine learning + interactive visualization"
APP_ICON = "⚽"
APP_DESCRIPTION = """
Discover player roles in the Premier League using unsupervised machine learning.
This app allows you to explore player clusters, understand role assignments,
and compare players across different statistical dimensions.
"""

# data paths
PLAYER_DATA_PATH = "data/processed/streamlit_player_data.csv"
PLAYER_CLUSTERS_PATH = "data/processed/player_clusters.csv"
PLAYER_PCA_PATH = "data/processed/player_pca_projection.csv"
PLAYER_UMAP_PATH = "data/processed/player_umap_2d.csv"
CLUSTER_METADATA_PATH = "data/processed/cluster_metadata.json"
ROLE_CLASSIFIER_PATH = "models/role_classifier.pkl"
SHAP_VALUES_PATH = "data/processed/shap_values.pkl"
DISTINCTIVE_FEATURES_PATH = "data/processed/distinctive_features.csv"
CLUSTER_REPRESENTATIVES_PATH = "data/processed/cluster_representatives.csv"
PERMUTATION_IMPORTANCE_PATH = "data/processed/permutation_importance.csv"

# visualization settings
CHART_WIDTH = 800
CHART_HEIGHT = 500

# color settings
ROLE_COLORS = {
    0: "#1f77b4",  # the enforcers (blue)
    1: "#ff7f0e",  # the balanced players (orange)
    2: "#2ca02c",  # the attackers (green)
}

# default descriptions
DEFAULT_ROLE_DESCRIPTIONS = {
    0: "Players focused on defensive duties and ball recovery",
    1: "Well-rounded players contributing across multiple phases of play",
    2: "Attack-minded players with high goal contribution metrics"
}

# radar chart categories  match column names in the player data
# Checking for these specific stats that are likely to be in the dataset
RADAR_CATEGORIES = [
    "goals",
    "assists", 
    "shots_total",
    "passes_completed",
    "progressive_passes",
    "progressive_carries",
    "successful_take_ons",
    "tackles",
    "interceptions",
    "blocks",
    "clearances",
    "aerials_won",
    "minutes",
    "goals_per90",
    "assists_per90",
    "x",  # Likely PCA or UMAP dimension
    "y",  # Likely PCA or UMAP dimension
    "centroid_distance",
    "role_confidence"
]

# Additional stats to try if the above aren't found
FALLBACK_CATEGORIES = [
    "goals",
    "assists",
    "shots",
    "passes",
    "tackles",
    "interceptions",
    "blocks",
    "clearances",
    "minutes",
    "x",
    "y"
]