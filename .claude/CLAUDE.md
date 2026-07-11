# Heart Disease MLOps Project

## Environment Setup

**Status**: ✓ Configured for Python 3.13

### Activation
```bash
source .venv-py313/bin/activate
```

### Installed Packages
- **Data Science**: pandas 2.3.3, numpy 2.5.1, scikit-learn 1.9.0, scipy 1.18.0
- **Visualization**: matplotlib 3.11.0, seaborn 0.13.2
- **ML Tracking**: mlflow 3.14.0
- **API**: fastapi 0.139.0, uvicorn 0.51.0, pydantic 2.13.4
- **Notebooks**: jupyter, jupyterlab, ipykernel
- **Testing**: pytest 9.1.1, flake8 7.3.0, httpx

### Notes
- Python 3.14 and 3.13 have better wheel support than 3.14 for ML packages
- Original requirements.txt had strict pinning that caused dependency conflicts (e.g., mlflow 2.14.3 required numpy<2 while newer packages need numpy 2.x)
- Updated to flexible version constraints to allow pip to resolve compatible versions automatically
