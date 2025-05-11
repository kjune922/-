from kubernetes import client, config
import json
import os
import random
from datetime import datetime

CLUSTERS_FILE = "clusters.json"
KUBECONFIG_DIR = "./kubeconfigs"

def load_kube_config(cluster_name):
    config_path = os.path.join(KUBECONFIG_DIR, f"{cluster_name}_config")
    try:
        config.load_kube_config(config_file=config_path)
        print(f"[✓] Connected to {cluster_name}")
        return True
    except Exception as e:
        print(f"[X] Failed to load config for {cluster_name}: {e}")
        return False

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

if __name__ == "__main__":
    selected = select_cluster()
    if selected:
        task_name = f"task-{random.randint(1000, 9999)}"
        print(f"[▶] Assigning {task_name} to {selected}")
        create_pod(selected, task_name)