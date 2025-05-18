"""
<코드 요약>
탄소 데이터를 갱신하는 파일을 백그라운드로 실행(한번만 실행해도 데이터는 주기적으로 갱신됨),
10초마다 스케줄러 반복해서 실행
chmod +x run_scheduler.sh (최초 한 번만 명령어 입력)
./run_scheduler.sh (파일 실행할 때마다 명령어 입력)
"""

echo "[1] 클러스터 탄소 데이터 갱신"
python3 cluster_data_fetcher.py &

echo "[2] 탄소 기반 작업 스케줄러 실행"
while true; do
  python3 carbon_scheduler.py
  sleep 10  # 10초마다 새 작업을 스케줄링
done