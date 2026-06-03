FROM python:3.11-slim

WORKDIR /opt/ml/code
COPY ml/training/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/ /opt/ml/code/ml/
COPY app/domain/ /opt/ml/code/app/domain/
COPY app/services/ /opt/ml/code/app/services/
COPY app/__init__.py /opt/ml/code/app/__init__.py

ENV PYTHONPATH=/opt/ml/code
ENTRYPOINT ["python", "/opt/ml/code/ml/training/train.py"]
