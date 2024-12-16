#!/bin/bash
docker run -p 5000:5000 --env WANDB_API_KEY=$WANDB_API_KEY flask-service
