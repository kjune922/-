import subprocess
import time
import os

CLUSTERS = ["k3d-k3d-kr-seo-a", "k3d-k3d-kr-seo-b", "k3d-k3d-kr-seo-c", "k3d-k3d-kr-seo-d"]
THRESHOLD = 0.5  # gCO₂eq
MIGRATION_SCRIPT = "python3 migration_manager.py"
INTERVAL = 10

def get_cluster_cpu(context):
    try:
        result = subprocess.check_output(
            ["kubectl", "--context", context, "top", "pods", "--no-headers"]
        )
        total_mcpu = 0
        for line in result.decode().splitlines():
            cpu = line.split()[1]
            if cpu.endswith("m"):
                total_mcpu += int(cpu[:-1])
        return total_mcpu
    except:
        return 0

def calculate_carbon(cpu):
    return round(cpu * 0.000475, 3)

def monitor_and_trigger():
    while True:
        for ctx in CLUSTERS:
            cpu = get_cluster_cpu(ctx)
            carbon = calculate_carbon(cpu)
            print(f"{ctx}: {cpu} mCPU → {carbon} gCO₂eq")
            if carbon > THRESHOLD:
                print(f"⚠️  {ctx} 임계치 초과 → 마이그레이션 실행")
                os.system(MIGRATION_SCRIPT)
                return
        time.sleep(INTERVAL)

if __name__ == "__main__":
    monitor_and_trigger()
