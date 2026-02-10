FROM python:3.14.3-alpine3.22

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ LICENSE ./

ENTRYPOINT ["python3", "main.py"]

EXPOSE 5001