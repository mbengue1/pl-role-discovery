Perfect—let’s draft a **full README-style project document** that you can drop directly into your GitHub repo. This will not only explain what the project is but also show recruiters you take documentation and storytelling seriously. I’ll tailor the tone and depth to your **resume style and prior projects**.

---

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
  ├── src/
  │   ├── data.py
  │   ├── features.py
  │   ├── clustering.py
  │   ├── explainability.py
  │   └── viz.py
  ├── requirements.txt
  ├── README.md
  └── LICENSE
```

---

## 📊 Methodology

1. **Data Collection**

   * Source: Kaggle Premier League stats datasets (or FBref exports)
   * Focus: Outfield players, ≥600 minutes played

2. **Feature Engineering**

   * Per-90 scaling for rate stats
   * Composite metrics (progression, creation, defense, finishing)
   * Scaling & outlier handling

3. **Dimensionality Reduction**

   * PCA → retain 85–90% variance
   * UMAP → visualization layer

4. **Clustering**

   * K-Means & Gaussian Mixtures
   * Metrics: Silhouette Score, Davies–Bouldin, Calinski-Harabasz
   * Manual inspection for interpretability

5. **Explainability**

   * Train RandomForest classifier → predict cluster labels
   * SHAP/permutation importance → global + local explanations

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

* **Python**: `pandas`, `numpy`, `scikit-learn`, `shap`
* **Visualization**: `plotly`, `seaborn`, `mplsoccer` (optional)
* **Web App**: `streamlit`
* **Deployment**: Streamlit Community Cloud
* **Versioning**: GitHub

---

## 🚀 Deployment

Run locally:

```bash
git clone https://github.com/mbengue1/premier-league-role-discovery.git
cd premier-league-role-discovery
pip install -r requirements.txt
streamlit run app/Home.py
```




## 📈 Future Improvements

* Add **season-over-season role drift** (track player role evolution)
* Integrate **team context features** (e.g., possession %, PPDA)
* Experiment with **deep learning embeddings** (autoencoders for representation learning)

---

⚽ **Author**: Mouhamed Mbengue
