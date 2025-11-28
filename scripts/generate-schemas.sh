#! /bin/bash
# This script generates the schemas for the project.
cd /app
# create the schemas directory if it doesn't exist
mkdir ./frontend/schemas
# curl the schemas from http://django:8000/api/schema/ and save it to the ./frontend/schemas directory
curl -X GET http://django:8000/api/schema/ > ./frontend/schemas/django-overtuned.yaml
# curl the schemas from http:/django:8000/api/auth/openapi.yaml
curl -X GET http://django:8000/api/auth/openapi.yaml > ./frontend/schemas/auth.yaml

# generate types from the schemas using openapi-typescript
cd frontend
npx openapi-typescript schemas/django-overtuned.yaml --output ./types/django-overtuned.d.ts
npx openapi-typescript schemas/auth.yaml --output ./types/auth.d.ts

# delete the schemas directory
rm -rf ./schemas

exit 0
