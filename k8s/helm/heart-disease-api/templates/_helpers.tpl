{{/*
Expand the name of the chart.
*/}}
{{- define "heart-disease-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "heart-disease-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "heart-disease-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "heart-disease-api.labels" -}}
helm.sh/chart: {{ include "heart-disease-api.chart" . }}
{{ include "heart-disease-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "heart-disease-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "heart-disease-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: {{ include "heart-disease-api.name" . }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "heart-disease-api.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "heart-disease-api.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
