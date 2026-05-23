FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn jsonschema httpx redis pydantic numpy pandas psycopg2-binary mcp
COPY . .
ENV PORT=8080
ENV SCHEMA_PATH="/app/contracts/situation.schema.json"
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
