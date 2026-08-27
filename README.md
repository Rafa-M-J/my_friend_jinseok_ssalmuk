# 윤진석 네이놈 게섯거라!!

> **오토마우스로 딸깍하고 3만 통나무 모아서 내 친구 진석이 만나러 가자!!!**

`my_friend_jinseok_ssalmuk`은 PySide6 + PyAutoGUI로 만든 Windows용 마우스 자동화 GUI입니다.

- 최대 **5개 딸깍 포인트** 저장
- 포인트별 클릭 후 대기시간 설정
- 사이클 주기 설정
- 선택적 `Ctrl + R` 새로고침
- Start / Pause / Resume / Stop
- 설정 자동 저장 및 불러오기
- 노트북에서도 사용할 수 있도록 세로 스크롤 UI
- 통나무 30,000개 진행도 표시
- 윤가놈식 병맛 문구 및 포켓몬 카드 UI

## 실행

### Windows EXE

GitHub Release에 올라온 `my_friend_jinseok_ssalmuk.exe`를 실행하면 Python 설치 없이 사용할 수 있습니다.

### 소스에서 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python my_friend_jinseok_ssalmuk.py
```

## 이미지 리소스

개발 환경에서 포켓몬 카드를 표시하려면 프로젝트 루트에 `assets/` 폴더를 만들고 아래 파일을 넣습니다.

```text
assets/
├─ kricketot.webp
├─ kricketune.webp
├─ heracross.webp
└─ delibird.webp
```

Windows EXE 빌드 시에는 다음처럼 리소스를 포함할 수 있습니다.

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile `
  --name my_friend_jinseok_ssalmuk `
  --icon "assets\kricketot.ico" `
  --add-data "assets;assets" `
  my_friend_jinseok_ssalmuk.py
```

## 긴급 종료

PyAutoGUI failsafe가 활성화되어 있습니다. 마우스를 **화면 왼쪽 위 모서리**로 빠르게 이동하면 자동화를 중단할 수 있습니다.

## 링크

- 제작자: **밍맹구 + GPT-5.6 Sol**
- GitHub: [Rafa-M-J](https://github.com/Rafa-M-J)
- 진석이 치지직: https://chzzk.naver.com/1ad5aa0f6c6741b072528fad5e5e76b1
- 근가놈 YouTube: https://www.youtube.com/@chzzk_ggn

## 주의

이 프로젝트는 개인적인 재미와 범용 GUI 자동화 실습을 위해 만든 비공식 프로젝트입니다. 자동화 대상 서비스의 이용약관과 운영정책을 확인하고 본인 책임하에 사용하세요.

포켓몬 관련 이미지 및 명칭의 권리는 각 권리자에게 있으며, 이 저장소에는 해당 이미지 파일을 포함하지 않습니다.
