import subprocess
import requests
import time

# Electricity Maps API 설정
API_TOKEN = "YOUR_API_TOKEN_HERE"  # 발급받은 API 키로 대체하세요
API_URL = "https://api-access.electricitymaps.com/free-tier"

# 클러스터 정보 설정
clusters = {
    "cluster1": {
        "kubeconfig": "kubeconfigs/cluster1.yaml",
        "location": {"lat": 37.7749, "lon": -122.4194},  # 예: 샌프란시스코
    },
    "cluster2": {
        "kubeconfig": "kubeconfigs/cluster2.yaml",
        "location": {"lat": 48.8566, "lon": 2.3522},     # 예: 파리
    },
    "cluster3": {
        "kubeconfig": "kubeconfigs/cluster3.yaml",
        "location": {"lat": 59.9139, "lon": 10.7522},    # 예: 오슬로
    }
}

# CPU 사용량 조회 함수
def get_cpu_usage(kubeconfig):
    try:
        output = subprocess.check_output(
            f"kubectl --kubeconfig {kubeconfig} top nodes --no-headers",
            shell=True
        ).decode("utf-8")

        total_cpu = 0
        for line in output.strip().split("\n"):
            parts = line.split()
            cpu_str = parts[1]
            cpu = int(cpu_str.replace("m", "")) if cpu_str.endswith("m") else int(cpu_str) * 1000
            total_cpu += cpu
        return total_cpu
    except subprocess.CalledProcessError:
        print(f"❌ {kubeconfig}에서 CPU 사용량을 가져오는 데 실패했습니다.")
        return None

# 탄소 강도 조회 함수
def get_carbon_intensity(lat, lon):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    params = {
        "lat": lat,
        "lon": lon
    }
    try:
        response = requests.get(f"{API_URL}/carbon-intensity/latest", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data["carbonIntensity"]
        else:
            print(f"⚠️ 탄소 강도 API 호출 실패: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"⚠️ 탄소 강도 API 요청 중 예외 발생: {e}")
        return None

# 탄소 배출량 계산 함수
def estimate_carbon(cpu_millicores, carbon_intensity):
    watt_per_core = 10  # 1 core ≈ 10W
    kwh = (cpu_millicores / 1000) * watt_per_core / 1000  # kWh
    return kwh * carbon_intensity

# 워크로드 배포 함수
def deploy_workload(kubeconfig, workload_file="workload.yaml"):
    try:
        subprocess.run(f"kubectl --kubeconfig {kubeconfig} apply -f {workload_file}", shell=True, check=True)
        print(f"✅ 워크로드가 {kubeconfig}에 성공적으로 배포되었습니다.")
    except subprocess.CalledProcessError:
        print(f"❌ 워크로드 배포 실패: {kubeconfig}")

# 메인 스케줄러 로직
def main():
    best_cluster = None
    lowest_carbon = float("inf")

    print("📡 클러스터 상태 수집 중...\n")
    for name, info in clusters.items():
        cpu = get_cpu_usage(info["kubeconfig"])
        if cpu is None:
            continue

        location = info["location"]
        carbon_intensity = get_carbon_intensity(location["lat"], location["lon"])
        if carbon_intensity is None:
            continue

        carbon = estimate_carbon(cpu, carbon_intensity)

        print(f"🖥️  {name} | CPU: {cpu}m | 탄소 강도: {carbon_intensity} gCO₂e/kWh | 추정 탄소 배출량: {carbon:.4f} gCO₂e")

        if carbon < lowest_carbon:
            lowest_carbon = carbon
            best_cluster = name

        time.sleep(1)  # API 호출 간 딜레이

    if best_cluster:
        print(f"\n🌱 가장 탄소 효율적인 클러스터: {best_cluster}")
        deploy_workload(clusters[best_cluster]["kubeconfig"])
    else:
        print("⚠️ 모든 클러스터에서 정보를 불러오지 못했습니다.")

if __name__ == "__main__":
    main()
