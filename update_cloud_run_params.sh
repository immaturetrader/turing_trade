cloud_run_function_name=$1
min_instances=$2
`gcloud beta run services update $cloud_run_function_name --platform managed --region asia-south1 --min-instances=$min_instances`
