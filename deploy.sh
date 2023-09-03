#!/bin/bash
PROJECT_ID="mitochondrion-project-344303"
REGION="asia-southeast2"
REPOSITORY="looker-llm"
IMAGE="eva-looker-llm:latest"

docker build --tag=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE .

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE
