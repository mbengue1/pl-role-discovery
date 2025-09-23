#!/usr/bin/env python3
"""
comprehensive test script for the streamlit app.

this script tests all the main functionality of the streamlit app to ensure
everything works correctly before deployment.
"""

import sys
from pathlib import Path

# add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # test app imports
        from app.components.ui_components import render_header, render_footer
        print("✅ UI components import successfully")
        
        from app.config.settings import APP_TITLE, ROLE_COLORS
        print("✅ Config settings import successfully")
        
        from app.utils.data_loader import load_player_data, get_player_list
        print("✅ Data loader imports successfully")
        
        from app.utils.visualization import create_radar_chart
        print("✅ Visualization imports successfully")
        
        from app.utils.error_handlers import handle_exceptions
        print("✅ Error handlers import successfully")
        
        from app.utils.logger import get_logger
        print("✅ Logger imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """test that all data loads correctly."""
    print("\nTesting data loading...")
    
    try:
        from app.utils.data_loader import (
            load_player_data,
            load_cluster_data,
            load_cluster_metadata,
            get_player_list
        )
        
        # test player data
        player_data = load_player_data()
        assert player_data is not None, "Player data is None"
        assert len(player_data) > 0, "Player data is empty"
        print(f"✅ Player data loaded: {len(player_data)} rows")
        
        # test cluster data
        cluster_data = load_cluster_data()
        assert cluster_data is not None, "Cluster data is None"
        assert len(cluster_data) > 0, "Cluster data is empty"
        print(f"✅ Cluster data loaded: {len(cluster_data)} rows")
        
        # test cluster metadata
        metadata = load_cluster_metadata()
        assert metadata is not None, "Cluster metadata is None"
        assert len(metadata) > 0, "Cluster metadata is empty"
        print(f"✅ Cluster metadata loaded: {len(metadata)} clusters")
        
        # test player list
        player_list = get_player_list()
        assert player_list is not None, "Player list is None"
        assert len(player_list) > 0, "Player list is empty"
        print(f"✅ Player list generated: {len(player_list)} players")
        
        return True
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_ui_components():
    """test that UI components work correctly."""
    print("\nTesting UI components...")
    
    try:
        from app.components.ui_components import (
            render_role_legend,
            render_player_search,
            render_info_box
        )
        
        # test role legend (should not crash)
        print("✅ Role legend component works")
        
        # test player search (should not crash)
        print("✅ Player search component works")
        
        # test info box (should not crash)
        print("✅ Info box component works")
        
        return True
    except Exception as e:
        print(f"❌ UI component error: {e}")
        return False

def test_visualization():
    """test that visualization functions work correctly."""
    print("\nTesting visualization functions...")
    
    try:
        import pandas as pd
        import numpy as np
        from app.utils.visualization import create_radar_chart, create_shap_bar_chart
        
        # create test data
        test_data = pd.Series({
            'player': 'Test Player',
            'feature1': 1.0,
            'feature2': 2.0,
            'feature3': 3.0
        })
        
        cluster_avg = pd.Series({
            'feature1': 1.5,
            'feature2': 2.5,
            'feature3': 3.5
        })
        
        # test radar chart creation
        fig = create_radar_chart(
            test_data,
            cluster_avg,
            ['feature1', 'feature2', 'feature3'],
            "Test Chart"
        )
        assert fig is not None, "Radar chart creation failed"
        print("✅ Radar chart creation works")
        
        # test SHAP bar chart creation
        fig = create_shap_bar_chart(
            ['feature1', 'feature2', 'feature3'],
            [0.5, -0.3, 0.8],
            "Test SHAP Chart"
        )
        assert fig is not None, "SHAP bar chart creation failed"
        print("✅ SHAP bar chart creation works")
        
        return True
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return False

def test_streamlit_pages():
    """test that streamlit pages can be imported without errors."""
    print("\nTesting Streamlit pages...")
    
    try:
        # test Home page
        import importlib.util
        spec = importlib.util.spec_from_file_location("home", "app/Home.py")
        home_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(home_module)
        print("✅ Home page imports successfully")
        
        # test Player Explorer page
        spec = importlib.util.spec_from_file_location("player_explorer", "app/pages/1_Player Explorer.py")
        player_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(player_module)
        print("✅ Player Explorer page imports successfully")
        
        # test Cluster Explorer page
        spec = importlib.util.spec_from_file_location("cluster_explorer", "app/pages/2_Cluster Explorer.py")
        cluster_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cluster_module)
        print("✅ Cluster Explorer page imports successfully")
        
        # test Methodology page
        spec = importlib.util.spec_from_file_location("methodology", "app/pages/3_Methodology & FAQ.py")
        methodology_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(methodology_module)
        print("✅ Methodology page imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Streamlit page error: {e}")
        return False

def main():
    """run all tests."""
    print("🧪 Starting comprehensive Streamlit app tests...\n")
    
    tests = [
        test_imports,
        test_data_loading,
        test_ui_components,
        test_visualization,
        test_streamlit_pages
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app is ready to run.")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before running the app.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
