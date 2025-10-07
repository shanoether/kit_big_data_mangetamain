colima start
docker context use colima
docker buildx use colima-builder

# Create and use a buildx builder (once)
docker buildx create --name colima-builder --use --driver docker-container --use
docker buildx inspect --bootstrap

# Build the image for linux/amd64 and load it locally
DOCKER_BUILDKIT=1 docker buildx build --platform linux/amd64 -t mangetamain-processor:latest --load .

# Run the image
#docker run --rm -v "$(pwd)/data:/app/data" mangetamain-processor:latest

#test
#docker run --rm -it --entrypoint /bin/bash -v "$(pwd)/data:/app/data" mangetamain-processor:latest
# then inside container:
#python -c "import sys; print(sys.path); import mangetamain; print('OK')"