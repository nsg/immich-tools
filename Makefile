IMAGE_PREFIX := localhost/immich-tools

api: api-build postgres
	podman run \
		--net host \
		-e DB_HOSTNAME=127.0.0.1 \
		-e DB_USERNAME=postgres \
		-e DB_PASSWORD=postgres \
		${IMAGE_PREFIX}-api

api-build:
	podman build services/api -t ${IMAGE_PREFIX}-api

postgres:
	nc -v 127.0.0.1 5432 -w0
