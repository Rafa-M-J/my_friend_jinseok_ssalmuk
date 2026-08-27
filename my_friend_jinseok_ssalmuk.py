import sys
import json
import time
import random
import os
from pathlib import Path

import pyautogui

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QLineEdit,
    QProgressBar,
    QScrollArea,
)


# ============================================================
# App
# ============================================================

APP_NAME = "my_friend_jinseok_ssalmuk"
MAX_POINTS = 5

GITHUB_URL = "https://github.com/Rafa-M-J"
CHZZK_URL = "https://chzzk.naver.com/1ad5aa0f6c6741b072528fad5e5e76b1"
YOUTUBE_URL = "https://www.youtube.com/@chzzk_ggn"

# ------------------------------------------------------------
# 배포용 경로
# ------------------------------------------------------------
# PyInstaller --onefile에서는 리소스가 임시 폴더(sys._MEIPASS)에 풀린다.
# 일반 .py 실행에서는 현재 스크립트가 있는 폴더를 기준으로 assets를 찾는다.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    RESOURCE_DIR = Path(sys._MEIPASS)
else:
    RESOURCE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = RESOURCE_DIR / "assets"

# 설정 파일은 exe 옆이 아니라 사용자 AppData에 저장한다.
# Program Files 등 쓰기 권한이 제한된 위치에서도 정상 동작하도록 하기 위함.
APPDATA_ROOT = Path(
    os.getenv("APPDATA")
    or os.getenv("LOCALAPPDATA")
    or (Path.home() / ".my_friend_jinseok_ssalmuk")
)

APP_DATA_DIR = APPDATA_ROOT / APP_NAME
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = APP_DATA_DIR / "my_friend_jinseok_ssalmuk_config.json"

# 이전 개발 버전 설정 파일 자동 마이그레이션용
LEGACY_CONFIG_FILES = [
    Path.cwd() / "my_friend_jinseok_ssalmuk_config.json",
    Path.cwd() / "config.json",
    Path(__file__).resolve().parent / "my_friend_jinseok_ssalmuk_config.json",
    Path(__file__).resolve().parent / "config.json",
]

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

LOGS_PER_CYCLE = 100
LOG_GOAL = 30_000

MEME_LINES = [
    '내가 왜 니 친구야',
    '공업용 우정. 공업용 딸깍. 공업용 통나무.',
    '에넬은 대장급이 맞음',
    '대단합니다. 동의합니다.',
    '사랑해 진석아. 너의 둥근 안경이 좋아.',
    '아 감사합니다. 정말 진짜 2월달에 여자친구랑 헤어지고 할 게 없어 가지고.',
]

CLICK_LINES = [
    "{name} 딸깍. 대단합니다. 동의합니다.",
    "{name} 딸깍. 내가 왜 니 친구야.",
    "{name} 딸깍. 에넬은 대장급이 맞음.",
    "{name} 딸깍. 아니 근데 진짜로.",
    "{name} 딸깍. 사랑해 진석아.",
    "{name} 딸깍. 사람 아니야.",
]

CYCLE_DONE_LINES = [
    "{cycle}회차 완료. 대단합니다. 동의합니다.",
    "{cycle}회차 완료. 윤진석 네이놈 게섯거라.",
    "{cycle}회차 완료. 내 친구 진석이에게 한 발짝 더.",
    "{cycle}회차 완료. 에넬은 대장급이 맞음.",
    "{cycle}회차 완료. 사랑해 진석아. 너의 둥근 안경이 좋아.",
    "{cycle}회차 완료. 아니 근데 진짜로.",
    "{cycle}회차 완료. 이게 맞나?",
    "{cycle}회차 완료. 내가 왜 니 친구야.",
]


# ============================================================
# Main Window
# ============================================================

class MyFriendJinseokSsalmukWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("윤진석 네이놈 게섯거라!!")
        self.resize(820, 700)

        # ----------------------------------------------------
        # Point data
        # ----------------------------------------------------

        self.points = [None] * MAX_POINTS

        # 좌표 캡처
        self.capture_index = None
        self.capture_countdown = 0

        # 자동화 상태
        self.running = False
        self.paused = False
        self.cycle_number = 0

        # 현재 사이클에 실제 사용할 Point
        self.active_points = []
        self.current_point_index = 0

        # scheduler
        self.pending_callback = None
        self.deadline = None
        self.remaining_ms = 0

        # ====================================================
        # Main widget
        # ====================================================

        # 노트북 해상도에서도 전체 UI가 잘리지 않도록
        # 메인 화면 전체를 세로 스크롤 영역으로 감싼다.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.setCentralWidget(scroll)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(16, 14, 16, 16)
        self.main_layout.setSpacing(10)

        self.setStyleSheet("""
            QMainWindow { background: #f7f7f5; }
            QWidget { font-size: 13px; }
            QGroupBox {
                font-weight: 700;
                border: 1px solid #b8b8b8;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                background: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }
            QPushButton {
                min-height: 30px;
                border: 1px solid #cfcfcf;
                border-radius: 7px;
                background: #ffffff;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background: #fff4b8;
                border: 1px solid #d4b52c;
            }
            QPushButton:pressed { background: #f6df70; }
            QPushButton:disabled {
                color: #9b9b9b;
                background: #f3f3f3;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                min-height: 27px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background: #ffffff;
                padding: 1px 6px;
            }
            QProgressBar {
                border: 1px solid #bdbdbd;
                border-radius: 7px;
                background: #eeeeee;
                text-align: center;
                min-height: 20px;
                font-weight: 700;
            }
            QProgressBar::chunk {
                background: #f2d34f;
                border-radius: 6px;
            }
        """)

        # ====================================================
        # Header
        # ====================================================

        title = QLabel("윤진석 네이놈 게섯거라!!")

        title.setStyleSheet("""
            font-size: 30px;
            font-weight: 900;
        """)

        subtitle = QLabel(
            "오토마우스로 치지직 포인트 쌀먹하고 3만 통나무 모아서 "
            "내 친구 진석이 만나러 가자!!!"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 2px;
        """)

        friend_banner = QLabel(
            '“내가 왜 니 친구야?”  →  응. 통나무 30,000개 들고 직접 확인하러 감.'
        )
        friend_banner.setWordWrap(True)
        friend_banner.setStyleSheet("""
            background: #fff4b8;
            border: 1px solid #e0c653;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: 700;
            margin-top: 5px;
        """)

        warning_label = QLabel(
            "※ 본 프로그램은 내 친구 진석이를 만나기 위해 3만 통나무를 수급하려는 "
            "놈붕이의 처절한 공업용 우정 프로젝트입니다."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            color: #777;
            font-size: 12px;
            margin-bottom: 8px;
        """)

        self.meme_label = QLabel(random.choice(MEME_LINES))
        self.meme_label.setWordWrap(True)
        self.meme_label.setStyleSheet("""
            color: #555;
            font-size: 12px;
            font-style: italic;
            padding: 2px 1px 4px 1px;
        """)

        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        self.main_layout.addWidget(friend_banner)
        self.main_layout.addWidget(warning_label)
        self.main_layout.addWidget(self.meme_label)

        # ====================================================
        # Cycle Settings
        # ====================================================

        self.cycle_group = QGroupBox("공업용 통나무 수급기")
        cycle_layout = QVBoxLayout(self.cycle_group)

        # Cycle wait
        cycle_wait_row = QHBoxLayout()
        cycle_wait_row.addWidget(QLabel("통나무 타이밍"))

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 999)
        self.minutes_spin.setValue(60)

        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setValue(30)

        cycle_wait_row.addWidget(self.minutes_spin)
        cycle_wait_row.addWidget(QLabel("분"))
        cycle_wait_row.addWidget(self.seconds_spin)
        cycle_wait_row.addWidget(QLabel("초"))
        cycle_wait_row.addStretch()

        cycle_layout.addLayout(cycle_wait_row)

        # Refresh
        refresh_row = QHBoxLayout()

        self.refresh_checkbox = QCheckBox("공업용 Ctrl + R 발사")
        self.refresh_checkbox.setChecked(True)

        refresh_row.addWidget(self.refresh_checkbox)
        refresh_row.addSpacing(20)
        refresh_row.addWidget(QLabel("새로고침 후 공업용 존버"))

        self.refresh_wait_spin = QDoubleSpinBox()
        self.refresh_wait_spin.setRange(0, 300)
        self.refresh_wait_spin.setDecimals(1)
        self.refresh_wait_spin.setSingleStep(0.5)
        self.refresh_wait_spin.setValue(5)
        self.refresh_wait_spin.setSuffix(" 초")

        refresh_row.addWidget(self.refresh_wait_spin)
        refresh_row.addStretch()

        cycle_layout.addLayout(refresh_row)
        self.main_layout.addWidget(self.cycle_group)

        # ====================================================
        # Click Points
        # ====================================================

        self.point_group = QGroupBox("딸깍 포인트")
        point_layout = QVBoxLayout(self.point_group)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("사용"))
        header_row.addWidget(QLabel("이름"))
        header_row.addWidget(QLabel("딸깍 좌표"))
        header_row.addWidget(QLabel("딸깍 후 존버"))
        header_row.addWidget(QLabel(""))
        point_layout.addLayout(header_row)

        self.enabled_checkboxes = []
        self.name_edits = []
        self.point_labels = []
        self.delay_spins = []
        self.capture_buttons = []
        self.point_rows = []

        for i in range(MAX_POINTS):

            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(4, 3, 4, 3)

            enabled = QCheckBox()
            enabled.setChecked(i < 3)

            name_edit = QLineEdit(f"Point {i + 1}")
            name_edit.setFixedWidth(120)

            coord_label = QLabel("X: ----   Y: ----")
            coord_label.setFixedWidth(180)

            delay_spin = QDoubleSpinBox()
            delay_spin.setRange(0, 300)
            delay_spin.setDecimals(1)
            delay_spin.setSingleStep(0.5)
            delay_spin.setValue(1.0)
            delay_spin.setSuffix(" 초")
            delay_spin.setFixedWidth(100)

            capture_button = QPushButton("좌표 박아두기")
            capture_button.setFixedWidth(140)
            capture_button.clicked.connect(
                lambda checked=False, index=i: self.start_capture(index)
            )

            row.addWidget(enabled)
            row.addWidget(name_edit)
            row.addWidget(coord_label)
            row.addWidget(delay_spin)
            row.addWidget(capture_button)

            point_layout.addWidget(row_widget)

            self.point_rows.append(row_widget)
            self.enabled_checkboxes.append(enabled)
            self.name_edits.append(name_edit)
            self.point_labels.append(coord_label)
            self.delay_spins.append(delay_spin)
            self.capture_buttons.append(capture_button)

        self.main_layout.addWidget(self.point_group)

        # ====================================================
        # Config
        # ====================================================

        config_row = QHBoxLayout()

        self.save_button = QPushButton("세팅 봉인")
        self.load_button = QPushButton("세팅 소환")

        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)

        config_row.addWidget(self.save_button)
        config_row.addWidget(self.load_button)
        config_row.addStretch()

        self.main_layout.addLayout(config_row)

        # ====================================================
        # Controls
        # ====================================================

        control_group = QGroupBox("내 친구 진석 챌린지")
        control_layout = QVBoxLayout(control_group)

        button_row = QHBoxLayout()

        self.start_button = QPushButton("▶  공업용 쌀먹 개시")
        self.pause_button = QPushButton("⏸  오늘만 친구하지 말자")
        self.stop_button = QPushButton("■  리트라이 종료")

        for button in (
            self.start_button,
            self.pause_button,
            self.stop_button,
        ):
            button.setMinimumHeight(42)

        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_automation)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.stop_button.clicked.connect(self.stop_automation)

        button_row.addWidget(self.start_button)
        button_row.addWidget(self.pause_button)
        button_row.addWidget(self.stop_button)

        control_layout.addLayout(button_row)

        self.countdown_label = QLabel("다음 공업용 딸깍까지: --:--")
        self.countdown_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 800;
        """)

        self.cycle_label = QLabel("누적 리트라이 성공: 0회")
        self.logs_label = QLabel(f"이번 세션 추정 통나무: 0 / {LOG_GOAL:,}개")

        self.logs_progress = QProgressBar()
        self.logs_progress.setRange(0, LOG_GOAL)
        self.logs_progress.setValue(0)
        self.logs_progress.setFormat(
            f"진석이 만나기 진행도  %p%   (0 / {LOG_GOAL:,})"
        )

        self.status_label = QLabel("대기 중: 사람 아니야... 그냥 프로그램이야.")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-weight: 700; margin-top: 3px;")

        control_layout.addWidget(self.countdown_label)
        control_layout.addWidget(self.cycle_label)
        control_layout.addWidget(self.logs_label)
        control_layout.addWidget(self.logs_progress)
        control_layout.addWidget(self.status_label)

        self.main_layout.addWidget(control_group)


        # ====================================================
        # Pokemon Friend Gallery
        # ====================================================

        pokemon_group = QGroupBox("윤가놈 인맥 도감")
        pokemon_layout = QHBoxLayout(pokemon_group)

        pokemon_layout.addWidget(
            self.create_pokemon_card(
                "kricketot.webp",
                "병1신",
                "윤가놈 인맥 도감 1번. 시작부터 심상치 않은 병1신 카드."
            )
        )

        pokemon_layout.addWidget(
            self.create_pokemon_card(
                "kricketune.webp",
                "병1신(진화체)",
                "카무사리 원툴련."
            )
        )

        pokemon_layout.addWidget(
            self.create_pokemon_card(
                "heracross.webp",
                "동덕이",
                "니로우한테 날개치기 맞고 싶다 헤으응."
            )
        )

        pokemon_layout.addWidget(
            self.create_pokemon_card(
                "delibird.webp",
                "노목이",
                "꼭두에게 프레젠트를."
            )
        )

        self.main_layout.addWidget(pokemon_group)

        # ====================================================
        # Footer / Links
        # ====================================================

        mission_footer = QLabel(
            "🎯 최종 목표: 통나무 30,000개 → ‘내가 왜 니 친구야?’ 직접 들으러 가기"
        )
        mission_footer.setAlignment(Qt.AlignCenter)
        mission_footer.setStyleSheet("""
            font-size: 13px;
            font-weight: 700;
            margin-top: 6px;
        """)

        footer = QLabel(
            f'제작자: <b>밍맹구와 GPT-5.6 Sol</b>  ·  '
            f'<a href="{GITHUB_URL}">GitHub: Rafa-M-J</a>'
            f'  ·  '
            f'<a href="{CHZZK_URL}">📺 내 친구 진석이 치지직</a>'
            f'  ·  '
            f'<a href="{YOUTUBE_URL}">▶ 근가놈 YouTube</a>'
        )
        footer.setOpenExternalLinks(True)
        footer.setTextInteractionFlags(Qt.TextBrowserInteraction)
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #777;
            font-size: 12px;
            margin-top: 2px;
        """)

        self.main_layout.addWidget(mission_footer)
        self.main_layout.addWidget(footer)

        # ====================================================
        # Timers
        # ====================================================

        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.capture_countdown_tick)

        self.action_timer = QTimer()
        self.action_timer.setSingleShot(True)
        self.action_timer.timeout.connect(self.execute_pending_action)

        self.display_timer = QTimer()
        self.display_timer.setInterval(200)
        self.display_timer.timeout.connect(self.update_countdown_display)

        self.meme_timer = QTimer()
        self.meme_timer.setInterval(15000)
        self.meme_timer.timeout.connect(self.rotate_meme)
        self.meme_timer.start()

        # ====================================================
        # Auto-load
        # ====================================================

        if CONFIG_FILE.exists():
            self.load_settings(show_message=False)

        else:
            # 기존 프로젝트 폴더의 설정을 발견하면 한 번 불러온 뒤
            # 새 AppData 위치에 자동 저장해서 마이그레이션한다.
            for legacy_file in LEGACY_CONFIG_FILES:
                if legacy_file.exists():
                    self.load_settings(
                        show_message=False,
                        file_path=legacy_file
                    )
                    self.save_settings(show_message=False)
                    break

    # ========================================================
    # Meme rotation
    # ========================================================

    def rotate_meme(self):
        self.meme_label.setText(random.choice(MEME_LINES))

    # ========================================================
    # Capture Position
    # ========================================================

    def start_capture(self, index):

        if self.running:
            return

        if self.capture_timer.isActive():
            return

        self.capture_index = index
        self.capture_countdown = 5

        name = self.name_edits[index].text().strip()
        if not name:
            name = f"Point {index + 1}"

        self.status_label.setText(
            f"{name}: 5초 안에 마우스를 공업용 딸깍 위치로 옮기셈 "
            f"({self.capture_countdown}초)"
        )

        self.capture_buttons[index].setEnabled(False)
        self.capture_timer.start(1000)

    def capture_countdown_tick(self):

        self.capture_countdown -= 1

        index = self.capture_index

        name = self.name_edits[index].text().strip()
        if not name:
            name = f"Point {index + 1}"

        if self.capture_countdown > 0:

            self.status_label.setText(
                f"{name}: 좌표 조준 중... 귀뚤톡크처럼 침착하게 "
                f"({self.capture_countdown}초)"
            )
            return

        self.capture_timer.stop()

        pos = pyautogui.position()

        self.points[index] = [pos.x, pos.y]

        self.point_labels[index].setText(
            f"X: {pos.x}   Y: {pos.y}"
        )

        self.capture_buttons[index].setEnabled(True)

        self.status_label.setText(
            f"{name} 좌표 저장됨. 대단합니다. 동의합니다."
        )

        self.capture_index = None

    # ========================================================
    # Save Config
    # ========================================================

    def save_settings(self, show_message=True):

        config = {
            "app": APP_NAME,
            "cycle_minutes": self.minutes_spin.value(),
            "cycle_seconds": self.seconds_spin.value(),
            "refresh_enabled": self.refresh_checkbox.isChecked(),
            "refresh_wait": self.refresh_wait_spin.value(),
            "points": []
        }

        for i in range(MAX_POINTS):

            config["points"].append({
                "enabled": self.enabled_checkboxes[i].isChecked(),
                "name": self.name_edits[i].text(),
                "position": self.points[i],
                "delay_after": self.delay_spins[i].value()
            })

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )

        self.status_label.setText("세팅 봉인 완료. 다음 리트라이에도 그대로 간다.")

        if show_message:
            QMessageBox.information(
                self,
                "더나이스",
                "세팅 봉인 완료.\n윤진석 네이놈 게섯거라."
            )

    # ========================================================
    # Load Config
    # ========================================================

    def load_settings(
        self,
        show_message=True,
        file_path=None
    ):

        if file_path is None:
            file_path = CONFIG_FILE

        if not file_path.exists():

            QMessageBox.warning(
                self,
                APP_NAME,
                "저장된 설정 파일이 없습니다."
            )

            return

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                config = json.load(f)

            self.minutes_spin.setValue(
                config.get("cycle_minutes", 60)
            )

            self.seconds_spin.setValue(
                config.get("cycle_seconds", 30)
            )

            self.refresh_checkbox.setChecked(
                config.get("refresh_enabled", True)
            )

            self.refresh_wait_spin.setValue(
                config.get("refresh_wait", 5)
            )

            legacy_click_delay = config.get(
                "click_delay",
                1
            )

            saved_points = config.get(
                "points",
                []
            )

            for i in range(MAX_POINTS):

                if i >= len(saved_points):

                    self.enabled_checkboxes[i].setChecked(False)
                    self.name_edits[i].setText(f"Point {i + 1}")
                    self.points[i] = None
                    self.delay_spins[i].setValue(legacy_click_delay)
                    self.point_labels[i].setText(
                        "X: ----   Y: ----"
                    )
                    continue

                data = saved_points[i]

                self.enabled_checkboxes[i].setChecked(
                    data.get("enabled", False)
                )

                self.name_edits[i].setText(
                    data.get("name", f"Point {i + 1}")
                )

                position = data.get("position", None)
                self.points[i] = position

                self.delay_spins[i].setValue(
                    data.get(
                        "delay_after",
                        legacy_click_delay
                    )
                )

                if position is not None:

                    x, y = position

                    self.point_labels[i].setText(
                        f"X: {x}   Y: {y}"
                    )

                else:

                    self.point_labels[i].setText(
                        "X: ----   Y: ----"
                    )

            self.status_label.setText("세팅 소환 완료. 더나이스.")

            if show_message:

                QMessageBox.information(
                    self,
                    "더나이스",
                    "세팅 소환 완료.\n공업용 우정 재개 가능."
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                APP_NAME,
                f"설정 불러오기 실패:\n{e}"
            )

    # ========================================================
    # Get Active Points
    # ========================================================

    def get_enabled_points(self):

        active = []

        for i in range(MAX_POINTS):

            if not self.enabled_checkboxes[i].isChecked():
                continue

            position = self.points[i]

            if position is None:

                raise ValueError(
                    f"Point {i + 1}이 활성화되어 있지만 "
                    f"좌표가 없습니다."
                )

            name = self.name_edits[i].text().strip()

            if not name:
                name = f"Point {i + 1}"

            active.append({
                "index": i,
                "name": name,
                "position": position,
                "delay_after": self.delay_spins[i].value()
            })

        if not active:
            raise ValueError("활성화된 Point가 없습니다.")

        return active

    # ========================================================
    # Start
    # ========================================================

    def start_automation(self):

        if self.running:
            return

        try:
            self.active_points = self.get_enabled_points()

        except ValueError as e:

            QMessageBox.warning(
                self,
                APP_NAME,
                str(e)
            )

            return

        cycle_seconds = (
            self.minutes_spin.value() * 60
            +
            self.seconds_spin.value()
        )

        if cycle_seconds <= 0:

            QMessageBox.warning(
                self,
                APP_NAME,
                "수급 주기는 최소 1초 이상이어야 합니다."
            )

            return

        self.running = True
        self.paused = False
        self.cycle_number = 0

        self.update_log_progress()

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        self.pause_button.setText(
            "⏸  오늘만 친구하지 말자"
        )

        self.set_settings_enabled(False)

        self.status_label.setText(
            "간다 진석아."
        )
        self.meme_label.setText("더나이스. 챌린지 시작.")

        self.display_timer.start()

        self.schedule_cycle_wait()

    # ========================================================
    # Cycle Wait
    # ========================================================

    def schedule_cycle_wait(self):

        if not self.running:
            return

        seconds = (
            self.minutes_spin.value() * 60
            +
            self.seconds_spin.value()
        )

        self.clear_point_highlight()

        self.status_label.setText(
            f"{self.cycle_number + 1}회차까지 존버."
        )

        self.schedule_action(
            seconds * 1000,
            self.begin_cycle
        )

    # ========================================================
    # Begin Cycle
    # ========================================================

    def begin_cycle(self):

        if not self.running:
            return

        try:
            self.active_points = self.get_enabled_points()

        except ValueError as e:

            self.stop_automation()

            QMessageBox.warning(
                self,
                APP_NAME,
                str(e)
            )

            return

        self.current_point_index = 0

        cycle_display = self.cycle_number + 1

        self.status_label.setText(
            f"{cycle_display}회차 공업용 수급 개시."
        )

        if self.refresh_checkbox.isChecked():

            try:
                pyautogui.hotkey(
                    "ctrl",
                    "r"
                )

            except pyautogui.FailSafeException:

                self.handle_failsafe()
                return

            wait_ms = int(
                self.refresh_wait_spin.value()
                * 1000
            )

            self.status_label.setText(
                f"{cycle_display}회차: 공업용 Ctrl+R 발사 완료 → 존버 중."
            )

            self.schedule_action(
                wait_ms,
                self.click_next_point
            )

        else:

            self.click_next_point()

    # ========================================================
    # Click
    # ========================================================

    def click_next_point(self):

        if not self.running:
            return

        if self.current_point_index >= len(
            self.active_points
        ):

            self.finish_cycle()
            return

        point = self.active_points[
            self.current_point_index
        ]

        index = point["index"]
        name = point["name"]

        x, y = point["position"]

        self.highlight_point(index)

        try:

            pyautogui.click(
                x=x,
                y=y,
                clicks=1
            )

        except pyautogui.FailSafeException:

            self.handle_failsafe()
            return

        self.status_label.setText(
            random.choice(CLICK_LINES).format(name=name) + f"  ({x}, {y})"
        )

        self.current_point_index += 1

        if self.current_point_index >= len(
            self.active_points
        ):

            self.finish_cycle()
            return

        delay_ms = int(
            point["delay_after"]
            * 1000
        )

        self.schedule_action(
            delay_ms,
            self.click_next_point
        )

    # ========================================================
    # Finish Cycle
    # ========================================================

    def finish_cycle(self):

        if not self.running:
            return

        self.clear_point_highlight()

        self.cycle_number += 1

        self.update_log_progress()

        self.status_label.setText(
            random.choice(CYCLE_DONE_LINES).format(cycle=self.cycle_number)
        )
        self.meme_label.setText(random.choice(MEME_LINES))

        self.schedule_cycle_wait()

    # ========================================================
    # Progress
    # ========================================================

    def update_log_progress(self):
        estimated_logs = min(self.cycle_number * LOGS_PER_CYCLE, LOG_GOAL)

        self.cycle_label.setText(
            f"누적 리트라이 성공: {self.cycle_number}회"
        )
        self.logs_label.setText(
            f"이번 세션 추정 통나무: {estimated_logs:,} / {LOG_GOAL:,}개"
        )
        self.logs_progress.setValue(estimated_logs)
        self.logs_progress.setFormat(
            f"진석이 만나기 진행도  %p%   ({estimated_logs:,} / {LOG_GOAL:,})"
        )

    # ========================================================
    # Point Highlight
    # ========================================================

    def clear_point_highlight(self):

        for row in self.point_rows:
            row.setStyleSheet("")

    def highlight_point(self, index):

        self.clear_point_highlight()

        self.point_rows[index].setStyleSheet("""
            QWidget {
                font-weight: 800;
                background: #fff4b8;
                border-radius: 6px;
            }
        """)

    # ========================================================
    # Scheduler
    # ========================================================

    def schedule_action(
        self,
        milliseconds,
        callback
    ):

        if not self.running:
            return

        milliseconds = max(
            0,
            int(milliseconds)
        )

        self.pending_callback = callback
        self.remaining_ms = milliseconds

        self.deadline = (
            time.monotonic()
            +
            milliseconds / 1000
        )

        self.action_timer.start(milliseconds)

    def execute_pending_action(self):

        if not self.running:
            return

        if self.paused:
            return

        callback = self.pending_callback

        self.pending_callback = None
        self.deadline = None
        self.remaining_ms = 0

        if callback is not None:
            callback()

    # ========================================================
    # Pause / Resume
    # ========================================================

    def toggle_pause(self):

        if not self.running:
            return

        if not self.paused:

            self.paused = True

            if self.action_timer.isActive():

                remaining = (
                    self.deadline
                    -
                    time.monotonic()
                )

                self.remaining_ms = max(
                    0,
                    int(remaining * 1000)
                )

                self.action_timer.stop()

            self.pause_button.setText(
                "▶  친구 관계 재개"
            )

            self.status_label.setText(
                "오늘만 친구하지 말자."
            )
            self.meme_label.setText(
                '“내가 왜 니 친구야?” — 잠깐만. 지금은 쉬는 중.'
            )

        else:

            self.paused = False

            self.pause_button.setText(
                "⏸  오늘만 친구하지 말자"
            )

            if self.pending_callback is not None:

                self.deadline = (
                    time.monotonic()
                    +
                    self.remaining_ms / 1000
                )

                self.action_timer.start(
                    self.remaining_ms
                )

            self.status_label.setText(
                "다시 친구하자."
            )
            self.meme_label.setText("더나이스. 다시 간다.")

    # ========================================================
    # Stop
    # ========================================================

    def stop_automation(self):

        if not self.running:
            return

        self.running = False
        self.paused = False

        self.action_timer.stop()
        self.display_timer.stop()

        self.pending_callback = None
        self.deadline = None
        self.remaining_ms = 0

        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.pause_button.setText(
            "⏸  오늘만 친구하지 말자"
        )

        self.set_settings_enabled(True)
        self.clear_point_highlight()

        self.countdown_label.setText(
            "다음 공업용 딸깍까지: --:--"
        )

        self.status_label.setText(
            "진석아 오늘은 여기까지다."
        )
        self.meme_label.setText(random.choice(MEME_LINES))

    # ========================================================
    # FailSafe
    # ========================================================

    def handle_failsafe(self):

        self.stop_automation()

        QMessageBox.warning(
            self,
            "공업용 탈출기 발동",
            "마우스를 화면 왼쪽 위 구석으로 옮겨 긴급 중지가 발동함.\n"
            "귀뚤톡크도 도망갈 때는 도망간다. 자동화 종료."
        )

    # ========================================================
    # Countdown
    # ========================================================

    def update_countdown_display(self):

        if not self.running:

            self.countdown_label.setText(
                "다음 공업용 딸깍까지: --:--"
            )

            return

        if self.paused:

            seconds = (
                self.remaining_ms / 1000
            )

        elif self.deadline is not None:

            seconds = max(
                0,
                self.deadline
                -
                time.monotonic()
            )

        else:

            self.countdown_label.setText(
                "다음 공업용 딸깍까지: 지금 딸깍 중..."
            )

            return

        total_seconds = int(
            seconds + 0.999
        )

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        secs = total_seconds % 60

        if hours > 0:

            text = (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{secs:02d}"
            )

        else:

            text = (
                f"{minutes:02d}:"
                f"{secs:02d}"
            )

        self.countdown_label.setText(
            f"다음 공업용 딸깍까지: {text}"
        )

    # ========================================================
    # Enable Settings
    # ========================================================

    def set_settings_enabled(
        self,
        enabled
    ):

        self.cycle_group.setEnabled(enabled)
        self.point_group.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.load_button.setEnabled(enabled)


    # ========================================================
    # Pokemon Friend Cards
    # ========================================================

    def create_pokemon_card(self, image_name, nickname, subtext):
        card = QGroupBox(nickname)
        card_layout = QVBoxLayout(card)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setMinimumHeight(120)
        image_label.setStyleSheet("""
            border: 1px dashed #c8c8c8;
            border-radius: 8px;
            background: #fafafa;
            padding: 6px;
        """)

        image_path = ASSETS_DIR / image_name

        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    120, 120,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_label.setPixmap(pixmap)
            else:
                image_label.setText(f"이미지 로드 실패\n{image_name}")
        else:
            image_label.setText(
                f"이미지 없음\n{image_name}\n\n"
                f"assets/{image_name} 리소스를 찾지 못했습니다."
            )

        desc_label = QLabel(subtext)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #555;
            padding-top: 4px;
        """)

        card_layout.addWidget(image_label)
        card_layout.addWidget(desc_label)
        return card

    # ========================================================
    # Close
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        if self.running:
            self.stop_automation()

        event.accept()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)

    window = MyFriendJinseokSsalmukWindow()
    window.show()

    sys.exit(app.exec())
