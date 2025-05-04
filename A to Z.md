서버 == 실제 컴퓨터 1대, 가상 서버 1개
노드 == 쿠버네티스가 관리하는 서버 1개
클러스터 == 여러 개의 서버(노드)를 하나로 묶은거임.


- docker
- kuber(kluster)
- scheduling algorithm
- agent?
- ec2, api(flask)
- 시각화 (react)

kluster(성곤) -> scheduling code(원희) -> 실시간 탄소 배출량 api + schduling code == api() 호출 ->api 기반 시각화  

---

- docker desktop 설치 완료.
- kind(kubernetes in docker) 설치
	- 로컬에 쿠버네티스 클러스터 생성을 위해서
	- chocolatey로 간단하게 설치
- kind로 cluster 생성 
	- carbon-cluster 클러스터 생성
	- kubectl 연결 설정 완료
	- kubectl == 생성한 cluster들을 직접 관리하는 도구임.
