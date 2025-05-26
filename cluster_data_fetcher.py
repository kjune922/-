import requests
import time
import json

"""
<코드 요약>
실시간으로 바뀌는 탄소 배출량의 값을 받아와 clusters.json 파일에 갱신신
"""

SERVER_URL = "https://carbon-server.onrender.com/status"  # 이 부분은 실제 EC2 IP로 바꾸기
CLUSTERS_FILE = "clusters.json"

def fetch_carbon_data():
    try:
        response = requests.get(SERVER_URL)
        if response.status_code == 200:
            data_list = response.json()  # 서버에서 리스트로 반환된다고 가정

            # 클러스터별로 정리
            cluster_data = {}
            for entry in data_list:
                cluster = entry["cluster"]
                cluster_data[cluster] = {
                    "carbon": entry["carbon"],
                    "timestamp": entry["timestamp"]
                }

            # 파일 저장
            with open(CLUSTERS_FILE, "w") as f:
                json.dump(cluster_data, f, indent=2)
            print("[✓] 클러스터 탄소 데이터 갱신됨")
        else:
            print(f"[X] 서버 응답 오류: {response.status_code}")
    except Exception as e:
        print(f"[X] 탄소 데이터 가져오기 실패: {e}")

if __name__ == "__main__":
    while True:
        fetch_carbon_data()
        time.sleep(5)  # 5초마다 갱신
