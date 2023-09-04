#!/bin/bash
REGION="asia-southeast2"
PROJECT_ID="mitochondrion-project-344303"

REPOSITORY="looker-llm"
IMAGE="eva-looker-llm:latest"
SERVICE="eva-looker-llm"

IMAGE_URL=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE
PORT=8501
SERVICE_ACCOUNT="default@mitochondrion-project-344303.iam.gserviceaccount.com"

# 1st build locally
docker build --tag=$IMAGE_URL .

# 2nd push into repo
docker push $IMAGE_URL

# 3rd deploy to cloud run
gcloud run deploy $SERVICE --image $IMAGE_URL --region $REGION \
    --allow-unauthenticated --port $PORT --service-account $SERVICE_ACCOUNT
