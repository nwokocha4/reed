FROM python:3.12-slim
WORKDIR /tests
COPY . /tests/
RUN pip install --no-cache-dir -r /tests/requirements.txt
RUN mkdir -p /app && chmod -R go-rwx /tests
CMD ["sh", "/tests/test.sh"]
