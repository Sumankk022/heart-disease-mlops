# Kubernetes Deployment Guide

This directory contains Kubernetes deployment manifests and Helm charts for the Heart Disease Prediction API.

## Directory Structure

```
k8s/
├── README.md                          # This file
├── deployment.yaml                    # Kubernetes deployment manifest
├── service.yaml                       # Kubernetes service manifest
├── ingress.yaml                       # Kubernetes ingress manifest (optional)
└── helm/
    └── heart-disease-api/
        ├── Chart.yaml                 # Helm chart metadata
        ├── values.yaml                # Default configuration values
        └── templates/
            ├── deployment.yaml        # Helm deployment template
            ├── service.yaml           # Helm service template
            ├── ingress.yaml           # Helm ingress template
            ├── serviceaccount.yaml    # Helm service account template
            ├── _helpers.tpl           # Helm helper templates
            └── NOTES.txt              # Post-install instructions
```

---

## Prerequisites

- **Docker image built:** `docker build -t heart-disease-api:latest .`
- **Kubernetes cluster running:**
  - Minikube (local testing)
  - Docker Desktop Kubernetes
  - GKE, EKS, AKS (cloud)
- **kubectl** configured to access the cluster
- **Helm** (v3+) installed (optional, for Helm deployment)

---

## Method 1: Direct Kubectl Deployment (Simple)

Apply Kubernetes manifests directly:

```bash
# Create namespace (optional)
kubectl create namespace mlops

# Apply manifests
kubectl apply -f k8s/deployment.yaml -n mlops
kubectl apply -f k8s/service.yaml -n mlops
kubectl apply -f k8s/ingress.yaml -n mlops  # optional

# Verify deployment
kubectl get pods -n mlops
kubectl get svc -n mlops
```

### Check Deployment Status

```bash
# View pods
kubectl get pods -n mlops
kubectl describe pod <pod-name> -n mlops

# View logs
kubectl logs -n mlops -l app=heart-disease-api -f

# Port forward for testing
kubectl port-forward -n mlops svc/heart-disease-api 8000:80

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

## Method 2: Helm Deployment (Recommended)

Helm simplifies configuration and updates.

### Install the Helm Chart

```bash
# Create namespace
kubectl create namespace mlops

# Install the chart
helm install heart-disease-api k8s/helm/heart-disease-api/ \
  --namespace mlops \
  --create-namespace

# Or with custom values
helm install heart-disease-api k8s/helm/heart-disease-api/ \
  --namespace mlops \
  -f k8s/helm/heart-disease-api/values.yaml
```

### Upgrade the Chart (after code changes)

```bash
# Rebuild Docker image
docker build -t heart-disease-api:v2 .

# Update Helm release
helm upgrade heart-disease-api k8s/helm/heart-disease-api/ \
  --namespace mlops \
  --set image.tag=v2
```

### Uninstall the Chart

```bash
helm uninstall heart-disease-api --namespace mlops
```

### View Helm Release Status

```bash
# List releases
helm list -n mlops

# Get deployment details
helm status heart-disease-api -n mlops

# Get values used
helm get values heart-disease-api -n mlops

# Dry-run to preview changes
helm upgrade heart-disease-api k8s/helm/heart-disease-api/ \
  --namespace mlops --dry-run --debug
```

---

## Configuration

### Via kubectl (edit deployment.yaml)

```yaml
# Modify k8s/deployment.yaml before applying
replicas: 2              # Number of replicas
resources.limits.cpu: 500m
resources.limits.memory: 512Mi
```

### Via Helm (values.yaml)

```bash
# Set values via command-line
helm install heart-disease-api k8s/helm/heart-disease-api/ \
  --set replicaCount=3 \
  --set image.tag=v1.1 \
  --set resources.limits.memory=1Gi

# Or create custom values file
cat > custom-values.yaml << EOF
replicaCount: 3
image:
  tag: v1.1
resources:
  limits:
    memory: 1Gi
EOF

helm install heart-disease-api k8s/helm/heart-disease-api/ \
  -f custom-values.yaml
```

---

## Testing the Deployment

### 1. Port Forward (Local Testing)

```bash
kubectl port-forward -n mlops svc/heart-disease-api 8000:80
```

Then access:
- **Health check:** `curl http://localhost:8000/health`
- **API docs:** http://localhost:8000/docs
- **Metrics:** `curl http://localhost:8000/metrics`

### 2. Make a Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
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
    "thal": 6
  }'
```

Expected response:
```json
{
  "prediction": 1,
  "label": "Heart disease",
  "confidence": 0.9438
}
```

### 3. View Logs

```bash
# Follow logs from all pods
kubectl logs -n mlops -l app=heart-disease-api -f

# Specific pod
kubectl logs -n mlops <pod-name> -f
```

---

## Monitoring & Metrics

The API exposes Prometheus metrics at `/metrics`.

### Scrape with Prometheus

Add to Prometheus `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'heart-disease-api'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - mlops
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

### Key Metrics

- `api_requests_total` - Total requests by endpoint
- `api_request_latency_seconds` - Request latency histogram
- `predictions_total` - Total predictions made

---

## Troubleshooting

### Pod not starting?

```bash
kubectl describe pod <pod-name> -n mlops
kubectl logs <pod-name> -n mlops
```

### Model file missing?

Ensure `models/model.joblib` exists locally before building Docker image:

```bash
python -m src.train
docker build -t heart-disease-api:latest .
```

### Service not accessible?

```bash
# Check service endpoints
kubectl get endpoints -n mlops heart-disease-api

# Test within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://heart-disease-api.mlops:80/health
```

### Helm chart not found?

Ensure you're in the project root:
```bash
helm install heart-disease-api ./k8s/helm/heart-disease-api/
```

---

## Production Checklist

- [ ] Docker image pushed to registry (Docker Hub, ECR, GCR)
- [ ] Helm chart configured for production (replicas, resource limits, probes)
- [ ] Persistent volumes configured for model storage
- [ ] RBAC roles and service accounts created
- [ ] Network policies configured
- [ ] Ingress configured with TLS
- [ ] Monitoring and logging integrated (Prometheus + Grafana, ELK stack)
- [ ] Backup strategy for models and data
- [ ] CI/CD pipeline configured for automatic deployments
- [ ] Health checks and liveness probes validated

---

## Quick Reference

```bash
# Minikube
minikube start
minikube dashboard

# kubectl
kubectl apply -f k8s/deployment.yaml
kubectl get pods -n mlops -w
kubectl port-forward -n mlops svc/heart-disease-api 8000:80
kubectl logs -n mlops -f -l app=heart-disease-api
kubectl delete -f k8s/deployment.yaml

# Helm
helm install <release-name> k8s/helm/heart-disease-api/
helm upgrade <release-name> k8s/helm/heart-disease-api/
helm uninstall <release-name>
helm status <release-name>
```

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Chart Documentation](https://helm.sh/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
