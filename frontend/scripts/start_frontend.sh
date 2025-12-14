#!/bin/bash

# 프론트엔드 서버 시작 스크립트

cd "$(dirname "$0")/.."

# node_modules 확인
if [ ! -d "node_modules" ]; then
    echo "의존성 설치 중..."
    npm install
fi

# 서버 시작
echo "프론트엔드 서버 시작 중..."
echo "서버 주소: http://localhost:5173"
echo ""
npm run dev
