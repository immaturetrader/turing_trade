gcloud beta run deploy execute-alerts --platform managed --region asia-south1 --min-instances 0 --image gcr.io/boxwood-veld-298509/execute_alerts@sha256:491c52fcbce0220f58573b326dedc1a47ee8e70d019395858c513776a795ab78 --concurrency 80 --memory 256Mi --timeout 300 --cpu 1 --port 8080