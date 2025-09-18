

# 📊 Premier League Player Role Discovery

**Unsupervised Machine Learning + Interactive Visualization**

## 🔎 Overview

This project applies **unsupervised machine learning** to **Premier League player statistics** to discover **data-driven player roles**.
Instead of relying on traditional position labels (DEF, MID, FWD), the model clusters players into **functional roles**—such as “Progressive Playmaker,” “Box-to-Box Midfielder,” “Clinical Striker,” or “Pressing Defender”—based on advanced match statistics.

The final output is an **interactive Streamlit web app** that allows users to:

* Search for any Premier League player
* View their **clustered role** and similar players
* Explore role-specific statistics via **radar charts and heatmaps**
* Visualize the player landscape in **2D PCA/UMAP scatter plots**
* Understand which features drive role assignment using **explainability tools (SHAP/Permutation Importance)**

---



## ⚙️ Features

* 📈 **Feature Engineering**: Per-90 normalization + composite indices (e.g., progression, chance creation, defensive activity)
* 🧩 **Clustering**: PCA + K-Means/Gaussian Mixture Models to group players into roles
* 🔍 **Explainability**: SHAP/permutation importance to highlight drivers behind role assignment
* 🎨 **Visualization**: Interactive radar charts, scatter plots, role heatmaps (Plotly + Streamlit)
* 🔗 **Player Similarity Search**: Find nearest neighbors in feature space (cosine similarity)
* 🌐 **Deployment**: Deployed to Streamlit Cloud for easy access

---

## 📂 Project Structure

```
premier-league-role-discovery/
  ├── app/                     # Streamlit app
  │   ├── Home.py
  │   ├── pages/
  │   │   ├── 1_Player Explorer.py
  │   │   ├── 2_Cluster Explorer.py
  │   │   └── 3_Methodology & FAQ.py
  ├── data/
  │   ├── raw/                 # original CSVs
  │   └── processed/           # cleaned feature matrix, model outputs
  ├── models/
  │   ├── kmeans.pkl
  │   ├── pca.pkl
  │   └── role_classifier.pkl
  ├── notebooks/
  │   ├── 01_data_cleaning.ipynb
  │   ├── 02_feature_engineering.ipynb
  │   ├── 03_model_selection.ipynb
  │   └── 04_visualization.ipynb
  ├── planning/                # Research and planning documents
  │   ├── documentation.md
  │   ├── multi-agent-plan.md
  │   └── research-results/
  │       └── plan.json
  ├── outputs/                 # Multi-agent research outputs
  │   ├── raw/                 # Individual research task results
  │   ├── synthesis/           # Synthesized design decisions
  │   └── citations/           # Citation verification
  ├── scripts/                 # Research automation
  │   ├── run_subagents.py
  │   ├── synthesize.py
  │   └── cite_verify.py
  ├── src/
  │   ├── data.py
  │   ├── features.py
  │   ├── clustering.py
  │   ├── explainability.py
  │   └── viz.py
  ├── utils/                   # Utility functions
  │   ├── openai_client.py
  │   └── io_helpers.py
  ├── requirements.txt
  ├── README.md
  └── LICENSE
```

---

## 📊 Methodology

### Research Phase

1. **Multi-Agent Research**
   * Parallel execution of research tasks using OpenAI API
   * Synthesis of findings into design decisions
   * Citation verification and validation

2. **Design Decisions**
   * Feature definitions and formulas documented
   * Clustering approach and evaluation metrics established
   * Explainability framework defined
   * UX patterns and visualization guidelines set

### Implementation Phase

1. **Data Collection**
   * Source: Kaggle Premier League stats datasets (or FBref exports)
   * Focus: Outfield players, ≥600 minutes played

2. **Feature Engineering**
   * Per-90 scaling for rate stats
   * Composite indices (PI, CCI, DA, FE)
   * Winsorization at 5th and 95th percentiles

3. **Dimensionality Reduction**
   * PCA → retain 90% variance
   * UMAP → visualization layer only

4. **Clustering**
   * K-Means & Gaussian Mixture Models
   * Metrics: Silhouette Score (≥0.20), Davies–Bouldin (≤1.40), ARI (≥0.70)
   * Bootstrap sampling for stability assessment

5. **Explainability**
   * RandomForest surrogate model
   * SHAP values for global and local explanations
   * Permutation importance for validation

---

## 🎨 App Walkthrough

* **Home Page**: Project overview, role legend
* **Player Explorer**:

  * Search player by name
  * See cluster role + nearest neighbors
  * Radar chart: Player vs cluster average
  * Bar chart: Feature contributions for this player
* **Cluster Explorer**:

  * PCA/UMAP scatter with players color-coded by cluster
  * Cluster profile heatmaps (role averages across features)
  * Representative players listed per role
* **Methodology**: Data sources, pipeline steps, model evaluation

---

## 🛠️ Tech Stack

* **Research**: `openai`, `concurrent.futures`, `tenacity`
* **Data Processing**: `pandas`, `numpy`, `scikit-learn`
* **Machine Learning**: `scikit-learn`, `shap`, `umap-learn`
* **Visualization**: `plotly`, `seaborn`, `mplsoccer` (optional)
* **Web App**: `streamlit`
* **Deployment**: Streamlit Community Cloud
* **Versioning**: GitHub

---

## 🚀 Deployment

### Research Pipeline

Run the multi-agent research pipeline:

```bash
# 1. Execute research tasks in parallel
python scripts/run_subagents.py --plan planning/research-results/plan.json --model gpt-4o

# 2. Synthesize research findings
python scripts/synthesize.py --model gpt-4o

# 3. Verify citations (optional)
python scripts/cite_verify.py --model gpt-4o
```

### Streamlit App

Run the app locally:

```bash
streamlit run app/Home.py
```


## 📈 Future Improvements

* Add **season-over-season role drift** (track player role evolution)
* Integrate **team context features** (e.g., possession %, PPDA)
* Experiment with **deep learning embeddings** (autoencoders for representation learning)

---

⚽ **Author**: Mouhamed Mbengue
