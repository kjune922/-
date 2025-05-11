# 베이스 이미지로 Python을 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 로컬 환경에서 필요한 파일들을 컨테이너로 복사
COPY requirements.txt .

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 포트 노출 (Flask는 기본적으로 5000 포트를 사용)
EXPOSE 5000

# 애플리케이션 실행
CMD ["python", "carbon_scheduler.py"]