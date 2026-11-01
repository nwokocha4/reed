FROM python:3.12-slim
WORKDIR /app
COPY environment/data /app/data
RUN mkdir -p /app/output
CMD ["python3", "/app/solve.py"]
