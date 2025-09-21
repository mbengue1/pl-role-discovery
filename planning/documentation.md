# Premier League Player Role Discovery — **Project Documentation**

**Author:** Mouhamed Mbengue

**Project Type:** Unsupervised ML + Interactive Analytics Web App

**Primary Users:** Football analysts, coaches/scouts, data-curious fans, recruiters/hiring managers (evaluation artifact)

**Status:** Planning complete → build plan defined → deployment targets specified

---

## 0) Executive Summary

This project discovers **data-driven player roles** in the English Premier League using **unsupervised learning** on rich, per-90-normalized on-ball and off-ball statistics. The final deliverable is a **deployed, interactive Streamlit application** that lets users:

* Search a player and see their **inferred role** (+ confidence),
* Explore **nearest-neighbor** similar players,
* Compare a player to their role archetype via  **radar charts** ,
* Visualize the league-wide player landscape with  **PCA/UMAP scatter** ,
* Understand **why** a player is assigned to a role via  **SHAP/permutation importance** .

This documentation formalizes the  **objectives, scope, data strategy, modeling decisions, explainability framework, system architecture, UX flows, evaluation criteria, non-functional requirements, testing/observability, risks, and roadmap** .

---

## 1) Goals, Scope & Success Criteria

### 1.1 Objectives

* **Discover roles** from data rather than relying on coarse positions (DEF/MID/FWD).
* **Make insights interpretable** (SHAP/permutation importance + role profiles).
* **Deliver an interactive tool** suitable for public demonstration, resume/portfolio, and technical interviews.
* **Engineer for maintainability** (clean module boundaries, reproducible pipeline, CI).

### 1.2 Non-Goals (MVP)

* Predicting **future** performance or market value.
* Modeling **in-match tactical dynamics** (e.g., event sequences).
* Proprietary data ingestion or paid data contracts.

### 1.3 Quantitative Success Criteria

* **Coverage:** ≥ 90% of outfield players with ≥ 600 minutes from target season.
* **Stability:** Cluster reproducibility under bootstrap resampling (Adjusted Rand Index ≥ 0.70 across seeds).
* **Quality:** Silhouette ≥ 0.20 and Davies–Bouldin ≤ 1.40 for chosen K (guidelines for real player data; interpretability prioritized).
* **Latency (UX):** Page-level interactions render key visuals in ≤ 3 seconds on Streamlit Cloud standard hardware.
* **Explainability UX:** Per-player SHAP panel renders in ≤ 2.5 seconds; top-5 contributing features displayed coherently.

---

## 2) User Personas & Core Use Cases

### 2.1 Personas

* **Analyst/Coach:** Needs quick, explainable role archetypes; compares squad profiles and scouting targets.
* **Data-Curious Fan:** Wants to see “who plays like whom” and  **why** .
* **Recruiter/Hiring Manager:** Evaluates full-stack ML capability, reproducible science, and clean UI/UX.

### 2.2 Key Use Cases

1. **Player Lookup:** Identify role, similar players, differentiating stats.
2. **Cluster Exploration:** Understand each role’s statistical profile and representative players.
3. **Role Comparison:** Compare role archetypes side-by-side (e.g., “Pressing Forward” vs “Clinical Striker”).
4. **Explainability:** For any player, see which features drove the role assignment.

---

## 3) Data Strategy

### 3.1 Sources & Scope

* **Primary:** FBref (public season tables; CSV export) or Kaggle mirrors of EPL stats.
* **Season (MVP):** Most recent complete season with robust minutes (e.g.,  **2024/25** ).
* **Entities:** **Outfield players** only; exclude GKs for MVP (goalkeeper feature distributions are disjoint).

### 3.2 Inclusion Filters

* **Minutes ≥ 600** to reduce noise from tiny samples.
* For players in multiple teams (transfers), aggregate season totals before per-90 normalization.

### 3.3 Data Compliance & Attribution

* Use public exports for personal/research use.
* **Do not rehost** raw source data in the repository; link instructions for users to export/locally place CSVs.
* Provide a **Data Sources & Attribution** section in docs/app.

### 3.4 Raw → Cleaned Schema (Representative)

Minimal set (final set may expand based on availability):

