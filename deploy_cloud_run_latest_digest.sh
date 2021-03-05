cloud_run_function_name=$1
min_instances=$2
latest_digest=`gcloud container images list-tags --format='get(DIGEST)' --limit=1 --sort-by=~TIMESTAMP gcr.io/boxwood-veld-298509/$cloud_run_function_name`
echo "latest digest is $latest_digest for the function $cloud_run_function_name"
`gcloud beta run deploy $cloud_run_function_name --platform managed --region asia-south1 --min-instances min_instances --image gcr.io/boxwood-veld-298509/$cloud_run_function_name@latest_digest --concurrency 80 --memory 256Mi --timeout 300 --cpu 1 --port 8080`
