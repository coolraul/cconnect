Minimal FastAPI service for Render + Supabase development.

## Endpoints

### Health check
GET /health

### Echo test
POST /echo

Payload:
{
  "data": { "hello": "world" }
}

Response:
{
  "echoed": { "hello": "world" }
}
