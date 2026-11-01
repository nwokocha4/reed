FROM python:3.12-slim
WORKDIR /tests
COPY tests/requirements.txt /tests/requirements.txt
RUN pip install --no-cache-dir -r /tests/requirements.txt
COPY tests/test.sh /tests/test.sh
COPY tests/conftest.py /tests/conftest.py
COPY tests/test_outputs.py /tests/test_outputs.py
COPY tests/expected.json /tests/expected.json
COPY tests/graded /tests/graded
RUN mkdir -p /app && chmod -R go-rwx /tests
CMD ["sh", "/tests/test.sh"]
