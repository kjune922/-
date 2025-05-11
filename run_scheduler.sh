#!/bin/bash

echo "[1] 클러스터 탄소 데이터 갱신"
python3 cluster_data_fetcher.py &

echo "[2] 탄소 기반 작업 스케줄러 실행"
while true; do
  python3 carbon_scheduler.py
  sleep 10  # 10초마다 새 작업을 스케줄링
done