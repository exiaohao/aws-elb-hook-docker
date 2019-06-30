FROM python:2.7-alpine

COPY lb.py ./
RUN pip install --no-cache-dir boto3 requests
CMD [ "python", "lb.py" ]