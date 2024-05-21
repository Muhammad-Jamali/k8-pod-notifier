DOCKER_REGISTRY = localhost:5000
IMAGE_TAG = latest

dockerbuild: ./Dockerfile
	docker build -f ./Dockerfile -t $(DOCKER_REGISTRY)/k8-status-monitor/k8-status-monitor:$(IMAGE_TAG) .
	docker push $(DOCKER_REGISTRY)/k8-status-monitor/k8-status-monitor:$(IMAGE_TAG)
docker:
	make dockerbuild