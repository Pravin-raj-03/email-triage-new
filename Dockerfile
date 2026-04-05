FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn pydantic openai pyyaml python-multipart httpx requests openenv-core gradio pandas

# Copy server and shared modules
COPY server/ server/
COPY models.py env.py tasks.py graders.py openenv.yaml ./

# Expose the FastAPI port
EXPOSE 7860

# Run the server entry point
CMD ["python", "-m", "server.app"]
