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

- docker desktop 설치 완료.
- kind(kubernetes in docker) 설치
	- 로컬에 쿠버네티스 클러스터 생성을 위해서
	- chocolatey로 간단하게 설치
- kind로 cluster 생성 
	- carbon-cluster 클러스터 생성
	- kubectl 연결 설정 완료
	- kubectl == 생성한 cluster들을 직접 관리하는 도구임.

---
## ec2 서버 위에 시작

ec2 서버 ssh키
```
// 인스턴스 중지 후 재 시작할 때마다 바뀜
인스턴스 -> 연결 -> ssh 클라이언트 -> ssh 키 복사해서 git bash에서 pem키 위치 찾아서 입력해주면 됨.
ex)
ssh -i "visualization.pem" ubuntu@ec2-12-345-67-89.ap-northeast-2.compute.amazonaws.com
```

### 1단계 : ec2 서버 환경 세팅

// 시스템 패키지 업데이트
```
sudo apt update && sudo apt upgrade -y
```

// Docker 설치
```
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
```

// 권한 부여(현재 사용자가 uubntu일 경우)
```
sudo usermod -aG docker $USER
```

이제 exit로 나갔다가 다시 ec2 서버 접속하면 docker 권한 적용되어 있음.

// k3s(경량 쿠버네티스) 설치
```
curl -sfL https://get.k3s.io | sh -
```

// kubectl 연결 설정
```
sudo mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown ubuntu:ubuntu ~/.kube/config
```
// 여기서 한 번 막혔음.
좋아요. 현재 문제가 되는 포인트는 `kubectl`이 여전히 **`/etc/rancher/k3s/k3s.yaml`** 파일을 참조하고 있다는 점입니다.  
하지만 우리는 이미 해당 파일을 `~/.kube/config`로 복사해 두었기 때문에, kubectl이 이 경로를 **기본 경로**로 인식하도록 환경변수를 설정해줘야 합니다.

// 환경 변수 설정
```
export KUBECONFIG=$HOME/.kube/config
```



// 잘 됐는지 확인
```
kubectl get nodes
// 아래 같은 결과가 나와야함.
NAME              STATUS   ROLES                  AGE     VERSION
ip-172-31-47-96   Ready    control-plane,master   6m52s   v1.32.4+k3s1
```

// 환경 변수 설정 영구 적용

```
echo 'export KUBECONFIG=$HOME/.kube/config' >> ~/.bashrc
source ~/.bashrc
```

### 2 스케줄링 알고리즘 

// 로컬에 있는 zip 파일을 ec2로 전송
```
scp -i ~/Desktop/carbon_ubuntu.pem ~/Desktop/carbon.zip ubuntu@52.79.236.222:~/
```

// ec2 서버에서 jungwongee파일 압축 해제
```
unzip "carbon.zip" -d carbon-scheduler
이거 안되면
unzip "/home/ubuntu/carbon.zip" -d carbon-scheduler
```

// 압축 해제 후 carbon_scheduler.py 파일로 접근
```
cd carbon-scheduler
ls
cd ./--JungWonHee
ls
```

// python, kubernetes 설치 ~  실행
```
ls
pip3 install -r requirements.txt
pip3 install kubernetes requests

// .local/bin을 path에 추가하기
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

python3 carbon_scheduler.py
```

그러면 pod 생성 되었다는 메세지 뜸.

// pod가 잘 생성 되었는지 확인
```
kubectl get pods

// 결과 화면이 아래처럼 나와야 함.
NAME        READY   STATUS    RESTARTS   AGE
task-5350   1/1     Running   0          6m3s
```

### 3 시각화

// 로컬에 있는 flask, react를 ec2 서버로 전송
```
// 코드 형식
scp -i [pem키 위치]~/Desktop/visualization.pem [zip 파일 위치]~/Desktop/carbon_back.zip ubuntu@[ec2 퍼블릭 ip]12.345.67.89:~/

scp -i ~/Desktop/visualization.pem ~/Desktop/carbon_back.zip ubuntu@[ec2 퍼블릭 ip]:~/

scp -i ~/Desktop/visualization.pem ~/Desktop/visualization.zip ubuntu@[ec2 퍼블릭 ip]:~/
```

// ec2 서버에서 압축 해제
```
unzip "carbon_back.zip" -d carbon-back
unzip "visualization.zip" -d visualization
```

// flask 실행을 위해 가상환경 생성
```
sudo apt update
sudo apt install python3.10-venv

// 가상 환경 생성
python3 -m venv venv

// 가상 환경 활성화(다음 부터는 바로 이거 하고 python app.py 하면 됨)
source venv/bin/activate
```

// requirement.txt 생성 후 app.py 실행
```
echo -e "Flask\nflask-cors" > requirements.txt
pip install -r requirements.txt
python app.py
```

// react
```
cd ~/visualization/carbon-dashboard
npm install
npm run dev
```

// vite 권한 문제 발생
```
// 권한 확인 및 수정
chmod +x node_modules/.bin/vite

// 그래도 안되면.. node_modules 삭제 후 재설치
rm -rf node_modules

// 다시 실행
npm install
npm run dev
```

// node.js 버전 업그레이드 해야됨
```
// 최소 14~16 이상이 필요함
node -v

// 18 이상으로 업그레이드
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

--- // 충돌 있을 때만
// 충돌 있으면 걍 강제로 덮어버리는게 빠르더라
sudo dpkg -i --force-overwrite /var/cache/apt/archives/nodejs_18.20.8-1nodesource1_amd64.deb

// 의존성 깨진 부분 정리
sudo apt -f install
---

// 업그레이드 확인
node -v
npm -v

// 다시 react 의존성 설치
cd ~/visualization/carbon-dashboard
rm -rf node_modules
npm install

// 실행(-- --host 이거는 ec2 외부 ip에서 접속 가능하게 해줌)
npm run dev -- --host

// http://[ec2 퍼블릭 ip]:5173 으로 접속하면 됨.
```

// axios 설정(vite.config.js)
```
// react의 axios 설정을 해줘야 함.
// vite.config.js에 프록시 설정을 해줄거임

import { defineConfig } from 'vite'

import react from '@vitejs/plugin-react'

export default defineConfig({

  plugins: [react()],

  server: {

    proxy: {

      // React 개발 서버에서 "/api"로 들어오는 요청은

      // Flask 서버(EC2의 IP)로 프록시한다.

      '/api': {

        target: 'http://[ec2 프라이빗 ip]:5000', // EC2 내부(프라이빗) IP

        changeOrigin: true,

        secure: false,

      },

    },

  },

})
```

// axios 설정(api.js)
```
// 개발하기 편하라고 base_api 를 상수값으로 local:5000 지정했을 거임.
// 상수 지정 지우고, 그냥 상대 경로로 다 지정해주면 됨.
// src/services/api.js
import axios from 'axios';

export const fetchCarbonData = async () => {
  const res = await axios.get('/api/carbon'); // ✅ 이렇게 절대 상대 경로!
  return res.data;
};

export const fetchJobData = async () => {
  const res = await axios.get('/api/jobs');
  return res.data;
};

export const fetchClusterLoad = async () => {
  const res = await axios.get('/api/cluster-load');
  return res.data;
};

export const fetchScheduleData = async () => {
  const res = await axios.get('/api/schedule');
  return res.data;
};

```
