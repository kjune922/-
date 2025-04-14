# carbon_scheduler.py

from kubernetes import client, config, watch

def bind_pod_to_node(pod_name, namespace, node_name):
    target = client.V1ObjectReference(api_version="v1", kind="Node", name=node_name)
    meta = client.V1ObjectMeta(name=pod_name)
    body = client.V1Binding(target=target, metadata=meta)

    client.CoreV1Api().create_namespaced_binding(namespace=namespace, body=body)

def main():
    # 쿠버네티스 클러스터 내부에서 실행할 때 설정
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    w = watch.Watch()

    print("Carbon Scheduler is running...")

    # Pod 이벤트 감시
    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']

        # 1. 아직 스케줄링 안 된 상태만 필터
        if pod.status.phase != "Pending":
            continue

        # 2. carbon-scheduler로 지정된 Pod만 처리
        if pod.spec.scheduler_name != "carbon-scheduler":
            continue

        print(f"Found a pod to schedule: {pod.metadata.name}")

        # 3. 모든 Node 목록 가져오기
        nodes = v1.list_node().items

        # 4. 여기서는 간단히 이름 순 정렬로 "탄소가 적다"고 가정
        selected_node = sorted(nodes, key=lambda node: node.metadata.name)[0]

        # 5. 선택한 Node에 Pod를 바인딩
        bind_pod_to_node(pod.metadata.name, pod.metadata.namespace, selected_node.metadata.name)

        print(f"Pod {pod.metadata.name} scheduled to {selected_node.metadata.name}")

if __name__ == "__main__":
    main()
