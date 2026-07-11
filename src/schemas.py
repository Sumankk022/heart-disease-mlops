"""Pydantic request/response schemas for the prediction API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PatientFeatures(BaseModel):
    """One patient record. Field descriptions follow the UCI dataset."""

    age: float = Field(..., ge=0, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(..., ge=0, le=4, description="Chest pain type")
    trestbps: float = Field(..., ge=0, description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., ge=0, description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results")
    thalach: float = Field(..., ge=0, description="Max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise-induced angina")
    oldpeak: float = Field(..., description="ST depression vs. rest")
    slope: int = Field(..., ge=0, le=3, description="Slope of peak exercise ST")
    ca: float = Field(..., ge=0, le=4, description="Major vessels colored (0-3)")
    thal: float = Field(..., description="Thalassemia (3=normal,6=fixed,7=reversible)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 63,
                "sex": 1,
                "cp": 1,
                "trestbps": 145,
                "chol": 233,
                "fbs": 1,
                "restecg": 2,
                "thalach": 150,
                "exang": 0,
                "oldpeak": 2.3,
                "slope": 3,
                "ca": 0,
                "thal": 6,
            }
        }
    }


class PredictionResponse(BaseModel):
    """Model output for a single patient."""

    prediction: int = Field(..., description="1 = heart disease predicted, 0 = not")
    label: str = Field(..., description="Human-readable label")
    confidence: float = Field(..., description="Probability of the predicted class")
