FROM python:3.12-slim
WORKDIR /app
COPY data /app/data
RUN mkdir -p /app/output
# The agent writes /app/solve.py at run time, so the image must not exec it on
# start: keep the container alive and let the harness exec into it.
CMD ["sleep", "infinity"]
