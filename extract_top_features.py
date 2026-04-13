import json
import xgboost as xgb
import numpy as np
import shap
from pathlib import Path
from collimator.features import FeatureSpec

# Load model and spec
model = xgb.XGBClassifier()
model.load_model("out/model.json")
with open("out/feature_spec.json") as f:
    spec_dict = json.load(f)
    # FeatureSpec doesn't have a from_dict, but we only need the list of names
    feature_names = spec_dict["feature_names"]

# Extract weights as a proxy for importance since SHAP is too slow for 150k features here
importance_scores = model.get_booster().get_score(importance_type="weight")
# Map scores back to feature names (XGBoost names them f0, f1, etc.)
named_importance = []
for fid, score in importance_scores.items():
    idx = int(fid[1:])
    if idx < len(feature_names):
        named_importance.append((feature_names[idx], score))

# Sort and take top 5000
named_importance.sort(key=lambda x: x[1], reverse=True)
top_5000 = [name for name, score in named_importance[:5000]]

with open("out/top_5000_features.json", "w") as f:
    json.dump(top_5000, f, indent=2)
print(f"Saved {len(top_5000)} features to out/top_5000_features.json")
