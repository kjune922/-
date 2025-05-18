"""
<코드 요약>
자동으로 클러스터를 생성해줌
chmod +x create_clusters.sh (최초 한 번만 명령어 입력)
./create_clusters.sh (파일 실행할 때마다 명령어 입력)
"""

#!/bin/bash

# 클러스터 이름 배열
clusters=("cluster1" "cluster2")

for cluster in "${clusters[@]}"
do
  echo "Creating Kind cluster: $cluster"

  # 클러스터 생성
  kind create cluster --name "$cluster"

  # kubeconfig 경로 출력 (기본 경로는 ~/.kube/config 안에 merge됨)
  # 별도 파일로 저장하려면 다음과 같이 export 가능
  kind get kubeconfig --name "$cluster" > "./kubeconfigs/${cluster}_config"

  echo "Saved kubeconfig for $cluster to ./kubeconfigs/${cluster}_config"
done

echo "All clusters created."