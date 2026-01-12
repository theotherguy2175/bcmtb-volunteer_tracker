docker buildx build --platform linux/amd64 -t bcmtb_hour-tracker:latest .
docker tag bcmtb_hour-tracker 10.0.10.140:5000/bcmtb_hour-tracker:latest
docker push 10.0.10.140:5000/bcmtb_hour-tracker:latest
