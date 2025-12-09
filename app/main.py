from fastapi import FastAPI
from app.schemas import EchoRequest, EchoResponse

app = FastAPI(
    title="Senior Support API",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest):
    """
    Test endpoint for Replit JS client.
    Just echoes whatever JSON is sent.
    """
    return {"echoed": payload.data}
