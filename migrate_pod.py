import subprocess
import time
import yaml
import json
import os

TARGET_POD_NAME = "cpu-burn-high"
NAMESPACE = "default"
SOURCE_CLUSTER = "k3d-k3d-kr-seo-a"
DEST_CLUSTER = "k3d-k3d-kr-seo-d"
BACKUP_FILE = "pod-backup.yaml"
CHECKPOINT_FILE = "checkpoints.json"

def run(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()

def backup_pod_yaml():
    cmd = ["kubectl", "--context", SOURCE_CLUSTER, "get", "pod", TARGET_POD_NAME,
           "-n", NAMESPACE, "-o", "yaml"]
    yaml_data = run(cmd)
    with open(BACKUP_FILE, "w") as f:
        f.write(yaml_data)

def clean_yaml():
    with open(BACKUP_FILE) as f:
        pod = yaml.safe_load(f)
    for key in ["uid", "resourceVersion", "selfLink", "creationTimestamp"]:
        pod["metadata"].pop(key, None)
    pod["metadata"].pop("annotations", None)
    pod["status"] = {}
    with open(BACKUP_FILE, "w") as f:
        yaml.dump(pod, f)

def deploy_to_new_cluster():
    subprocess.run(["kubectl", "--context", DEST_CLUSTER, "apply", "-f", BACKUP_FILE])

def delete_old_pod():
    subprocess.run(["kubectl", "--context", SOURCE_CLUSTER, "delete", "pod", TARGET_POD_NAME, "-n", NAMESPACE])

def save_checkpoint():
    checkpoint = {
        "pod": TARGET_POD_NAME,
        "from": SOURCE_CLUSTER,
        "to": DEST_CLUSTER,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    data = []
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
    data.append(checkpoint)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    backup_pod_yaml()
    clean_yaml()
    deploy_to_new_cluster()
    save_checkpoint()
    time.sleep(2)
    delete_old_pod()
