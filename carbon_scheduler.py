from kubernetes import client, config
import json
import os
import random
from datetime import datetime

"""
<코드 요약>
1. clusters.json 파일에서 클러스터별 탄소배출량 정보를 읽음
2. 탄소배출량이 가장 낮은 클러스터를 선택
3. 해당 클러스터의 kubeconfig를 불러옴
4. 새로운 Pod를 배포
"""

CLUSTERS_FILE = "clusters.json"
KUBECONFIG_DIR = "./kubeconfigs"
# clusters.json: 클러스터 이름과 각 클러스터의 탄소배출량 정보가 담긴 JSON 파일
# ./kubeconfigs/: 각 클러스터에 접근하기 위한 kubeconfig 파일들이 저장된 디렉터리

def load_kube_config(cluster_name):
    config_path = os.path.join(KUBECONFIG_DIR, f"{cluster_name}_config")
    try:
        config.load_kube_config(config_file=config_path)
        print(f"[✓] Connected to {cluster_name}")
        return True
    except Exception as e:
        print(f"[X] Failed to load config for {cluster_name}: {e}")
        return False
# 특정 클러스터의 kubeconfig 파일을 로드해서 해당 클러스터에 연결을 시도

def create_pod(cluster_name, task_name):
    if not load_kube_config(cluster_name):
        return

    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": task_name, "labels": {"task": task_name}},
        "spec": {
            "containers": [{
                "name": "carbon-task",
                "image": "nginx",
                "ports": [{"containerPort": 80}]
            }]
        }
    }

    try:
        api = client.CoreV1Api()
        api.create_namespaced_pod(namespace="default", body=pod_manifest)
        print(f"[✓] Pod {task_name} scheduled on {cluster_name}")
    except Exception as e:
        print(f"[X] Failed to schedule pod on {cluster_name}: {e}")
# 선택된 클러스터에 task_name 이름의 Pod를 생성
# nginx 이미지를 사용하는 컨테이너를 기본으로 갖는 Pod를 생성
# Pod는 default 네임스페이스에 배포

def select_cluster():
    if not os.path.exists(CLUSTERS_FILE):
        print("[X] Cluster data file not found.")
        return None

    with open(CLUSTERS_FILE) as f:
        clusters = json.load(f)

    if not clusters:
        print("[X] No cluster data available.")
        return None

    return min(clusters, key=lambda k: clusters[k]["carbon"])
# clusters.json 파일에서 클러스터 정보를 읽고, carbon 값(탄소 배출량)이 가장 낮은 클러스터를 선택하여 반환

if __name__ == "__main__":
    selected = select_cluster()
    if selected:
        task_name = f"task-{random.randint(1000, 9999)}"
        print(f"[▶] Assigning {task_name} to {selected}")
        create_pod(selected, task_name)
# 선택한 클러스터로 랜덤한 이름의 새로운 pod 생성