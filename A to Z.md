서버 == 실제 컴퓨터 1대, 가상 서버 1개

노드 == 쿠버네티스가 관리하는 서버 1개

클러스터 == 여러 개의 서버(노드)를 하나로 묶은거임.

pod == 하나 이상의 컨테이너를 모아 놓은 것. 쿠버네티스 애플리케이션의 최소 단위임. 


- docker
- kuber(kluster)
- scheduling algorithm
- agent?
- ec2, api(flask)
- 시각화 (react)

kluster(성곤) -> scheduling code(원희) -> 실시간 탄소 배출량 api + schduling code == api() 호출 ->api 기반 시각화  

---
## cluster 구축

- docker desktop 설치 완료.
- kind(kubernetes in docker) 설치
	- 로컬에 쿠버네티스 클러스터 생성을 위해서
	- chocolatey로 간단하게 설치
- kind로 cluster 생성 
	- carbon-cluster 클러스터 생성
	- kubectl 연결 설정 완료
	- kubectl == 생성한 cluster들을 직접 관리하는 도구임.

## carbon - scheduling 알고리즘 적용
- carbon-scheduler.py
- carbon-scheduler-deployment.yaml
- kind-config.yaml
- dockerfile

커스텀 스케줄러 배포까지 완료.

문제상황 : 테스트용 pod를 생성하고 스케줄러가 그 pod를 감지하긴 했는데, pod를 노드에 바인딩하는데 실패했음. 바인딩 api 호출이 실패한듯? 
