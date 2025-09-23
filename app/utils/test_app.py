"""
test script for validating the premier league player role discovery app.

this script tests the core functionality of the app by loading data and
checking that essential components are working correctly.
"""

import os
import sys
from pathlib import Path

# add the app directory to the path so we can import modules
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path.parent))

import pandas as pd

from app.utils.data_loader import (
    get_player_data,
    get_player_list,
    get_similar_players,
    load_cluster_data,
    load_cluster_metadata,
    load_cluster_representatives,
    load_distinctive_features,
    load_pca_data,
    load_player_data,
    load_role_classifier,
    load_shap_values,
    load_umap_data,
)
from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

def test_data_loading():
    """test that all data files can be loaded correctly."""
    logger.info("Testing data loading...")
    
    # test player data loading
    player_data = load_player_data()
    assert player_data is not None, "Failed to load player data"
    assert len(player_data) > 0, "Player data is empty"
    logger.info(f"✅ Player data loaded successfully: {len(player_data)} rows")
    
    # test cluster data loading
    cluster_data = load_cluster_data()
    assert cluster_data is not None, "Failed to load cluster data"
    assert len(cluster_data) > 0, "Cluster data is empty"
    logger.info(f"✅ Cluster data loaded successfully: {len(cluster_data)} rows")
    
    # test PCA data loading
    pca_data = load_pca_data()
    if pca_data is not None:
        logger.info(f"✅ PCA data loaded successfully: {len(pca_data)} rows")
    else:
        logger.warning("⚠️ PCA data not found")
    
    # test UMAP data loading
    umap_data = load_umap_data()
    if umap_data is not None:
        logger.info(f"✅ UMAP data loaded successfully: {len(umap_data)} rows")
    else:
        logger.warning("⚠️ UMAP data not found")
    
    # test cluster metadata loading
    metadata = load_cluster_metadata()
    assert metadata is not None, "Failed to load cluster metadata"
    # Check for role names in a different format
    has_roles = any("name" in cluster_data for cluster_data in metadata.values())
    assert has_roles, "Cluster metadata missing role names"
    logger.info(f"✅ Cluster metadata loaded successfully")
    
    # test role classifier loading
    classifier = load_role_classifier()
    if classifier is not None:
        logger.info(f"✅ Role classifier loaded successfully")
    else:
        logger.warning("⚠️ Role classifier not found")
    
    # test SHAP values loading
    shap_values = load_shap_values()
    if shap_values is not None:
        logger.info(f"✅ SHAP values loaded successfully")
    else:
        logger.warning("⚠️ SHAP values not found")
    
    logger.info("Data loading tests completed")

def test_player_functions():
    """test player-specific functions."""
    logger.info("Testing player functions...")
    
    # test player list
    player_list = get_player_list()
    assert player_list is not None, "Failed to get player list"
    assert len(player_list) > 0, "Player list is empty"
    logger.info(f"✅ Player list generated successfully: {len(player_list)} players")
    
    # test player data retrieval
    if player_list:
        test_player = player_list[0]
        player_data = get_player_data(test_player)
        assert player_data is not None, f"Failed to get data for player: {test_player}"
        logger.info(f"✅ Player data retrieved successfully for: {test_player}")
        
        # test similar players
        similar_players = get_similar_players(test_player, n=5)
        if similar_players is not None:
            assert len(similar_players) > 0, f"No similar players found for: {test_player}"
            logger.info(f"✅ Similar players found for: {test_player}")
        else:
            logger.warning(f"⚠️ Similar players function failed for: {test_player}")
    
    logger.info("Player function tests completed")

def run_all_tests():
    """run all test functions."""
    logger.info("Starting app validation tests...")
    
    try:
        test_data_loading()
        test_player_functions()
        logger.info("✅ All tests passed successfully!")
        return True
    except AssertionError as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)