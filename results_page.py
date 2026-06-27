from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QComboBox, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from recommender.model_recommender import recommend_models

PAGE_BG = "#111318"
CARD_BG = "#14171f"
CARD_HV = "#161924"
BORDER  = "#1e2130"
BORDER2 = "#252a3d"
TEXT1   = "#e2e8f0"
TEXT2   = "#8b92a5"
TEXT3   = "#4a5068"
PURPLE  = "#7c3aed"
PURPLEL = "#a78bfa"
GREEN   = "#10b981"
RED     = "#ef4444"

UC_COLORS = {
    "Coding":        ("#1a2d4a", "#60a5fa"),
    "General Chat":  ("#2a1a4a", "#c084fc"),
    "RAG":           ("#0f2d23", "#34d399"),
    "Summarization": ("#2d1f0a", "#fbbf24"),
}
SPEED_C = {"Fast": "#10b981", "Medium": "#f59e0b", "Slow": "#ef4444"}

COMBO_STYLE = f"""
QComboBox {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 7px;
    color: {TEXT1};
    padding: 6px 10px;
    font-size: 12px;
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: #1a1d2e;
    color: {TEXT1};
    border: 1px solid {BORDER2};
    selection-background-color: {PURPLE};
    outline: none;
}}
"""


class ResultsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAGE_BG};")
        self._system_info = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Topbar
        top = QFrame()
        top.setFixedHeight(52)
        top.setStyleSheet(f"background: {PAGE_BG}; border-bottom: 1px solid {BORDER};")
        tb = QHBoxLayout(top)
        tb.setContentsMargins(28, 0, 28, 0)
        crumb = QLabel(f'<span style="color:{TEXT3}">LLM Bench › </span>'
                       f'<span style="color:{TEXT1}; font-weight:600">Recommendations</span>')
        crumb.setStyleSheet("font-size: 13px;")
        tb.addWidget(crumb)
        tb.addStretch()
        self.count_label = QLabel("")
        self.count_label.setStyleSheet(f"font-size: 12px; color: {TEXT3};")
        tb.addWidget(self.count_label)
        outer.addWidget(top)

        # Filter bar
        fbar = QFrame()
        fbar.setFixedHeight(52)
        fbar.setStyleSheet(f"background: {PAGE_BG}; border-bottom: 1px solid {BORDER};")
        fb = QHBoxLayout(fbar)
        fb.setContentsMargins(28, 0, 28, 0)
        fb.setSpacing(10)

        fl = QLabel("Filter:")
        fl.setStyleSheet(f"font-size: 12px; color: {TEXT3};")
        fb.addWidget(fl)

        self.combo = QComboBox()
        self.combo.addItems(["All", "Coding", "General Chat", "RAG", "Summarization"])
        self.combo.setFixedWidth(180)
        self.combo.setStyleSheet(COMBO_STYLE)
        self.combo.currentTextChanged.connect(self._filter)
        fb.addWidget(self.combo)
        fb.addStretch()
        outer.addWidget(fbar)

        # Cards scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {PAGE_BG}; border: none; }}")

        self.container = QWidget()
        self.container.setStyleSheet(f"background: {PAGE_BG};")
        self.cl = QVBoxLayout(self.container)
        self.cl.setContentsMargins(28, 20, 28, 20)
        self.cl.setSpacing(8)

        scroll.setWidget(self.container)
        outer.addWidget(scroll)

    def load(self, info):
        self._system_info = info
        self._filter(self.combo.currentText())

    def _filter(self, uc):
        if not self._system_info:
            return
        uc_arg = None if uc == "All" else uc
        models = recommend_models(self._system_info, use_case_filter=uc_arg)

        for i in reversed(range(self.cl.count())):
            item = self.cl.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        ok = [m for m in models if m["can_run"]]
        no = [m for m in models if not m["can_run"]]
        self.count_label.setText(f"{len(ok)} compatible  ·  {len(no)} incompatible")

        if ok:
            sec = self._section_label("Compatible with your system", GREEN)
            self.cl.addWidget(sec)
            for m in ok:
                self.cl.addWidget(self._card(m, True))

        if no:
            sec = self._section_label("Requires more hardware", RED)
            self.cl.addWidget(sec)
            for m in no:
                self.cl.addWidget(self._card(m, False))

        self.cl.addStretch()

    def _section_label(self, text, color):
        l = QLabel(text)
        l.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {color}; "
                        f"letter-spacing: 0.5px; padding: 12px 0 4px 0;")
        return l

    def _card(self, model, can_run):
        card = QFrame()
        border_col = "#1e3a2e" if can_run else BORDER
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD_BG};
                border: 1px solid {border_col};
                border-radius: 10px;
            }}
            QFrame:hover {{
                background: {CARD_HV};
                border: 1px solid {BORDER2};
            }}
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(card)
        row.setContentsMargins(18, 14, 16, 14)
        row.setSpacing(16)

        # Left
        left = QVBoxLayout()
        left.setSpacing(5)

        # Name row
        nr = QHBoxLayout()
        nr.setSpacing(8)
        name = QLabel(model["name"])
        name.setStyleSheet(f"font-size: 14px; font-weight: 700; "
                           f"color: {TEXT1 if can_run else TEXT3};")
        nr.addWidget(name)

        sc = SPEED_C.get(model["speed_class"], TEXT2)
        spd = QLabel(f"● {model['speed_class']}")
        spd.setStyleSheet(f"font-size: 11px; color: {sc}; font-weight: 500;")
        nr.addWidget(spd)
        nr.addStretch()

        tag_lbl = QLabel(model["ollama_tag"])
        tag_lbl.setStyleSheet(f"font-size: 10px; color: {TEXT3}; "
                               f"font-family: 'Consolas', monospace;")
        nr.addWidget(tag_lbl)
        left.addLayout(nr)

        # Description
        desc = QLabel(model["description"])
        desc.setStyleSheet(f"font-size: 12px; color: {TEXT2};")
        desc.setWordWrap(True)
        left.addWidget(desc)

        # Tags
        tr = QHBoxLayout()
        tr.setSpacing(5)
        for uc in model["use_cases"]:
            bg, fg = UC_COLORS.get(uc, (BORDER, TEXT2))
            t = QLabel(uc)
            t.setStyleSheet(f"background: {bg}; color: {fg}; border-radius: 4px; "
                            f"padding: 2px 8px; font-size: 10px; font-weight: 600;")
            tr.addWidget(t)
        tr.addStretch()
        left.addLayout(tr)

        # Perf note
        pc = GREEN if can_run else RED
        pn = QLabel(model["performance_note"])
        pn.setStyleSheet(f"font-size: 11px; color: {pc};")
        left.addWidget(pn)

        row.addLayout(left, stretch=4)

        # Right
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop | Qt.AlignRight)
        right.setSpacing(6)

        sz = QLabel(f"{model['size_gb']} GB")
        sz.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {PURPLEL};")
        sz.setAlignment(Qt.AlignRight)
        right.addWidget(sz)

        req_parts = [f"RAM {model['min_ram_gb']}GB"]
        if model['min_vram_gb'] > 0:
            req_parts.append(f"VRAM {model['min_vram_gb']}GB")
        req = QLabel("  ·  ".join(req_parts))
        req.setStyleSheet(f"font-size: 10px; color: {TEXT3};")
        req.setAlignment(Qt.AlignRight)
        right.addWidget(req)

        # Download btn
        dl = QPushButton("↓  Ollama page")
        dl.setFixedHeight(30)
        dl.setFixedWidth(120)
        dl.setCursor(Qt.PointingHandCursor)
        dl.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {BORDER2};
                border-radius: 6px;
                color: {PURPLEL};
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: rgba(124,58,237,0.12);
                border: 1px solid {PURPLE};
            }}
        """)
        url = model["download_url"]
        dl.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
        right.addWidget(dl)

        # Copy command
        cmd = f"ollama pull {model['ollama_tag']}"
        cp = QPushButton(cmd)
        cp.setFixedHeight(26)
        cp.setFixedWidth(120)
        cp.setCursor(Qt.PointingHandCursor)
        cp.setStyleSheet(f"""
            QPushButton {{
                background: #0e1018;
                border: 1px solid {BORDER};
                border-radius: 5px;
                color: {TEXT3};
                font-size: 9px;
                font-family: 'Consolas', monospace;
                padding: 0 6px;
            }}
            QPushButton:hover {{ color: {TEXT2}; background: #131620; }}
        """)
        cp.clicked.connect(lambda _, c=cmd, b=cp: self._copy(c, b))
        right.addWidget(cp)

        row.addLayout(right, stretch=1)
        return card

    def _copy(self, text, btn):
        QApplication.clipboard().setText(text)
        orig = btn.text()
        btn.setText("✓ Copied")
        QTimer.singleShot(1500, lambda: btn.setText(orig))