| Category               | Features (examples)                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| Identification         | player_name, team, position_label (raw), minutes                                           |
| Possession/Progression | progressive_passes, progressive_carries, passes_into_final_third, carries_into_final_third |
| Creative               | key_passes, shot_creating_actions (SCA), expected_assists (xA)                             |
| Shooting               | shots, goals, non_pen_xG, shots_on_target                                                  |
| Defensive              | tackles (def 3rd/mid 3rd/att 3rd), interceptions, blocks, pressures, successful_pressures  |
| Carry/Take-on          | carries, carry_progression, take_ons_att, take_ons_succ                                    |
| Aerial/Physical        | aerials_won, aerials_lost                                                                  |

---

## 4) Feature Engineering

### 4.1 Normalization

* **Per-90 rates:**

  feat_per90=raw_countminutes×90\text{feat\_per90} = \frac{\text{raw\_count}}{\text{minutes}} \times 90
* **Share/efficiency** features (where applicable), e.g., finishing efficiency, pressure success rate, take-on success rate.

### 4.2 Composite Indices (MVP definitions)

* **Progression Index (PI):**

  PI=progressive_passes_per90+progressive_carries_per90PI = \text{progressive\_passes\_per90} + \text{progressive\_carries\_per90}
* **Chance Creation Index (CCI):**

  CCI=key_passes_per90+SCA_per90CCI = \text{key\_passes\_per90} + \text{SCA\_per90}
* **Defensive Activity (DA):**

  DA=tackles_per90+interceptions_per90+blocks_per90DA = \text{tackles\_per90} + \text{interceptions\_per90} + \text{blocks\_per90}
* **Finishing Efficiency (FE):** robust ratio with clipping to reduce volatility:

  FE=clip(goalsmax⁡(shots,ϵ),[p5,p95])FE = \text{clip}\left(\frac{\text{goals}}{\max(\text{shots},\epsilon)}, [p_5, p_{95}]\right)

> **Notes:**
>
> • Clip/winsorize extreme ratios to the 5th–95th percentile.
>
> • Guard against division by zero with small ϵ\epsilon.

### 4.3 Scaling & Outliers

* **StandardScaler** for model inputs (zero mean, unit variance).
* Winsorization (5–95) on heavy-tailed features (e.g., FE, aerials).

### 4.4 Feature Selection

* Drop features with  **near-zero variance** , and optionally reduce **highly collinear** pairs (|ρ|>0.95) to stabilize clustering.

---

## 5) Modeling Strategy

### 5.1 Dimensionality Reduction

* **PCA** to capture **85–90%** variance (≈ 10–20 components depending on feature count).
* **UMAP (2D)** for visualization only; **not** fed to clustering (prevents manifold-driven artifacts).

### 5.2 Clustering Algorithms

* **Primary:** K-Means (fast, stable centroids).
* **Secondary:** Gaussian Mixture Models (elliptical clusters, soft probabilities).

**Model selection grid:**

* K∈{6,7,8,…,12}K \in \{6,7,8,\dots,12\} for each algorithm.
* Evaluate:  **Silhouette** ,  **Davies–Bouldin** ,  **Calinski–Harabasz** .
* **Interpretability gate:** prefer K that yields **distinct, football-intuitive prototypes** after center inspection.

### 5.3 Cluster Naming

* Inspect **cluster centers** and **top-N players** by proximity to center.
* readable names, e.g.:
  * Progressive Playmaker
  * Box-to-Box Midfielder
  * Clinical Striker
  * Pressing Forward
  * Deep-Lying Distributor
  * Aggressive Ball-Winner
* Persist a **cluster legend** (name ↔ color ↔ id).

### 5.4 Reproducibility

* Fixed random seeds for PCA, K-Means/GMM.
* Save artifacts: `pca.pkl`, `kmeans.pkl` (or `gmm.pkl`), `feature_list.json`, `scaler.pkl`.

---

## 6) Explainability Framework

### 6.1 Classifier Surrogate

Train **RandomForestClassifier** on the (scaled, PCA-reduced or raw scaled) feature matrix to predict  **cluster labels** . The classifier serves as a **local boundary approximator** for SHAP.

