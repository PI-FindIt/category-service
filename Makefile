OS := $(shell uname)
ifeq ($(OS),Darwin)
	EXECUTABLES = gsed gtr
	K := $(foreach exec,$(EXECUTABLES),\
			$(if $(shell which $(exec)),some string,$(error "No GNU tools installed on macOS, consider installing using brew")))
	SED := gsed
	TR := gtr
else
	SED := sed
	TR := tr
endif

PROJECT_NAME := $(shell basename $(PWD))
PROJECT_NAME_SNAKE_CASE := $(shell echo $(PROJECT_NAME) | $(TR) '-' '_')
PROJECT_NAME_PASCAL_CASE := $(shell echo $(PROJECT_NAME) | $(SED) 's/[^-]\+/\L\u&/g' | $(TR) -d '-')
PROJECT_NAME_KEBAB_CASE := $(shell echo $(PROJECT_NAME) | $(SED) 's/-[^-]*$$//')
PROJECT_NAME_SPACES := $(shell echo $(PROJECT_NAME) | $(SED) 's/-/ /g; s/\b\(.\)/\u\1/g')

TEMPLATE_FOLDER := ./templates
COMPOSE_FILE := compose.yaml
COMPOSE_TEMPLATE := $(TEMPLATE_FOLDER)/compose.template.yaml
COMPOSE_PROD_FILE := compose.prod.yaml
COMPOSE_PROD_TEMPLATE := $(TEMPLATE_FOLDER)/compose.prod.template.yaml

DOCKERFILE := Dockerfile
DOCKERFILE_TEMPLATE := $(TEMPLATE_FOLDER)/Dockerfile.template

DOCKERFILE_PROD := Dockerfile.prod
DOCKERFILE_PROD_TEMPLATE := $(TEMPLATE_FOLDER)/Dockerfile.template.prod

WORKFLOW_TEMPLATE := $(TEMPLATE_FOLDER)/submodule.template.yaml
WORKFLOW_FILE := .github/workflows/submodule.yaml
SONAR_TEMPLATE := $(TEMPLATE_FOLDER)/sonar.template.yaml
SONAR_FILE := .github/workflows/sonar.yaml

PROTOBUF_FOLDER := protobuf/$(PROJECT_NAME_SNAKE_CASE)
PROTOBUF_SERVICE_FILE := $(PROTOBUF_FOLDER)/$(PROJECT_NAME_KEBAB_CASE).proto
PROTOBUF_SERVICE_FILE_TEMPLATE := $(TEMPLATE_FOLDER)/service.template.proto
PROTOBUF_SERVICE_SERVER := src/api/service.py
PROTOBUF_SERVICE_SERVER_TEMPLATE := $(TEMPLATE_FOLDER)/service.template.py
PROTOBUF_CONNECTIONS := protobuf/connections.py
PROTOBUF_CONNECTIONS_TEMPLATE := $(TEMPLATE_FOLDER)/connections.template.py

MAIN_FILE := src/main.py
MAIN_TEMPLATE := $(TEMPLATE_FOLDER)/main.template.py

GRAPHQL_FILE := src/api/graphql.py
GRAPHQL_TEMPLATE := $(TEMPLATE_FOLDER)/graphql.template.py

MODEL_FILE := src/models/model.py
MODEL_TEMPLATE := $(TEMPLATE_FOLDER)/model.template.py

all: dev prod protobuf-create protobuf-gen model-create main-create merge-upstream-config

prepare-compose:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g; s/kebab/$(PROJECT_NAME_KEBAB_CASE)/g' $(COMPOSE_TEMPLATE) > $(COMPOSE_FILE)

prepare-compose-prod:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g; s/kebab/$(PROJECT_NAME_KEBAB_CASE)/g' $(COMPOSE_PROD_TEMPLATE) > $(COMPOSE_PROD_FILE)

prepare-dockerfile:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(DOCKERFILE_TEMPLATE) > $(DOCKERFILE)

prepare-dockerfile-prod:
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(DOCKERFILE_PROD_TEMPLATE) > $(DOCKERFILE_PROD)

