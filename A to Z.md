# Carbon-Aware Scheduler 실습 기록

본 문서는 로컬 환경에서 Kind(Kubernetes in Docker)를 기반으로 한 **탄소 인지형 스케줄러(carbon-aware scheduler)**의 구축 및 실습 과정을 정리한 내용입니다.

## 📦 프로젝트 개요

- **목표**: 탄소 배출량 데이터를 기반으로 가장 친환경적인 노드에 파드를 스케줄링하는 쿠버네티스 스케줄러 구현
- **기반 기술**:
  - Docker / Kind
  - Kubernetes (kubectl)
  - Python (Kubernetes Client)
  - Custom Scheduler
  - RBAC 설정
  - 테스트용 NGINX 파드

---

## 🛠️ 개발 환경 구성

### 1. Docker & Kind 설치

- Docker Desktop 설치
- Kind 설치 (Windows Chocolatey 사용):
  ```bash
  choco install kind
  ```

### 2. Kind 클러스터 생성

```bash
kind create cluster --name carbon-cluster
```

- 생성된 클러스터는 `kubectl`로 제어 가능
- `kubectl cluster-info` 또는 `kubectl get nodes`로 정상 연결 확인

---

## 🧠 Carbon Scheduler 구현

### 1. 주요 기능

- 쿠버네티스 클러스터 내의 `Pending` 상태 파드 감지
- 탄소 배출량 데이터(더미) 기반으로 가장 친환경적인 노드 선택
- 선택된 노드에 수동 바인딩 수행 (custom scheduler)

### 2. 핵심 파일

- `carbon_scheduler.py`: 스케줄러 로직(Python)
- `Dockerfile`: 해당 스케줄러의 컨테이너 이미지 정의

### 3. Docker 이미지 빌드 및 로딩

```bash
docker build -t carbon-scheduler:latest .
kind load docker-image carbon-scheduler:latest --name carbon-cluster
```

---

## 🚀 배포 및 테스트

### 1. Deployment (carbon-scheduler.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: carbon-scheduler
  labels:
    app: carbon-scheduler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: carbon-scheduler
  template:
    metadata:
      labels:
        app: carbon-scheduler
    spec:
      serviceAccountName: carbon-scheduler-sa
      containers:
      - name: carbon-scheduler
        image: carbon-scheduler:latest
```

```bash
kubectl apply -f carbon-scheduler.yaml
```

### 2. RBAC 설정 (rbac.yaml)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: carbon-scheduler-sa

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: carbon-scheduler-role
rules:
- apiGroups: [""]
  resources: ["pods", "pods/binding", "nodes"]
  verbs: ["get", "list", "watch", "create"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: carbon-scheduler-rolebinding
subjects:
- kind: ServiceAccount
  name: carbon-scheduler-sa
  namespace: default
roleRef:
  kind: ClusterRole
  name: carbon-scheduler-role
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f rbac.yaml
```

---

### 3. 테스트 파드 실행 (nginx-test-pod.yaml)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-test
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
  schedulerName: carbon-scheduler
```

```bash
kubectl apply -f nginx-test-pod.yaml
```

---

## 🧪 로그 확인 및 결과 검증

### 스케줄러 로그 확인

```bash
kubectl logs -f deployment/carbon-scheduler
```

정상 로그 예시:

```
Carbon Scheduler is running...
Found a pod to schedule: nginx-test
Selected node carbon-cluster-control-plane with carbon intensity: 200.0 g CO2/kWh
Pod nginx-test scheduled to carbon-cluster-control-plane
```

### 파드 상태 확인

```bash
kubectl get pod nginx-test -o wide
kubectl get pod nginx-test -o jsonpath="{.spec.schedulerName}"
kubectl get pod nginx-test -o jsonpath="{.spec.nodeName}"
```

---

## 🐞 문제 해결 (Troubleshooting)

| 문제                            | 원인 및 해결법                                                                 |
|-------------------------------|------------------------------------------------------------------------------|
| `403 Forbidden` (watch error) | `default` SA가 watch 권한 없음 → RBAC에서 ServiceAccount 및 ClusterRoleBinding 적용 |
| `target must not be None`     | `V1Binding` 생성 시 `target` 필드 빠짐 → `V1ObjectReference` 정확히 정의해야 함     |
| Pod이 자동 스케줄링됨          | `schedulerName`이 기본값(`default-scheduler`)일 경우 발생 → 명시적으로 설정 필요    |
| 새 이미지 반영 안됨           | 기존 Pod에 캐시된 이미지가 있음 → Pod 삭제 후 다시 생성, `kind load` 반복 필요     |

---

## ✅ 결과

- 커스텀 스케줄러가 정상적으로 파드를 감지하고 탄소 배출량 기준으로 노드를 선택함
- RBAC, Docker 이미지 연동, 수동 바인딩까지 통합 성공
- 이후 Flask 기반 API 연동 및 React 시각화로 확장 예정

---
