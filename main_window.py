from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.scan_page import ScanPage
from ui.results_page import ResultsPage
from ui.benchmark_page import BenchmarkPage

APP_STYLE = """
QMainWindow, QWidget#root {
    background-color: #111318;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Inter', 'SF Pro Display', sans-serif;
}
QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2d3a;
    border-radius: 2px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { height: 0; }
QToolTip {
    background: #1e2130;
    color: #e2e8f0;
    border: 1px solid #2a2d3a;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}
"""

SIDEBAR_STYLE = """
QFrame#sidebar {
    background: #0c0e14;
    border-right: 1px solid #1a1d27;
}
"""

NAV_BTN = """
QPushButton {
    background: transparent;
    color: #6b7280;
    border: none;
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
}
QPushButton:hover {
    background: #16192a;
    color: #c4c9d4;
}
QPushButton[active="true"] {
    background: #1a1d2e;
    color: #a78bfa;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Bench")
        self.setMinimumSize(1100, 700)
        self.resize(1260, 800)
        self.setStyleSheet(APP_STYLE)
        self.system_info = None

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: #111318; }")
        self.scan_page = ScanPage(self)
        self.results_page = ResultsPage(self)
        self.benchmark_page = BenchmarkPage(self)
        self.stack.addWidget(self.scan_page)
        self.stack.addWidget(self.results_page)
        self.stack.addWidget(self.benchmark_page)
        root.addWidget(self.stack)

        self._navigate(0)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(SIDEBAR_STYLE)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(12, 20, 12, 20)
        lay.setSpacing(2)

        # Brand
        brand_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet("color: #7c3aed; font-size: 16px; padding: 0 4px 0 2px;")
        title = QLabel("LLM Bench")
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #e2e8f0; letter-spacing: -0.3px;")
        version = QLabel("v1.0")
        version.setStyleSheet("font-size: 11px; color: #3d4255; margin-left: 4px; padding-top: 2px;")
        brand_row.addWidget(dot)
        brand_row.addWidget(title)
        brand_row.addWidget(version)
        brand_row.addStretch()
        lay.addLayout(brand_row)
        lay.addSpacing(20)

        # Section label
        sec = QLabel("GENERAL")
        sec.setStyleSheet("font-size: 10px; color: #3a3f54; letter-spacing: 1.5px; font-weight: 600; padding: 0 6px; margin-bottom: 4px;")
        lay.addWidget(sec)

        self.nav_btns = []
        items = [
            ("⬡  System Scan", 0),
            ("◈  Recommendations", 1),
            ("◎  Benchmark", 2),
        ]
        for label, idx in items:
            btn = QPushButton(label)
            btn.setStyleSheet(NAV_BTN)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda _, i=idx: self._navigate(i))
            lay.addWidget(btn)
            self.nav_btns.append(btn)

        lay.addSpacing(16)
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #1a1d27;")
        lay.addWidget(div)
        lay.addStretch()

        # Bottom
        bottom_items = [
            ("⚙  Settings", None),
            ("⊞  Documentation", None),
        ]
        for label, _ in bottom_items:
            btn = QPushButton(label)
            btn.setStyleSheet(NAV_BTN)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            lay.addWidget(btn)

        lay.addSpacing(8)
        copy_label = QLabel("© 2026 Raghav Upadhyay\nAll rights reserved.")
        copy_label.setStyleSheet("font-size: 10px; color: #2a2f42; padding: 0 6px; line-height: 1.6;")
        copy_label.setAlignment(Qt.AlignLeft)
        lay.addWidget(copy_label)

        return sidebar

    def _navigate(self, idx):
        if idx in (1, 2) and self.system_info is None:
            self.stack.setCurrentIndex(0)
            self.scan_page.show_warning()
            self._set_active(0)
            return
        self.stack.setCurrentIndex(idx)
        self._set_active(idx)
        if idx == 1 and self.system_info:
            self.results_page.load(self.system_info)
        if idx == 2 and self.system_info:
            self.benchmark_page.load(self.system_info)

    def _set_active(self, active):
        for i, btn in enumerate(self.nav_btns):
            btn.setProperty("active", "true" if i == active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def on_scan_complete(self, info):
        self.system_info = info