### 6.2 SHAP

* **TreeExplainer** for RF:
  * **Global summary:** top features distinguishing roles overall.
  * **Local (per-player):** bar plot of top 5 contributors to the assigned role.
* **Permutation Importance** as **sanity check** for global feature influence.

### 6.3 UX Integration

* **Player page:** SHAP bars clarify “why this role.”
* **Cluster page:** global SHAP summary and  **cluster profile heatmaps** .

---

## 7) System Architecture

```
File : prem-data-artcheture-flow documentation

   
```

### 7.1 Repository Layout 

```
premier-league-role-discovery/
  app/
    Home.py
    pages/
      1_Player Explorer.py
      2_Cluster Explorer.py
      3_Methodology & FAQ.py
  data/
    raw/            # not tracked, .gitignored (instructions to obtain)
    processed/
      player_stats_cleaned.csv
      player_feature_matrix.csv
      player_clustered.csv
  models/
    scaler.pkl
    pca.pkl
    kmeans.pkl
    role_classifier.pkl
  notebooks/
    01_data_cleaning.ipynb
    02_feature_engineering.ipynb
    03_model_selection.ipynb
    04_explainability.ipynb
  src/
    data.py
    features.py
    clustering.py
    explainability.py
    viz.py
    utils.py
  tests/
    test_features.py
    test_clustering.py
    test_explainability.py
  requirements.txt
  LICENSE
  README.md           # high-level landing page (not this document)
  .gitignore
```

---

## 8) Application Design (UX Flows)

### 8.1 Navigation

Sidebar:

* 🏠 **Home**
* 🔍 **Player Explorer**
* 📊 **Cluster Explorer**
* 📚 **Methodology & FAQ**

### 8.2 Home

* 1–2 paragraph overview
* **Role legend** (consistent colors)
* Small pipeline schematic

### 8.3 Player Explorer (Primary workflow)

Inputs:

* Player search (autocomplete; dropdown fallback)

Panels:

* **Role Assignment** : Role name + confidence (from cluster distance or GMM posterior)
* **Radar Chart** : Player vs role average
* **Similar Players** : Top-k by cosine similarity (show team)
* **Explainability** : SHAP bar (top 5 contributors)

### 8.4 Cluster Explorer

* **UMAP/PCA scatter** (hover = player, team, role)
* **Cluster selection** → profile heatmap + representative players
* **Role comparison** : two-role side-by-side radar/bars

### 8.5 Methodology & FAQ

* Data source, filters, features
* PCA/Clustering choices and metrics (tables/figures)
* Explainability approach and limitations
* FAQ (e.g., “Why isn’t player X in role Y?”)

---

## 9) Non-Functional Requirements

* **Performance:** Responsive visuals ≤ 3 seconds typical; cached data loaders; pre-computations saved as artifacts.
* **Reliability:** Deterministic builds via pinned `requirements.txt`; saved seeds.
* **Security & Privacy:** No PII; public sports data only; no secrets required.
* **Portability:** Works locally (`streamlit run app/Home.py`) and on Streamlit Cloud; artifacts stored in repo.
* **Accessibility (best effort):** Clear color palette, legend, alternative text for key figures.

---

## 10) Evaluation Protocol

### 10.1 Quantitative (Model)

* Report Silhouette, Davies–Bouldin, Calinski–Harabasz across K∈[6,12]K \in [6,12].
* **Stability:** Bootstrap sample (e.g., 200 resamples), compute ARI across solutions.
* **Sensitivity:** Remove top-N high-variance features to test role robustness (labels should mostly persist).

### 10.2 Qualitative (Domain)

* Face-validity checks:
  * Do “Clinical Striker” clusters contain archetypal finishers?
  * Do “Progressive Playmakers” show high progression and creation?
* Edge cases documented (hybrid profiles, small-sample players).

### 10.3 UX

* Manual user tests (3–5 users): findability, clarity, perceived latency.

---

## 11) Testing Strategy

* **Unit Tests (pytest):**
  * `features.py`: per-90, composites, clipping behavior.
  * `clustering.py`: shapes, deterministic seeding, label count matches K.
  * `explainability.py`: SHAP value shapes; non-empty top-k attributions.
