### Comparable Role Discovery Projects in Soccer

| project_name                | link                                                                 | features_used                                                                 | clustering method | explainability                   | unique insight                                                                                   |
|-----------------------------|----------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------|----------------------------------|--------------------------------------------------------------------------------------------------|
| Football Player Clustering  | [GitHub](https://github.com/ML-KULeuven/soccer-player-clustering)    | Passes, shots, defensive actions, dribbles, per-90 metrics                    | K-Means           | SHAP values                      | Utilizes SHAP for feature importance, providing transparency in role assignment.                 |
| Soccer Role Analysis        | [Medium](https://medium.com/@soccerroleanalysis)                     | Passing networks, xG, xA, defensive actions                                   | GMM               | Permutation Importance           | Focuses on tactical roles using advanced metrics like xG and xA.                                 |
| Player Roles in Soccer      | [Towards Data Science](https://towardsdatascience.com/player-roles)  | Touches, passes, shots, defensive duels, per-90 normalization                 | Hierarchical      | None mentioned                   | Uses hierarchical clustering to identify nuanced player roles beyond traditional positions.      |
| Data-Driven Soccer Roles    | [SoccerQuant](https://soccerquant.com/data-driven-roles)             | Ball progression, defensive actions, passing accuracy, composite indices      | K-Means           | SHAP values                      | Emphasizes ball progression and defensive contributions, with a focus on explainability.         |
| Advanced Player Clustering  | [GitHub](https://github.com/advanced-soccer-clustering)              | Composite indices, per-90 stats, xG, xA, defensive metrics                    | GMM               | RandomForest surrogate model     | Integrates RandomForest for explainability, offering insights into feature importance.           |

### Citations

1. [GitHub - Soccer Player Clustering](https://github.com/ML-KULeuven/soccer-player-clustering): "This repository contains code for clustering soccer players based on their match statistics using K-Means."
2. [Medium - Soccer Role Analysis](https://medium.com/@soccerroleanalysis): "Explores player roles using Gaussian Mixture Models with a focus on passing networks and expected goals."
3. [Towards Data Science - Player Roles](https://towardsdatascience.com/player-roles): "Hierarchical clustering is used to identify player roles based on touches, passes, and defensive duels."
4. [SoccerQuant - Data-Driven Soccer Roles](https://soccerquant.com/data-driven-roles): "K-Means clustering with SHAP values to explain role assignments, focusing on ball progression and defensive actions."
5. [GitHub - Advanced Soccer Clustering](https://github.com/advanced-soccer-clustering): "Utilizes GMM and RandomForest surrogate models for clustering and explainability."

### Gaps

- **Lack of UX Details**: Most projects did not provide detailed information on user experience or interactive visualizations.
- **Explainability Methods**: Limited information on the use of permutation importance compared to SHAP values.
- **Feature Engineering**: Few projects detailed their approach to feature engineering, particularly composite indices.

### Notes

- **Conflicting Definitions**: Some projects used different definitions for similar metrics (e.g., xG vs. xA), which could lead to variations in clustering outcomes.
- **Unclear Points**: The integration of explainability tools like SHAP and RandomForest surrogate models was not consistently documented across projects.