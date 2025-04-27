from kubernetes import client, config, watch
import requests
import json
from typing import Dict, List, Optional

# 탄소 배출량 관련 데이터 타입 정의
class CarbonEmission:
    def __init__(self, region: str, value: float, timestamp: str):
        self.region = region        # 지역 식별자 (예: "us-east-1")
        self.value = value          # 탄소 배출량 (예: g CO2/kWh)
        self.timestamp = timestamp  # 측정 시간 (ISO 8601 형식)

# 각 노드의 탄소 배출량 정보를 저장하는 캐시
node_carbon_cache: Dict[str, CarbonEmission] = {}

def fetch_carbon_intensity(region: str) -> Optional[CarbonEmission]:
    """
    지정된 지역의 탄소 배출량 정보를 가져옵니다.
    실제 구현은 나중에 추가됩니다.
    
    :param region: 노드가 위치한 지역 (예: "us-east-1")
    :return: 탄소 배출량 정보 객체
    """
    # TODO: 실제 API에서 탄소 배출량 데이터를 가져오는 구현 추가
    # 임시로 더미 데이터 반환
    dummy_emissions = {
        "us-east-1": 500.0,   # 높은 탄소 배출
        "eu-west-1": 200.0,   # 중간 탄소 배출
        "eu-north-1": 50.0,   # 낮은 탄소 배출
    }
    
    if region in dummy_emissions:
        return CarbonEmission(
            region=region,
            value=dummy_emissions[region],
            timestamp="2025-04-27T12:00:00Z"
        )
    return None

def get_node_region(node) -> str:
    """
    노드의 지역 정보를 추출합니다.
    
    :param node: 쿠버네티스 노드 객체
    :return: 노드가 위치한 지역 식별자
    """
    # 노드의 라벨에서 지역 정보 추출
    # 실제 구현에서는 클라우드 프로바이더에 따라 다를 수 있음
    labels = node.metadata.labels
    
    # AWS 지역 예시
    if "topology.kubernetes.io/region" in labels:
        return labels["topology.kubernetes.io/region"]
    
    # 라벨이 없는 경우 노드 이름에서 추출 시도
    # 임시 로직: 노드 이름에 지역 정보가 포함되어 있다고 가정
    node_name = node.metadata.name
    for region in ["us-east-1", "eu-west-1", "eu-north-1"]:
        if region in node_name:
            return region
    
    # 기본값 반환
    return "unknown-region"

def update_carbon_data_for_nodes(nodes) -> None:
    """
    주어진 노드 리스트의 탄소 배출량 데이터를 업데이트합니다.
    
    :param nodes: 쿠버네티스 노드 객체 리스트
    """
    for node in nodes:
        region = get_node_region(node)
        emission = fetch_carbon_intensity(region)
        if emission:
            node_carbon_cache[node.metadata.name] = emission

def select_lowest_carbon_node(nodes) -> client.V1Node:
    """
    탄소 배출량이 가장 낮은 노드를 선택합니다.
    
    :param nodes: 쿠버네티스 노드 객체 리스트
    :return: 선택된 노드
    """
    # 모든 노드의 탄소 배출량 데이터 업데이트
    update_carbon_data_for_nodes(nodes)
    
    # 탄소 배출량 기준으로 정렬된 노드 리스트 생성
    sorted_nodes = sorted(
        nodes,
        key=lambda node: node_carbon_cache.get(node.metadata.name, CarbonEmission("unknown", float('inf'), "")).value
    )
    
    # 탄소 배출량이 가장 낮은 노드 반환
    return sorted_nodes[0]

def bind_pod_to_node(pod_name, namespace, node_name):
    """
    지정된 파드를 지정된 노드에 바인딩합니다.
    
    :param pod_name: 바인딩할 파드 이름
    :param namespace: 파드의 네임스페이스
    :param node_name: 대상 노드 이름
    """
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
        
        # 노드 레디니스 상태 필터링 (Ready 상태인 노드만 선택)
        ready_nodes = [node for node in nodes if is_node_ready(node)]
        
        if not ready_nodes:
            print("No ready nodes available for scheduling")
            continue

        # 4. 탄소 배출량이 가장 낮은 노드 선택
        selected_node = select_lowest_carbon_node(ready_nodes)
        
        # 선택된 노드의 탄소 배출량 정보 로깅
        node_emission = node_carbon_cache.get(selected_node.metadata.name)
        if node_emission:
            print(f"Selected node {selected_node.metadata.name} with carbon intensity: {node_emission.value} g CO2/kWh")
        else:
            print(f"Selected node {selected_node.metadata.name} (carbon data unavailable)")

        # 5. 선택한 Node에 Pod를 바인딩
        bind_pod_to_node(pod.metadata.name, pod.metadata.namespace, selected_node.metadata.name)

        print(f"Pod {pod.metadata.name} scheduled to {selected_node.metadata.name}")

def is_node_ready(node) -> bool:
    """
    노드가 Ready 상태인지 확인합니다.
    
    :param node: 쿠버네티스 노드 객체
    :return: 노드가 Ready 상태이면 True, 아니면 False
    """
    if not node.status.conditions:
        return False
        
    for condition in node.status.conditions:
        if condition.type == "Ready" and condition.status == "True":
            return True
    return False

if __name__ == "__main__":
    main()