prepare-workflow:
	mkdir -p .github/workflows
	$(SED) 's/serviceName/$(PROJECT_NAME)/g' $(WORKFLOW_TEMPLATE) > $(WORKFLOW_FILE)
	cp $(SONAR_TEMPLATE) $(SONAR_FILE)

protobuf-gen:
	python -m grpc_tools.protoc -I=$(PROTOBUF_FOLDER) --python_out=$(PROTOBUF_FOLDER) --grpc_python_out=$(PROTOBUF_FOLDER) --pyi_out=$(PROTOBUF_FOLDER) $(PROTOBUF_SERVICE_FILE)
	$(SED) 's/import $(PROJECT_NAME_KEBAB_CASE)_pb2/from . import $(PROJECT_NAME_KEBAB_CASE)_pb2/g' $(PROTOBUF_FOLDER)/$(PROJECT_NAME_KEBAB_CASE)_pb2_grpc.py > $(PROTOBUF_FOLDER)/$(PROJECT_NAME_KEBAB_CASE)_pb2_grpc.py.tmp
	mv $(PROTOBUF_FOLDER)/$(PROJECT_NAME_KEBAB_CASE)_pb2_grpc.py.tmp $(PROTOBUF_FOLDER)/$(PROJECT_NAME_KEBAB_CASE)_pb2_grpc.py

protobuf-create:
	git submodule update --init --recursive
	cd protobuf && git checkout main && cd ..
	mkdir -p $(PROTOBUF_FOLDER)
	touch $(PROTOBUF_FOLDER)/__init__.py
	$(SED) 's/ServiceName/$(PROJECT_NAME_PASCAL_CASE)/g' $(PROTOBUF_SERVICE_FILE_TEMPLATE) > $(PROTOBUF_SERVICE_FILE)
	$(SED) 's/service_name/$(PROJECT_NAME_SNAKE_CASE)/g; s/ServiceName/$(PROJECT_NAME_PASCAL_CASE)/g' $(PROTOBUF_SERVICE_SERVER_TEMPLATE) > $(PROTOBUF_SERVICE_SERVER)
	$(SED) 's/service_name/$(PROJECT_NAME_SNAKE_CASE)/g; s/service-name/$(PROJECT_NAME)/g; s/ServiceName/$(PROJECT_NAME_PASCAL_CASE)/g; s/kebab/$(PROJECT_NAME_KEBAB_CASE)/g' $(PROTOBUF_CONNECTIONS_TEMPLATE) >> $(PROTOBUF_CONNECTIONS)

main-create:
	$(SED) 's/serviceName/$(PROJECT_NAME_KEBAB_CASE)/g; s/ServiceName/$(PROJECT_NAME_SPACES)/g' $(MAIN_TEMPLATE) > $(MAIN_FILE)

model-create:
	$(SED) 's/service_name/$(PROJECT_NAME_SNAKE_CASE)/g;' $(GRAPHQL_TEMPLATE) > $(GRAPHQL_FILE)
	$(SED) 's/service_name/$(PROJECT_NAME_SNAKE_CASE)/g;' $(MODEL_TEMPLATE) > $(MODEL_FILE)

dev: prepare-dockerfile prepare-compose prepare-workflow

prod: prepare-dockerfile-prod prepare-compose-prod prepare-workflow

clean:
	rm -f $(COMPOSE_FILE) $(COMPOSE_PROD_FILE) $(DOCKERFILE) $(DOCKERFILE_PROD) $(WORKFLOW_FILE) $(PROTOBUF_SERVICE_SERVER) $(GRAPHQL_FILE) $(MODEL_FILE) $(MAIN_FILE) $(SONAR_FILE)
	rm -rf $(PROTOBUF_FOLDER)
	git remote remove upstream

migration-new:
	alembic revision --autogenerate -m "$(message)"

migration-upgrade:
	alembic upgrade head

migration-downgrade:
	alembic downgrade -1

merge-upstream-config:
	git checkout main
	git remote add upstream git@github.com:PI-FindIt/service-template.git
	git fetch upstream
	git merge upstream/main --allow-unrelated-histories

merge-upstream:
	git fetch upstream
	git merge upstream/main
