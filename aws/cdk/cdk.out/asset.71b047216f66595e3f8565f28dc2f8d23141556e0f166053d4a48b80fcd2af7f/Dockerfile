# Multi-stage minimal container for Squeeze MCP Server
# Compatible with AWS Fargate, AWS App Runner, or AWS Lambda (via Lambda Web Adapter)

FROM python:3.12-alpine AS runtime

# Create non-root user for security
RUN addgroup -S squeeze && adduser -S squeeze -G squeeze

WORKDIR /app

# Copy pure standard-library application
COPY squeeze_core.py app.py openapi-schema.json ./

# Environment defaults
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER squeeze

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

ENTRYPOINT ["python3", "app.py"]
