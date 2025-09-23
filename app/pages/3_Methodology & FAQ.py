"""
methodology and faq page for the premier league player role discovery app.

this page explains the data sources, methodology, and answers frequently asked
questions about the player role discovery project.
"""

import os
import sys
from pathlib import Path

# add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import streamlit as st

from app.components.ui_components import render_footer, render_header, render_info_box
from app.utils.error_handlers import handle_exceptions
from app.utils.logger import get_logger

# initialize logger
logger = get_logger(__name__)

@handle_exceptions(error_message="Error loading methodology page", show_streamlit_error=True)
def main():
    """main function to render the methodology and faq page."""
    # render header
    render_header()
    
    st.header("📚 Methodology & FAQ")
    
    # create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Data Sources", 
        "Methodology", 
        "Model Evaluation", 
        "FAQ"
    ])
    
    with tab1:
        st.subheader("Data Sources")
        
        st.markdown("""
        ### Primary Data Source
        
        This project uses data from **FBref**, a public source of football statistics:
        
        * **Season:** 2024/25 Premier League
        * **Players:** 563 outfield players with ≥600 minutes played
        * **Features:** 266 statistical metrics per player
        
        ### Data Categories
        
        The dataset includes the following categories of statistics:
        
        * **Standard:** Goals, assists, minutes played, etc.
        * **Shooting:** Shots, shots on target, goals per shot, etc.
        * **Passing:** Pass completion, progressive passes, etc.
        * **Defense:** Tackles, interceptions, blocks, etc.
        * **Possession:** Touches, carries, take-ons, etc.
        * **Miscellaneous:** Aerials won, fouls, etc.
        
        ### Feature Engineering
        
        All raw statistics were processed as follows:
        
        1. **Per-90 normalization** to account for different playing time
        2. **Composite indices** created (PI, CCI, DA, FE)
        3. **Winsorization** at 5th and 95th percentiles to handle outliers
        4. **Standardization** (zero mean, unit variance) for modeling
        """)
        
        # data compliance notice
        render_info_box(
            title="Data Compliance Notice",
            content="""
            This project uses publicly available data for research and educational purposes.
            The raw data is not redistributed and proper attribution is provided.
            """,
            icon="⚖️"
        )
    
    with tab2:
        st.subheader("Methodology")
        
        st.markdown("""
        ### Data Processing Pipeline
        
        1. **Data Collection**
           * FBref exports for Premier League 2024/25 season
           * Filtering to players with ≥600 minutes played
        
        2. **Feature Engineering**
           * Per-90 normalization
           * Composite indices creation
           * Winsorization and standardization
        
        3. **Dimensionality Reduction**
           * PCA to capture 90% variance (3 components)
           * UMAP for 2D visualization
        
        4. **Clustering**
           * K-Means algorithm with k=3
           * Cluster stability assessment via bootstrap
           * Role naming based on distinctive features
        
        5. **Explainability**
           * RandomForest surrogate model
           * SHAP values for feature importance
           * Permutation importance for validation
        
        ### Key Algorithms
        
        * **PCA (Principal Component Analysis):** Linear dimensionality reduction
        * **K-Means:** Centroid-based clustering algorithm
        * **UMAP:** Non-linear dimensionality reduction for visualization
        * **SHAP (SHapley Additive exPlanations):** Feature attribution method
        """)
        
        # methodology diagram
        try:
            image_path = project_root / "app" / "assets" / "methodology_diagram.svg"
            if image_path.exists():
                st.image(
                    str(image_path),
                    caption="Methodology Pipeline",
                    width="stretch"  # Updated from use_column_width
                )
            else:
                st.info("Methodology diagram not available")
        except Exception as e:
            logger.warning(f"Could not load methodology diagram: {e}")
            st.info("Methodology diagram not available")
    
    with tab3:
        st.subheader("Model Evaluation")
        
        st.markdown("""
        ### Clustering Performance
        
        The final clustering model achieved the following metrics:
        
        * **Silhouette Score:** 0.2455 (threshold: ≥0.20)
        * **Stability (ARI):** 0.9143 (threshold: ≥0.70)
        * **Davies-Bouldin Index:** 1.5658 (threshold: ≤1.40)
        
        ### Cluster Distribution
        
        * **Cluster 0 ("The Enforcers"):** 166 players (29.5%)
        * **Cluster 1 ("The Balanced Players"):** 294 players (52.2%)
        * **Cluster 2 ("The Attackers"):** 103 players (18.3%)
        
        ### PCA Performance
        
        * **Components:** 3
        * **Variance Explained:** 90%
        * **Original Features:** 266
        
        ### Validation Approach
        
        * **Bootstrap Stability:** 50 bootstrap samples to assess clustering robustness
        * **Face Validity:** Manual inspection of cluster assignments against football intuition
        * **Surrogate Model:** RandomForest classifier to approximate cluster boundaries
        """)
        
        # create metrics visualization
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Silhouette Score", "0.2455", "+22.8% vs threshold")
        
        with col2:
            st.metric("Stability (ARI)", "0.9143", "+30.6% vs threshold")
        
        with col3:
            st.metric("Davies-Bouldin", "1.5658", "+11.8% vs threshold")
    
    with tab4:
        st.subheader("Frequently Asked Questions")
        
        # create expandable FAQ sections
        with st.expander("Why use unsupervised learning instead of traditional positions?"):
            st.markdown("""
            Traditional positions (DEF, MID, FWD) are too broad and don't capture the nuanced roles
            that modern players fulfill. For example, a "midfielder" could be a defensive anchor,
            a creative playmaker, or a box-to-box runner.
            
            Unsupervised learning discovers patterns directly from the data without imposing
            preconceived categories, allowing us to identify functional roles based on what players
            actually do on the pitch rather than where they nominally line up.
            """)
        
        with st.expander("How were the number of clusters (k=3) determined?"):
            st.markdown("""
            The optimal number of clusters was determined through a combination of:
            
            1. **Quantitative metrics:** Silhouette score, Davies-Bouldin index, and stability (ARI)
            2. **Interpretability:** Ensuring clusters represent meaningful, distinct player roles
            3. **Bootstrap stability:** Testing if clusters remain consistent across resamples
            
            While more granular clusters (e.g., k=5 or k=8) were tested, k=3 provided the best
            balance of statistical validity and clear role differentiation for this dataset.
            """)
        
        with st.expander("Why isn't player X in role Y?"):
            st.markdown("""
            Player role assignments are based entirely on statistical performance, not reputation
            or subjective assessment. Some reasons a player might be assigned to an unexpected role:
            
            1. **Statistical profile:** The player's statistical footprint may differ from their
               perceived playing style
            2. **Team context:** Players in different teams may accumulate different statistics
               despite similar roles
            3. **Sample size:** Players with fewer minutes may have more volatile statistics
            4. **Hybrid roles:** Some players genuinely operate between traditional roles
            
            The clustering is not "right" or "wrong" - it simply groups players with similar
            statistical profiles.
            """)
        
        with st.expander("How are similar players determined?"):
            st.markdown("""
            Similar players are determined based on:
            
            1. **Cluster membership:** Players in the same cluster
            2. **Statistical similarity:** Proximity in the feature space (using either raw features,
               PCA components, or a combination)
            
            The similarity measure is not based on subjective assessment or player reputation,
            but purely on statistical performance metrics.
            """)
        
        with st.expander("Can this approach be extended to other leagues or seasons?"):
            st.markdown("""
            Yes, this methodology is designed to be extensible to:
            
            1. **Other leagues:** Any competition with comparable statistical coverage
            2. **Multiple seasons:** Tracking role evolution over time
            3. **Different sports:** Any sport with rich statistical tracking
            
            The main requirements are consistent statistical tracking and sufficient sample sizes
            (number of players and minutes played).
            """)
        
        with st.expander("How reliable are the SHAP explanations?"):
            st.markdown("""
            SHAP explanations have several strengths and limitations:
            
            **Strengths:**
            - Based on solid game-theoretic principles
            - Consistent attribution of feature importance
            - Local explanations for individual predictions
            
            **Limitations:**
            - Based on a surrogate model (RandomForest), not the original clustering
            - May not capture complex feature interactions perfectly
            - Sensitive to feature correlation
            
            SHAP values should be interpreted as one tool for understanding role assignments,
            not as definitive explanations.
            """)
    
    # render footer
    render_footer()

if __name__ == "__main__":
    main()