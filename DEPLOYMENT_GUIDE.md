# 배포 가이드

## 1. AWS EC2 인스턴스 설정

### 1.1 EC2 인스턴스 생성
1. AWS 콘솔 로그인
2. EC2 대시보드에서 "인스턴스 시작" 클릭
3. 인스턴스 설정:
   - 이름: danggeun-study-app
   - AMI: Ubuntu Server 22.04 LTS
   - 인스턴스 유형: t2.micro (무료 티어)
   - 키 페어: 새로 생성 (이름: danggeun-key)
   - 네트워크 설정: 보안 그룹 생성
     - SSH (포트 22): 내 IP
     - HTTP (포트 80): 모든 IP
     - HTTPS (포트 443): 모든 IP
     - 커스텀 TCP (포트 8501): 모든 IP
4. "인스턴스 시작" 클릭

### 1.2 SSH 접속
```bash
# 키 파일 권한 설정
chmod 400 danggeun-key.pem

# SSH 접속
ssh -i danggeun-key.pem ubuntu@<EC2-PUBLIC-IP>
```

## 2. DockerHub 설정

### 2.1 DockerHub 계정 생성
1. https://hub.docker.com 접속
2. "Sign Up" 클릭하여 계정 생성
3. 이메일 인증 완료

### 2.2 Docker 설치 (EC2 인스턴스)
```bash
# Docker 설치
sudo apt-get update
sudo apt-get install -y docker.io

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
# (변경사항 적용을 위해 재로그인 필요)
```

### 2.3 DockerHub 로그인
```bash
docker login
# DockerHub 사용자명과 비밀번호 입력
```

## 3. 애플리케이션 배포

### 3.1 Docker 이미지 빌드 및 푸시
```bash
# 프로젝트 디렉토리로 이동
cd /path/to/project

# Docker 이미지 빌드
docker build -t <dockerhub-username>/danggeun-study-app:latest .

# DockerHub에 이미지 푸시
docker push <dockerhub-username>/danggeun-study-app:latest
```

### 3.2 EC2에서 애플리케이션 실행
```bash
# Docker 이미지 풀
docker pull <dockerhub-username>/danggeun-study-app:latest

# 컨테이너 실행
docker run -d \
  --name danggeun-app \
  -p 8501:8501 \
  <dockerhub-username>/danggeun-study-app:latest
```

## 4. (선택) 도메인 연결 및 HTTPS 설정

### 4.1 도메인 구매 및 설정
1. Route 53 또는 다른 DNS 서비스에서 도메인 구매
2. 도메인의 A 레코드를 EC2 인스턴스의 퍼블릭 IP로 설정

### 4.2 HTTPS 설정 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt-get update
sudo apt-get install -y certbot

# SSL 인증서 발급
sudo certbot certonly --standalone -d your-domain.com

# Nginx 설치 및 설정
sudo apt-get install -y nginx
sudo nano /etc/nginx/sites-available/danggeun
```

Nginx 설정 예시:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Nginx 설정 활성화
sudo ln -s /etc/nginx/sites-available/danggeun /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. 모니터링 및 유지보수

### 5.1 로그 확인
```bash
# Docker 컨테이너 로그
docker logs danggeun-app

# 실시간 로그 확인
docker logs -f danggeun-app
```

### 5.2 컨테이너 관리
```bash
# 컨테이너 상태 확인
docker ps

# 컨테이너 재시작
docker restart danggeun-app

# 컨테이너 중지
docker stop danggeun-app

# 컨테이너 삭제
docker rm danggeun-app
```

### 5.3 이미지 업데이트
```bash
# 새 버전 배포 시
docker pull <dockerhub-username>/danggeun-study-app:latest
docker stop danggeun-app
docker rm danggeun-app
docker run -d --name danggeun-app -p 8501:8501 <dockerhub-username>/danggeun-study-app:latest
```

## 6. 문제 해결

### 6.1 일반적인 문제
1. 포트 충돌: `netstat -tulpn | grep 8501`로 포트 사용 확인
2. 메모리 부족: `free -h`로 메모리 상태 확인
3. 디스크 공간: `df -h`로 디스크 사용량 확인

### 6.2 로그 확인
```bash
# Docker 로그
docker logs danggeun-app

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 6.3 SSL 인증서 갱신
```bash
# 수동 갱신
sudo certbot renew

# 자동 갱신 설정
sudo crontab -e
# 다음 줄 추가
0 0 1 * * /usr/bin/certbot renew --quiet
``` 