* **Integration Tests:**
  * End-to-end pipeline on a tiny fixture dataset (5–10 players) to validate artifact generation.
* **App Smoke Tests:**
  * Ensure pages render with fixture artifacts and minimal data.
* **Static Analysis:**
  * `ruff`/`flake8` for style; `black` for formatting (optional).

---

## 12) Observability & Analytics

* **Structured logging** (Python `logging`) for pipeline steps.
* Optional **usage analytics** (lightweight): counts of player searches, cluster views (file-based counters or SQLite). Disabled by default; toggle in config.

---

## 13) Deployment

* **Primary:** Streamlit Community Cloud.
* **Artifacts in repo** to remove cold-start model training.
* **Alternatives (future):** Docker + Render/Fly.io; FastAPI backend if moving heavy compute off the UI.

**Release checklist:**

* `requirements.txt` pins
* Sample screenshots in README
* Data acquisition instructions (no raw redistribution)
* Validated artifacts in `models/` + `data/processed/`

---

## 14) Risks & Mitigations

| Risk                   | Impact           | Mitigation                                                        |
| ---------------------- | ---------------- | ----------------------------------------------------------------- |
| Source schema drift    | Broken loaders   | Centralize column mapping in `data.py`+ schema asserts          |
| Overfitting composites | Misleading roles | Keep composites simple; document formulas; sensitivity tests      |
| Unstable clustering    | Confusing roles  | Bootstrap stability checks; prefer Ks with robust ARI             |
| UX latency             | Drop-offs        | Precompute artifacts; cache; limit SHAP to top-k features         |
| Licensing concerns     | Repo takedown    | Don’t rehost raw data; provide export instructions + attribution |
| Small sample players   | Role noise       | Minutes ≥ 600 filter; show warning badges for low minutes        |

---

## 15) Roadmap

### 15.1 MVP (this build)

* Single season (2022/23)
* Outfield players
* Per-90 + composites
* PCA + K-Means (primary), GMM (secondary)
* SHAP + permutation importance
* Streamlit app with 4 pages
* Deployment to Streamlit Cloud
* Unit/integration tests, seeds pinned

### 15.2 Near-Term Enhancements

* **Role Drift:** Multi-season tracking of player embeddings/roles over time.
* **Team Context:** Possession %, PPDA, pace to situate roles by system style.
* **Alternative DR:** Autoencoder embeddings (compare to PCA).
* **Clustering Variants:** HDBSCAN/DBSCAN for density-based roles.
* **Compare Players:** Side-by-side player comparison page.

### 15.3 Long-Term Ideas

* **Temporal models:** Rolling windows, in-season trend shifts.
* **Scenario analysis:** “Who could replace Player X in Role Y?”
* **Export pack:** PDF role reports per player.

---

## 16) Reproducibility & Governance

* **Versioning:** Tag releases; artifact file names include version + season.
* **Seeds:** Fixed seeds in PCA/K-Means and surrogate RF.
* **Environment:** `requirements.txt` pinned; optional `uv`/`pip-tools` lock.
* **Data Lineage:** Document exact CSVs and retrieval dates.
* **(Optional) DVC:** Track processed data & artifacts without storing large raw files.

---

## 18) Phase 3 Results Summary

### Clustering Performance

- **Final Algorithm**: K-Means with k=3
- **Silhouette Score**: 0.2455 (meets threshold of ≥0.20)
- **Stability (ARI)**: 0.9143 (exceeds threshold of ≥0.70)
- **Davies-Bouldin**: 1.5658 (slightly above threshold of ≤1.40)
- **Bootstrap Stability**: Excellent consistency across 50 bootstrap samples

### Discovered Player Roles

1. **Cluster 0 - "The Enforcers"**: Defensive specialists with high tackles, interceptions, and blocks
2. **Cluster 1 - "The Creators"**: Attacking playmakers with high key passes, assists, and chance creation
3. **Cluster 2 - "The Finishers"**: Goal threats with high shots on target and clinical finishing

### Key Achievements

- Successfully reduced 236 features to 3 meaningful principal components (90% variance retained)
- Identified 3 distinct, interpretable player archetypes aligned with football intuition
- Achieved high clustering stability, indicating robust role definitions
- Generated comprehensive outputs: PCA projections, cluster assignments, and UMAP visualizations

