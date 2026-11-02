FROM python:3.12-slim
WORKDIR /tests
COPY requirements.txt /tests/requirements.txt
RUN pip install --no-cache-dir -r /tests/requirements.txt
COPY test.sh /tests/test.sh
COPY conftest.py /tests/conftest.py
COPY test_outputs.py /tests/test_outputs.py
COPY expected.json /tests/expected.json
COPY graded /tests/graded
RUN mkdir -p /app && chmod -R go-rwx /tests
CMD ["sh", "/tests/test.sh"]
