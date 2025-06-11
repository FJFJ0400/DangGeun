# 배포 작업 (사용자 처리)

## 1. AWS EC2 인스턴스 생성 및 SSH 접속
- (1) AWS 콘솔(https://aws.amazon.com)에 로그인 (또는 회원가입) 후 EC2 대시보드에서 "인스턴스 시작" 클릭
- (2) 인스턴스 설정 (예: danggeun-study-app, Ubuntu Server 22.04 LTS, t2.micro(무료 티어), danggeun-key(새 키 페어), 보안 그룹(SSH(22), HTTP(80), HTTPS(443), 커스텀 TCP(8501) 등) 후 "인스턴스 시작" 클릭
- (3) danggeun-key.pem 파일을 로컬에 다운로드 후 (예: C:\Users\YEONGJAE KIM\Desktop\orange) chmod 400 danggeun-key.pem (또는 Windows에서는 파일 속성에서 "읽기"만 허용)으로 권한 설정
- (4) SSH 접속 (예: ssh -i danggeun-key.pem ubuntu@<EC2-PUBLIC-IP>)

## 2. DockerHub 계정 생성 및 로그인 (EC2 인스턴스 내)
- (1) https://hub.docker.com 에서 "Sign Up" 클릭 후 계정 생성 (이메일 인증 완료)
- (2) EC2 인스턴스(SSH 접속 후)에서 Docker 설치 (예: sudo apt-get update; sudo apt-get install -y docker.io; sudo systemctl start docker; sudo systemctl enable docker; sudo usermod -aG docker $USER (재로그인 필요))
- (3) docker login (DockerHub 사용자명 및 비밀번호 입력)

## 3. Docker 이미지 빌드 및 푸시 (EC2 인스턴스 내)
- (1) 프로젝트 코드를 EC2 인스턴스에 업로드 (예: git clone https://github.com/FJFJ0400/DangGeun.git danggeun; cd danggeun)
- (2) Dockerfile, .dockerignore, DEPLOYMENT_GUIDE.md (또는 TECH_STACK_AND_MANUAL.md)가 있는지 확인 후, docker build -t <dockerhub-username>/danggeun-study-app:latest . (예: docker build -t fjfj0400/danggeun-study-app:latest .)로 이미지 빌드
- (3) docker push <dockerhub-username>/danggeun-study-app:latest (예: docker push fjfj0400/danggeun-study-app:latest)로 DockerHub에 이미지 푸시

## 4. EC2 인스턴스에서 Docker 컨테이너 실행 (EC2 인스턴스 내)
- (1) (필요시) docker pull <dockerhub-username>/danggeun-study-app:latest (예: docker pull fjfj0400/danggeun-study-app:latest)로 최신 이미지 풀
- (2) docker run -d --name danggeun-app -p 8501:8501 <dockerhub-username>/danggeun-study-app:latest (예: docker run -d --name danggeun-app -p 8501:8501 fjfj0400/danggeun-study-app:latest)로 컨테이너 실행
- (3) (선택) docker ps, docker logs danggeun-app (또는 docker logs -f danggeun-app)로 컨테이너 상태 및 로그 확인

## 5. (선택) 도메인 연결 및 HTTPS 적용 (EC2 인스턴스 내)
- (1) Route 53 또는 다른 DNS 서비스에서 도메인 구매 후, 도메인의 A 레코드를 EC2 인스턴스의 퍼블릭 IP로 설정
- (2) (예: Let's Encrypt) certbot (sudo apt-get install -y certbot) 설치 후, sudo certbot certonly --standalone -d your-domain.com (예: danggeun-study.com)으로 SSL 인증서 발급
- (3) (예: Nginx) sudo apt-get install -y nginx 후, /etc/nginx/sites-available/danggeun (또는 /etc/nginx/sites-available/default) 파일에 (예: danggeun-study.com) 도메인 및 SSL 인증서 경로(/etc/letsencrypt/live/your-domain.com/fullchain.pem, /etc/letsencrypt/live/your-domain.com/privkey.pem)를 설정 (예: proxy_pass http://localhost:8501; 등) 후, sudo ln -s /etc/nginx/sites-available/danggeun /etc/nginx/sites-enabled/ (또는 sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/) 후, sudo nginx -t 및 sudo systemctl restart nginx

## 6. (선택) 모니터링 및 유지보수 (EC2 인스턴스 내)
- (1) (필요시) docker ps, docker logs danggeun-app, docker restart danggeun-app, docker stop danggeun-app, docker rm danggeun-app 등으로 컨테이너 관리
- (2) (필요시) (예: Let's Encrypt) sudo certbot renew (또는 sudo crontab -e 후 "0 0 1 * * /usr/bin/certbot renew --quiet" 추가)로 SSL 인증서 갱신 