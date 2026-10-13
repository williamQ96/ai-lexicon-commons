FROM python:3.12-slim
WORKDIR /app
COPY server.py ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
USER 1026:100
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/_mirror-health', timeout=3)"
CMD ["python", "server.py"]
