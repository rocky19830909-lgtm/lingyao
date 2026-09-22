FROM public.ecr.aws/docker/library/python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries 10 -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
COPY . .
RUN mkdir -p /data/uploads
ENV UPLOAD_DIR=/data/uploads
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]
