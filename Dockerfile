# Dockerfile

# 1. Python 기반 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY carbon_scheduler.py .

# 4. 필요한 라이브러리 설치
RUN pip install kubernetes

# 5. 실행 명령어
CMD ["python", "carbon_scheduler.py"]
