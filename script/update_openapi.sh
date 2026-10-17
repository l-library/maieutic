curl -o frontend/src/api/openapi.json --url 'http://127.0.0.1:8000/openapi.json' && echo "openapi.json已更新"
cd frontend && npm run gen:api && echo "type.ts 已更新"