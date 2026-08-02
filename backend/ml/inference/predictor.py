"""
predictor.py

Production inference engine.

Responsibilities
----------------
✓ Load packaged model
✓ Load preprocessing pipeline
✓ Validate patient input
✓ Preprocess features
✓ Predict disease
✓ Return probabilities
"""

from __future__ import annotations

import json
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)
# ==============================================================================
# Exceptions
# ==============================================================================

class PredictionError(Exception):
    """Base prediction exception."""


class ModelNotLoadedError(PredictionError):
    """Model has not been loaded."""


class InvalidInputError(PredictionError):
    """Invalid patient data."""
    # ==============================================================================
# Configuration
# ==============================================================================

@dataclass(slots=True)
class PredictorConfig:

    model_directory: Path
    # ==============================================================================
# Prediction Result
# ==============================================================================

@dataclass(slots=True)
class PredictionResult:

    prediction: int

    probability: float

    confidence: float

    class_probabilities: dict[str, float]
    # ==============================================================================
# Predictor
# ==============================================================================

class Predictor:
    """
    Production inference engine.
    """

    def __init__(
        self,
        config: PredictorConfig,
    ) -> None:

        self.config = config

        self.model = None

        self.pipeline = None

        self.schema = None

        self.feature_names = None
            # ==========================================================================
    # Load Model
    # ==========================================================================

    def load_model(self):

        model_path = (
            self.config.model_directory /
            "model.joblib"
        )

        if not model_path.exists():

            raise ModelNotLoadedError(
                model_path
            )

        self.model = joblib.load(
            model_path
        )

        logger.info(
            "Model loaded."
        )

    # ==========================================================================
    # Load Preprocessor
    # ==========================================================================

    def load_pipeline(self):

        pipeline_path = (
            self.config.model_directory /
            "preprocessor.joblib"
        )

        if not pipeline_path.exists():

            raise ModelNotLoadedError(
                pipeline_path
            )

        self.pipeline = joblib.load(
            pipeline_path
        )

        logger.info(
            "Pipeline loaded."
        )

    # ==========================================================================
    # Load Schema
    # ==========================================================================

    def load_schema(self):

        schema_path = (
            self.config.model_directory /
            "schema.json"
        )

        with open(
            schema_path,
            "r",
            encoding="utf-8",
        ) as file:

            self.schema = json.load(file)

        logger.info(
            "Schema loaded."
        )

    # ==========================================================================
    # Load Feature Names
    # ==========================================================================

    def load_feature_names(self):

        feature_path = (
            self.config.model_directory /
            "feature_names.json"
        )

        with open(
            feature_path,
            "r",
            encoding="utf-8",
        ) as file:

            self.feature_names = json.load(
                file
            )

    # ==========================================================================
    # Initialize
    # ==========================================================================

    def initialize(self):

        self.load_model()

        self.load_pipeline()

        self.load_schema()

        self.load_feature_names()

        logger.info(
            "Inference engine initialized."
        )
            # ==========================================================================
    # Validate Input
    # ==========================================================================

    def validate_input(
        self,
        patient_data: dict[str, Any],
    ) -> None:
        """
        Validate patient input against schema.
        """

        if self.schema is None:

            raise ModelNotLoadedError(
                "Schema not loaded."
            )

        required = self.schema.get(
            "required_columns",
            []
        )

        missing = [

            column

            for column in required

            if column != self.schema.get("target_column")
            and column not in patient_data

        ]

        if missing:

            raise InvalidInputError(

                "Missing required fields:\n"

                + "\n".join(missing)

            )

        logger.info(
            "Patient input validated."
        )

    # ==========================================================================
    # Create DataFrame
    # ==========================================================================

    def create_dataframe(
        self,
        patient_data: dict[str, Any],
    ) -> pd.DataFrame:
        """
        Convert dictionary to dataframe.
        """

        dataframe = pd.DataFrame(
            [patient_data]
        )

        logger.info(
            "Input dataframe created."
        )

        return dataframe

    # ==========================================================================
    # Preprocess
    # ==========================================================================

    def preprocess(
        self,
        dataframe: pd.DataFrame,
    ):
        """
        Apply fitted preprocessing pipeline.
        """

        if self.pipeline is None:

            raise ModelNotLoadedError(
                "Preprocessing pipeline not loaded."
            )

        transformed = self.pipeline.transform(
            dataframe
        )

        logger.info(
            "Input transformed."
        )

        return transformed

    # ==========================================================================
    # Predict
    # ==========================================================================

    def predict(
        self,
        patient_data: dict[str, Any],
    ) -> PredictionResult:
        """
        Predict disease.
        """

        if self.model is None:

            raise ModelNotLoadedError(
                "Model not loaded."
            )

        self.validate_input(
            patient_data
        )

        dataframe = self.create_dataframe(
            patient_data
        )

        transformed = self.preprocess(
            dataframe
        )

        prediction = int(

            self.model.predict(
                transformed
            )[0]

        )

        probabilities = (

            self.model.predict_proba(
                transformed
            )[0]

        )

        confidence = float(
            np.max(probabilities)
        )

        probability = float(
            probabilities[prediction]
        )

        class_probabilities = {

            str(index): float(value)

            for index, value in enumerate(
                probabilities
            )

        }

        logger.info(
            "Prediction completed."
        )

        return PredictionResult(

            prediction=prediction,

            probability=probability,

            confidence=confidence,

            class_probabilities=class_probabilities,

        )
        # ==========================================================================
    # Predict JSON
    # ==========================================================================

    def predict_json(
        self,
        patient_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        JSON-ready prediction.
        """

        result = self.predict(
            patient_data
        )

        return {

            "prediction": result.prediction,

            "probability": result.probability,

            "confidence": result.confidence,

            "class_probabilities": (
                result.class_probabilities
            ),

        }
    # ==============================================================================
# Factory
# ==============================================================================

def load_predictor(
    model_directory: str | Path,
) -> Predictor:
    """
    Load predictor and initialize all artifacts.
    """

    predictor = Predictor(

        PredictorConfig(

            model_directory=Path(
                model_directory
            )

        )

    )

    predictor.initialize()

    return predictor