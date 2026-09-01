FROM python:3.15.0b2-alpine3.22

RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ LICENSE ./

ENTRYPOINT ["python3", "main.py"]

EXPOSE 5001
