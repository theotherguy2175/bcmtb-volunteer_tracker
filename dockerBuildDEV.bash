# docker buildx build --build-arg VERSION_STR="v.$(date +'%y.%-m.%-d.%-H.%-M')" --platform linux/amd64 -t bcmtb_hour-tracker:dev .
docker buildx build --platform linux/amd64 -t bcmtb_hour-tracker:dev .
docker tag bcmtb_hour-tracker 10.0.10.140:5000/bcmtb_hour-tracker:dev
docker push 10.0.10.140:5000/bcmtb_hour-tracker:dev