### Output Files Generated

- `player_pca_projection.csv`: PCA-transformed data
- `player_clusters.csv`: Cluster assignments with player metadata
- `player_umap_2d.csv`: 2D UMAP coordinates for visualization

---

## 19) Build Plan (Actionable Checklists)

### Module 1 — Data Collection & Cleaning

* [X] Export season tables (standard, shooting, passing, defending, possession, carrying/take-ons).
* [X] Harmonize column names; join on player & season; aggregate multi-team rows.
* [X] Filter out GKs; enforce minutes ≥ 600.
* [X] Save `player_stats_cleaned.csv`; write loader with schema asserts.

### Module 2 — Feature Engineering ✅

* [X] Compute per-90s; composites (PI, CCI, DA, FE)
* [X] Winsorize heavy tails; StandardScaler fit/save
* [X] Build `player_stats_engineered.csv` (563 players × 266 features)

### Module 3 — Modeling ✅

* [X] Fit PCA to target variance (90%); save artifacts
* [X] Grid search K for K-Means and GMM; evaluate metrics
* [X] Choose K=3 by metrics + interpretability; name clusters
* [X] Bootstrap stability assessment (ARI = 0.9143)
* [X] Generate UMAP visualization
* [X] Save all artifacts: `pca.pkl`, `kmeans.pkl`, labeled dataframes

### Module 4 — Explainability

* [ ] Train RF surrogate on (scaled ± PCA) to predict clusters; save `role_classifier.pkl`.
* [ ] Generate global SHAP summary; implement per-player SHAP top-k retrieval.
* [ ] Compute permutation importances; export CSV.

### Module 5 — Streamlit App

* [ ] Home + legend + pipeline schematic.
* [ ] Player Explorer: search, role, neighbors, radar, SHAP.
* [ ] Cluster Explorer: UMAP/PCA scatter; cluster profiles; role compare.
* [ ] Methodology & FAQ page.
* [ ] Centralize colors/legend; cache data/artifacts.

### Module 6 — Deployment & Polish

* [ ] Pin requirements; validate cold start; push to Streamlit Cloud.
* [ ] Add screenshots/gifs; final README; LICENSE; tests passing.
* [ ] Optional: lightweight usage analytics toggle.

---

## 20) Glossary

* **Per-90:** Normalization to 90 minutes to compare players with different minutes.
* **UMAP:** Nonlinear dimensionality reduction for visualization.
* **Silhouette / DB / CH:** Cluster quality metrics; complementary views of separation/compactness.
* **SHAP:** Shapley-value-based attribution for feature influence (global/local).
* **PPDA:** Passes allowed Per Defensive Action (team pressing proxy).

---

## 21) Appendices

### A) Feature List (Representative; will adapt to available columns)

* **Progression:** progressive_passes_per90, progressive_carries_per90, passes_into_final_third_per90, carries_into_final_third_per90
* **Creation:** key_passes_per90, SCA_per90, xA_per90
* **Shooting:** shots_per90, goals_per90, non_pen_xG_per90, shots_on_target_per90, finishing_efficiency
* **Defensive:** tackles_def3rd_per90, tackles_mid3rd_per90, tackles_att3rd_per90, interceptions_per90, blocks_per90, pressures_per90, successful_pressures_rate
* **Carry/Take-ons:** carries_per90, carry_progression_per90, take_ons_att_per90, take_ons_succ_rate
* **Aerial:** aerials_won_per90, aerials_win_rate

### B) Model Selection Protocol

1. Standardize & PCA to 85–90% variance.
2. For each K in 6–12 and algorithm in {K-Means, GMM}, compute Silhouette/DB/CH.
3. Rank by metrics; shortlist top 2–3 K.
4. Inspect centers & exemplars; run stability (bootstrap ARI).
5. Choose final K by  **interpretability + stability** ; name roles; lock legend.

### C) UX Performance Todo

* Cache loaders (`st.cache_data`) and artifacts (`st.cache_resource`).
* Precompute per-player SHAP top-k; store small JSON to avoid recompute.
