# 베이스 이미지 선택
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 로컬 파일 복사
COPY . .

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# kubeconfig 접근을 위해 권한 설정 (옵션)
RUN mkdir -p /root/.kube

# 환경변수 설정 (예시로 KUBECONFIG_DIR 지정)
ENV KUBECONFIG_DIR=/app/kubeconfigs

# 기본 실행 명령: carbon_scheduler 실행
CMD ["python", "carbon_scheduler.py"]