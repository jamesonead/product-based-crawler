#! /bin/bash
VM_NAME=test-product-based-crawler
STARTUP_SCRIPT=./start_up.sh

gcloud compute instances create $VM_NAME \
    --project=hadoop-test-gsp \
    --zone=asia-east1-b \
    --machine-type=n1-standard-16 \
    --network=default \
    --service-account=700173755971-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/monitoring.write \
    --metadata-from-file=startup-script=$STARTUP_SCRIPT \
    --labels pro=report,user=james




