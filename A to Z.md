서버 == 실제 컴퓨터 1대, 가상 서버 1개
노드 == 쿠버네티스가 관리하는 서버 1개
클러스터 == 여러 개의 서버(노드)를 하나로 묶은거임.

pod == 하나 이상의 컨테이너를 모아 놓은 것. 쿠버네티스 애플리케이션의 최소 단위임. 

// local에서 A to Z까지 과정.

Docker 이미지 빌드

```bash
// docker desktop 실행 시킨 상태에서 해야됨.
// vscode에서 실행함.
docker build -t carbon-exporter:latest .
```

k3d 세팅

```bash
// 설치 실패 떠서 관리자 권한으로 cmd 실행
cd C:\Users\USER\Desktop\Carbon
choco install k3d

// 설치 완료 후 vscode 껐다가 다시 켜서 k3d 버전 확인
k3d version

// k3d 클러스터 확인
k3d cluster list

// k3d 클러스터 생성
k3d cluster create carbon-cluster

// exporter 이미지 빌드
k3d image import carbon-exporter:latest -c carbon-cluster
```

k3d vs minikube

✅ 이유: 너희 프로젝트 요구사항과 `k3d`의 적합성

| 요구사항 | 왜 `k3d`가 적합한가 |
| --- | --- |
| ✅ Prometheus + Grafana 모니터링 | Helm 차트로 쉽게 설치 가능, 실습에 적합한 네트워크 구조 제공 |
| ✅ Exporter 이미지 수동 배포 필요 | `k3d image import`로 로컬 빌드 이미지 바로 반영 가능 |
| ✅ 멀티 클러스터 확장 계획 (Caspian 기반) | `k3d cluster create`로 여러 클러스터 시뮬레이션 가능 |
| ✅ 로컬 실습 중심 (EC2나 실제 클라우드 X) | `k3d`는 Docker 기반으로 로컬에서 안전하게 작동함 |
| ✅ 경량 Kubernetes 필요 | `minikube`보다 훨씬 가볍고 빠름 |

---

❌ 반대로 지금 상태 (Docker Desktop Kubernetes)의 문제점

| 항목 | 한계 |
| --- | --- |
| Docker Desktop의 Kubernetes는 `docker build`한 이미지를 자동으로 인식 못 함 | 별도 레지스트리 설정 필요 |
| Helm이나 multi-node 구성 연습에 불리 | k3d처럼 자유롭게 노드/클러스터 추가 불가 |
| 프로젝트 제출/실습용 시연에 불편 | 발표 시 구조 설명이 복잡해짐 ("이건 Docker Desktop이고요…") |

---

🔥 결론: 너희 프로젝트 성격상 `k3d` 사용이 가장 맞다

만든 exporter 이미지를 클러스터에 배포

```bash
kubectl apply -f k8s/

// 배포 실패.. 예전에 kind로 생성한 클러스터 api를 가리키고있음.

// cmd 를 관리자 권한으로 실행
notepad %USERPROFILE%\.kube\config

// notepad로 열린 파일에 아래 내용을 수정
server: https://localhost:56330

// 그러고 vscode에서 node 확인\
kubectl get nodes

C:\Users\USER\Desktop\Carbon>kubectl get nodes
NAME                          STATUS   ROLES                  AGE   VERSION
k3d-carbon-cluster-server-0   Ready    control-plane,master   45m   v1.31.5+k3s1       

C:\Users\USER\Desktop\Carbon>kubectl apply -f k8s/
deployment.apps/carbon-exporter created
service/carbon-exporter created

// 여기서 pod 상태가 errImagePull 상태인 에러가 발생함... 

C:\Users\USER\Desktop\Carbon>kubectl get pods
NAME                               READY   STATUS         RESTARTS   AGE
carbon-exporter-765ff6fb9d-zz24t   0/1     ErrImagePull   0          10s

C:\Users\USER\Desktop\Carbon>kubectl get svc
NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
carbon-exporter   ClusterIP   10.43.234.64   <none>        8000/TCP   15s
kubernetes        ClusterIP   10.43.0.1      <none>        443/TCP    47m

// k8s/exporter-deployment.yaml 파일 열어서 
containers:
      - name: carbon-exporter
        image: carbon-exporter:latest
        imagePullPolicy: Never ## 이 줄 추가
        
// 그러고 corbon-exporter 지우고 다시 포하면 됨.

C:\Users\USER\Desktop\Carbon>kubectl delete deployment carbon-exporter
deployment.apps "carbon-exporter" deleted

C:\Users\USER\Desktop\Carbon>kubectl apply -f k8s/
deployment.apps/carbon-exporter created
service/carbon-exporter unchanged

C:\Users\USER\Desktop\Carbon>kubectl get pods
NAME                               READY   STATUS    RESTARTS   AGE
carbon-exporter-64d68c596c-qnn98   1/1     Running   0          6s

// 이렇게 뜨면 성공한거임. 이제 exporter가 클러스터 내에서 정상 작동중이고, prometheus가 metric
수집할 준비가 완료됐음.
```

prometheus 설치

```bash
// 먼저 helm부터 설치
// 관리자 권한 cmd
choco install kubernetes-helm

// vscode 재 시작
helm version

// prometheus 설치
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus -f grafana/provisioning/prometheus-values.yaml

// prometheus 서버가 제대로 동작 중인지 확인
// pod 상태 == running
C:\Users\USER\Desktop\Carbon>kubectl get pods -l app.kubernetes.io/name=prometheus
NAME                                 READY   STATUS    RESTARTS   AGE
prometheus-server-78b77d9478-4j4d5   2/2     Running   0          79s

// 포트 : 80
C:\Users\USER\Desktop\Carbon>kubectl get svc -l app.kubernetes.io/name=prometheus
NAME                TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
prometheus-server   ClusterIP   10.43.253.78   <none>        80/TCP    83s 
```

grafana 설치

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana grafana/grafana -f grafana/provisioning/grafana-values.yaml

C:\Users\USER\Desktop\Carbon>kubectl get pods -l app.kubernetes.io/name=grafana
NAME                       READY   STATUS            RESTARTS   AGE
grafana-6876bf4c5d-5dmkn   0/1     PodInitializing   0          12s

C:\Users\USER\Desktop\Carbon>kubectl get svc -l app.kubernetes.io/name=grafana
NAME      TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
grafana   NodePort   10.43.212.124   <none>        80:32619/TCP   16s

// 로컬에서 grafana 접속 가능.
http://localhost:32619

// 접속 안되면 Windows + Docker Desktop + k3d 조합에서 발생하는 네트워크 포워딩 이슈임.
// kubectl port-forward로 강제 연결
C:\Users\USER\Desktop\Carbon>kubectl port-forward svc/grafana 3000:80

// 그러고 브라우저에서 아래 주소로 접속
http://localhost:3000
```
