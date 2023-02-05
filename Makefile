IMAGE_PREFIX := localhost/immich-tools

api: api-build postgres
	podman run \
		--net host \
		--env-file .env-file \
		${IMAGE_PREFIX}-api

hasher: hasher-build postgres camera
	podman run \
		--net host \
		--env-file .env-file \
		-v ${PWD}/camera:/user/bcdf8310-430f-48de-a4d2-0d2a1868e901 \
		${IMAGE_PREFIX}-hasher

syncthing: syncthing-build camera
	podman run \
		--net host \
		--env-file .env-file \
		-v ${PWD}/camera:/sync \
		${IMAGE_PREFIX}-syncthing

import: import-build camera
	podman run \
		--net host \
		--env-file .env-file \
		-v ${PWD}/files:/import \
		${IMAGE_PREFIX}-import

harmonize: harmonize-build camera
	podman run \
		--net host \
		--env-file .env-file \
		-v ${PWD}/camera:/sync \
		${IMAGE_PREFIX}-harmonize

.PHONY: camera
camera:
	test -e camera/thumbnails

%-build:
	podman build services/$* -t ${IMAGE_PREFIX}-$*

postgres:
	nc -v 127.0.0.1 5432 -w0
