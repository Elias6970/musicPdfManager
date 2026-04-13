@echo off
datamodel-codegen --url http://localhost:8000/openapi.json --input-file-type openapi --output frontend\pyqt\app\models\generated_models.py --output-model-type pydantic_v2.BaseModel --formatters ruff-check ruff-format
