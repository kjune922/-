from prometheus_client import start_http_server, Gauge
import subprocess
import time

# Prometheus 메트릭 정의
carbon_gauge = Gauge("carbon_emission_gco2", "Carbon Emission in gCO2eq", ["cluster"])

# 클러스터 목록
clusters = ["k3d-k3d-kr-seo-a", "k3d-k3d-kr-seo-b", "k3d-k3d-kr-seo-c", "k3d-k3d-kr-seo-d"]

# 탄소 환산 함수
def calculate_carbon(cpu_m, mem_mib):
    return round((cpu_m * 0.000475) + (mem_mib * 0.000285), 4)

# 클러스터별 리소스 수집
def get_cluster_resources(context):
    try:
        result = subprocess.check_output(
            ["kubectl", "--context", context, "top", "pods", "--no-headers"]
        )
        cpu_total, mem_total = 0, 0
        for line in result.decode().splitlines():
            parts = line.split()
            cpu = parts[1].replace("m", "")
            mem = parts[2].replace("Mi", "")
            cpu_total += int(cpu)
            mem_total += int(mem)
        return cpu_total, mem_total
    except:
        return 0, 0

# 메트릭 서버 시작 및 루프
if __name__ == "__main__":
    start_http_server(8000)
    print("✅ carbon_exporter running at http://localhost:8000/metrics")

    while True:
        for cluster in clusters:
            cpu, mem = get_cluster_resources(cluster)
            gco2 = calculate_carbon(cpu, mem)
            carbon_gauge.labels(cluster=cluster).set(gco2)
            print(f"{cluster}: {cpu} mCPU + {mem} MiB → {gco2} gCO₂eq")

        time.sleep(10)
