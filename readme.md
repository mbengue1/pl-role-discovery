# Premier League Player Role Discovery

**Unsupervised Machine Learning + Interactive Visualization**

## Overview

This project uses unsupervised machine learning to discover data-driven player roles from Premier League statistics. Instead of relying on traditional position labels (DEF, MID, FWD), the model clusters players into functional roles based on advanced match statistics.

The project delivers an interactive Streamlit web app that allows users to:

* Search for any Premier League player
* View their clustered role and similar players
* Explore role-specific statistics via radar charts and heatmaps
* Visualize the player landscape in 2D PCA/UMAP scatter plots
* Understand which features drive role assignment using explainability tools

## Quick Start

### Setup

```bash
# Clone the repository
git clone https://github.com/mbengue1/pl-role-discovery.git
cd pl-role-discovery

# Create and activate conda environment
conda create -n prem-discovery python=3.11
conda activate prem-discovery

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
# Launch the Streamlit app
streamlit run app/Home.py
```

Visit `http://localhost:8501` in your browser to explore the app.

### Deployed Version

The app is also deployed on Streamlit Cloud: [pl-role-discovery.streamlit.app](https://pl-role-discovery.streamlit.app)

## Project Structure

```
pl-role-discovery/
├── app/                       # Streamlit application
│   ├── Home.py               # Main app entry point
│   ├── assets/               # Static assets
│   ├── components/           # UI components
│   ├── config/               # Configuration
│   ├── pages/                # App pages
│   │   ├── 1_Player Explorer.py
│   │   ├── 2_Cluster Explorer.py
│   │   └── 3_Methodology & FAQ.py
│   └── utils/                # Utility functions
├── data/                     # Data files
│   ├── processed/            # Processed datasets
│   └── raw/                  # Raw data (not tracked)
├── notebooks/                # Jupyter notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_pca_clustering.ipynb
├── planning/                 # Project documentation
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Methodology

### Data Processing Pipeline

1. **Data Collection**
   - FBref exports for Premier League 2024/25 season
   - Filtering to players with ≥600 minutes played

2. **Feature Engineering**
   - Per-90 normalization
   - Composite indices creation (PI, CCI, DA, FE)
   - Winsorization and standardization

3. **Dimensionality Reduction**
   - PCA to capture 90% variance (3 components)
   - UMAP for 2D visualization

4. **Clustering**
   - K-Means algorithm with k=3
   - Cluster stability assessment via bootstrap
   - Role naming based on distinctive features

### Discovered Player Roles

1. **The Enforcers (Cluster 0)**: Defensive specialists with high tackles, interceptions, and blocks
2. **The Balanced Players (Cluster 1)**: Versatile players with balanced attacking and defensive contributions
3. **The Attackers (Cluster 2)**: Goal threats with high shots on target and clinical finishing

### Model Performance

- **Silhouette Score**: 0.2455 (threshold: ≥0.20)
- **Stability (ARI)**: 0.9143 (threshold: ≥0.70)
- **Davies-Bouldin**: 1.5658 (threshold: ≤1.40)
- **PCA Components**: 3 (90% variance retained)

## App Features

### Home Page
- Project overview and role legend
- Cluster distribution statistics
- Model performance metrics

### Player Explorer
- Player search with autocomplete
- Role assignment with confidence
- Radar charts comparing player to cluster average
- Similar players by statistical profile
- SHAP explanations for role assignment

### Cluster Explorer
- Interactive UMAP/PCA scatter plots
- Cluster profile heatmaps
- Representative players per role
- Role comparison side-by-side
- Feature importance visualization

### Methodology & FAQ
- Data sources and processing details
- Methodology explanation
- Model evaluation metrics
- Frequently asked questions

## Tech Stack

- **Data Processing**: pandas, numpy, scikit-learn
- **Machine Learning**: scikit-learn, shap, umap-learn
- **Visualization**: plotly, seaborn, matplotlib
- **Web App**: streamlit
- **Deployment**: Streamlit Community Cloud

## Future Improvements

- Multi-season analysis: Track player role evolution over time
- Team context features: Incorporate team playing style metrics
- Deep learning embeddings: Experiment with autoencoders for representation learning
- Temporal models: Analyze in-season role shifts
- Export functionality: Generate PDF reports for players/teams

## Data Source

This project uses publicly available data from [FBref](https://fbref.com/). All data is used for educational and research purposes only.

## Author

**Mouhamed Mbengue**