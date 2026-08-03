# MediGenie Phases: Implementation Plan (2, 3, 5)

This document outlines the short-term implementation plan and runnable commands for:
- Phase 2: Train & integrate disease models
- Phase 3: Improve accuracy (tuning & validation)
- Phase 5: Explainability (SHAP / coefficients)

Goals
-----
- Phase 2: Provide reproducible training pipeline runs, model packaging, and a way to register models under `ml/models/<model_name>` so `PredictionService` can load them.
- Phase 3: Add evaluation commands for common metrics and a simple configuration for hyperparameter sweeps.
- Phase 5: Provide a helper for computing SHAP explanations (if `shap` installed) and fallbacks to model coefficients/importances.

Quick commands
--------------
Run training (example for `heart_disease` model):

```bash
cd backend
python -m ml.training.trainer --model heart_disease
```

Evaluate a trained model (example):

```bash
cd backend
python -m ml.training.evaluator --model heart_disease --data datasets/processed/heart_disease/test.csv
```

Compute explainability for a single JSON input (requires `shap`):

```bash
cd backend
python scripts/run_model_tasks.py explain --model heart_disease --input '{"age":45, "bmi":28, "glucose":120, "systolic_bp":130, "cholesterol":200}'
```

Notes
-----
- The repository already contains training and preprocessing modules under `ml/`. The helper script `scripts/run_model_tasks.py` wraps calls and provides dry-run mode.
- For large sweeps, use the training scripts' CLI and a scheduler/cluster.

Next steps (recommended immediate work)
-------------------------------------
1. Run the training command for the target disease model(s) and package outputs under `ml/models/<model_name>`.
2. Run evaluation against held-out test data and collect metrics (AUC, precision/recall, calibration).
3. Use `scripts/run_model_tasks.py explain` to reproduce SHAP attributions for sample inputs and integrate top factors into `PredictionService` outputs.
