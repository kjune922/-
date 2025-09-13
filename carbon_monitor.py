from monitor import get_cluster_cpu_memory_usage

CARBON_FACTORS = {
    "k3d-k3d-kr-seo-a": 350,
    "k3d-k3d-kr-seo-b": 280,
    "k3d-k3d-kr-seo-c": 400,
    "k3d-k3d-kr-seo-d": 250
}

def estimate_carbon(cpu_millicores, mem_mebibytes, carbon_factor):
    # CPU 기준: 1mCPU = 0.1W
    cpu_watts = cpu_millicores * 0.1
    cpu_kwh = cpu_watts / 1000

    # Memory 기준: 1MiB = 약 0.0003 kWh/h
    mem_kwh = mem_mebibytes * 0.0003

    total_kwh = cpu_kwh + mem_kwh
    return total_kwh * carbon_factor

if __name__ == "__main__":
    print("CPU + 메모리 기반 탄소 배출량 측정\n")

    for context in CARBON_FACTORS:
        cpu, mem = get_cluster_cpu_memory_usage(context)
        carbon = estimate_carbon(cpu, mem, CARBON_FACTORS[context])
        print(f"{context}: {cpu} mCPU / {mem} MiB → {carbon:.2f} gCO₂eq")
