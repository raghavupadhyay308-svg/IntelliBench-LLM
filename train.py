"""
Train two ML models:
1. RandomForestRegressor  → predict tokens_per_sec
2. RandomForestClassifier → predict quality tier (0-4)

Features: ram_gb, vram_gb, cpu_cores, cpu_freq_mhz, has_cuda,
          model_size_gb, model_min_ram_gb, model_min_vram_gb, requires_gpu
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error, r2_score,
    classification_report, accuracy_score
)
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "ram_gb", "vram_gb", "cpu_cores", "cpu_freq_mhz", "has_cuda",
    "model_size_gb", "model_min_ram_gb", "model_min_vram_gb", "requires_gpu"
]

TIER_NAMES = {0: "Won't Run", 1: "Slow", 2: "Okay", 3: "Good", 4: "Great"}

DATA_PATH   = os.path.join(os.path.dirname(__file__), "dataset.csv")
MODELS_DIR  = os.path.join(os.path.dirname(__file__), "models")


def train():
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    print(f"Dataset: {len(df)} samples, {df['quality_tier'].nunique()} tiers\n")

    X = df[FEATURES].values
    y_reg = df["tokens_per_sec"].values
    y_cls = df["quality_tier"].values

    X_train, X_test, yr_train, yr_test, yc_train, yc_test = train_test_split(
        X, y_reg, y_cls, test_size=0.2, random_state=42, stratify=y_cls
    )

    print("=" * 50)
    print("Training Regressor (tokens/sec prediction)...")
    print("=" * 50)

    regressor = RandomForestRegressor(
        n_estimators=200,
        max_depth=18,
        min_samples_leaf=2,
        max_features="sqrt",
        n_jobs=-1,
        random_state=42,
    )
    regressor.fit(X_train, yr_train)

    yr_pred = regressor.predict(X_test)
    yr_pred = np.clip(yr_pred, 0, None)

    mae = mean_absolute_error(yr_test, yr_pred)
    r2  = r2_score(yr_test, yr_pred)
    print(f"  MAE:  {mae:.2f} tokens/sec")
    print(f"  R²:   {r2:.4f}")

    # Feature importance
    importances = regressor.feature_importances_
    fi = sorted(zip(FEATURES, importances), key=lambda x: -x[1])
    print("\n  Top feature importances (regression):")
    for feat, imp in fi:
        bar = "█" * int(imp * 40)
        print(f"    {feat:<22} {imp:.3f}  {bar}")

    print("\n" + "=" * 50)
    print("Training Classifier (quality tier prediction)...")
    print("=" * 50)

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=18,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    classifier.fit(X_train, yc_train)

    yc_pred = classifier.predict(X_test)
    acc = accuracy_score(yc_test, yc_pred)
    print(f"  Accuracy: {acc:.4f} ({acc*100:.1f}%)\n")
    print("  Per-class report:")
    tier_labels = [TIER_NAMES[i] for i in sorted(TIER_NAMES.keys())]
    print(classification_report(yc_test, yc_pred,
                                target_names=tier_labels, zero_division=0))

    fi2 = sorted(zip(FEATURES, classifier.feature_importances_), key=lambda x: -x[1])
    print("  Top feature importances (classification):")
    for feat, imp in fi2:
        bar = "█" * int(imp * 40)
        print(f"    {feat:<22} {imp:.3f}  {bar}")

    # Save models
    reg_path = os.path.join(MODELS_DIR, "regressor.pkl")
    cls_path = os.path.join(MODELS_DIR, "classifier.pkl")
    meta_path = os.path.join(MODELS_DIR, "meta.pkl")

    joblib.dump(regressor, reg_path)
    joblib.dump(classifier, cls_path)
    joblib.dump({
        "features":   FEATURES,
        "tier_names": TIER_NAMES,
        "reg_mae":    round(mae, 2),
        "reg_r2":     round(r2, 4),
        "cls_acc":    round(acc, 4),
    }, meta_path)

    print(f"\n✅ Saved:")
    print(f"   {reg_path}")
    print(f"   {cls_path}")
    print(f"   {meta_path}")
    return regressor, classifier


if __name__ == "__main__":
    train()
