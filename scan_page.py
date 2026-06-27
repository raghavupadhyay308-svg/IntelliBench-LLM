from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QObject

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scanner.system_scan import scan_system

PAGE_BG  = "#111318"
CARD_BG  = "#14171f"
BORDER   = "#1e2130"
TEXT1    = "#e2e8f0"
TEXT2    = "#8b92a5"
TEXT3    = "#4a5068"
PURPLE   = "#7c3aed"
PURPLEL  = "#a78bfa"
GREEN    = "#10b981"
YELLOW   = "#f59e0b"
RED      = "#ef4444"

CARD = f"""
QFrame.card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
"""

BTN_PRIMARY = f"""
QPushButton {{
    background: {PURPLE};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    padding: 0 20px;
}}
QPushButton:hover {{ background: #6d28d9; }}
QPushButton:disabled {{ background: #1e2130; color: {TEXT3}; }}
"""


class Worker(QObject):
    done = Signal(dict)
    def run(self):
        self.done.emit(scan_system())


class ScanPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAGE_BG};")
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Top breadcrumb bar
        topbar = QFrame()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet(f"background: {PAGE_BG}; border-bottom: 1px solid {BORDER};")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(28, 0, 28, 0)
        crumb = QLabel(f'<span style="color:{TEXT3}">LLM Bench</span>'
                       f'<span style="color:{TEXT3}"> › </span>'
                       f'<span style="color:{TEXT1}; font-weight:600">System Scan</span>')
        crumb.setStyleSheet("font-size: 13px;")
        tb.addWidget(crumb)
        tb.addStretch()
        outer.addWidget(topbar)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {PAGE_BG}; border: none; }}")
        content = QWidget()
        content.setStyleSheet(f"background: {PAGE_BG};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(20)

        # Header
        h = QLabel("Welcome to LLM Bench")
        h.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {TEXT1}; letter-spacing: -0.5px;")
        sub = QLabel("Scan your hardware to discover which local LLMs you can run.")
        sub.setStyleSheet(f"font-size: 13px; color: {TEXT2}; margin-top: -4px;")
        lay.addWidget(h)
        lay.addWidget(sub)

        # Warning
        self.warn = QLabel("⚠  Run a scan first to unlock Recommendations and Benchmark.")
        self.warn.setStyleSheet(f"""
            background: rgba(239,68,68,0.08);
            border: 1px solid rgba(239,68,68,0.2);
            border-radius: 8px;
            padding: 10px 14px;
            color: #fca5a5;
            font-size: 12px;
        """)
        self.warn.hide()
        lay.addWidget(self.warn)

        # Scan button + status row
        row = QHBoxLayout()
        self.btn = QPushButton("Run system scan")
        self.btn.setFixedHeight(38)
        self.btn.setFixedWidth(160)
        self.btn.setStyleSheet(BTN_PRIMARY)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self._scan)
        self.status = QLabel("")
        self.status.setStyleSheet(f"font-size: 12px; color: {PURPLEL}; margin-left: 12px;")
        row.addWidget(self.btn)
        row.addWidget(self.status)
        row.addStretch()
        lay.addLayout(row)

        # Results (hidden until scan)
        self.results = QWidget()
        self.results.hide()
        rl = QVBoxLayout(self.results)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(16)

        # Stats grid (4 cards)
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        rl.addLayout(self.grid)

        # GPU card (full width)
        self.gpu_card = QFrame()
        self.gpu_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        self.gpu_lay = QVBoxLayout(self.gpu_card)
        self.gpu_lay.setContentsMargins(20, 16, 20, 16)
        self.gpu_lay.setSpacing(6)
        rl.addWidget(self.gpu_card)

        # Ollama card
        self.ollama_card = QFrame()
        self.ollama_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        self.ollama_lay = QVBoxLayout(self.ollama_card)
        self.ollama_lay.setContentsMargins(20, 16, 20, 16)
        self.ollama_lay.setSpacing(4)
        rl.addWidget(self.ollama_card)

        lay.addWidget(self.results)
        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _scan(self):
        self.warn.hide()
        self.btn.setEnabled(False)
        self.status.setText("Scanning hardware…")
        self.results.hide()

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self._done)
        self.worker.done.connect(self.thread.quit)
        self.thread.start()

    def _done(self, info):
        self.btn.setEnabled(True)
        self.status.setText("Scan complete — navigate to Recommendations")
        self._render(info)
        self.results.show()
        mw = self.window()
        if hasattr(mw, "on_scan_complete"):
            mw.on_scan_complete(info)

    def _render(self, info):
        # Clear grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.setParent(None)

        cpu = info["cpu"]
        ram = info["ram"]
        storage = info["storage"]
        os_info = info["os"]

        cards = [
            ("CPU", cpu["name"],
             f'{cpu["cores_physical"]}P / {cpu["cores_logical"]}L cores'
             + (f'  ·  {int(cpu["freq_mhz"])} MHz' if cpu.get("freq_mhz") else ""),
             PURPLEL),
            ("Memory", f'{ram["total_gb"]} GB',
             f'{ram["available_gb"]} GB free  ·  {ram["used_percent"]}% used', GREEN),
            ("Storage", f'{storage[0]["total_gb"]} GB' if storage else "N/A",
             f'{storage[0]["free_gb"]} GB free on {storage[0]["mountpoint"]}' if storage else "", YELLOW),
            ("Platform", os_info["system"] + " " + os_info["release"],
             cpu["arch"], TEXT2),
        ]

        for i, (label, val, sub, col) in enumerate(cards):
            c = self._stat_card(label, val, sub, col)
            self.grid.addWidget(c, 0, i)

        # GPU
        for i in reversed(range(self.gpu_lay.count())):
            w = self.gpu_lay.itemAt(i).widget()
            if w: w.setParent(None)

        gpus = info["gpu"]
        gl = QLabel("GPU")
        gl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {TEXT3}; letter-spacing: 1px;")
        self.gpu_lay.addWidget(gl)

        if gpus:
            for g in gpus:
                row = QHBoxLayout()
                name = QLabel(g["name"])
                name.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT1};")
                row.addWidget(name)
                row.addStretch()
                cuda = QLabel("CUDA ✓" if g.get("cuda") else "No CUDA")
                cuda.setStyleSheet(f"font-size: 12px; color: {'#10b981' if g.get('cuda') else '#ef4444'}; font-weight: 600;")
                row.addWidget(cuda)
                self.gpu_lay.addLayout(row)
                vram = QLabel(f'{g["vram_total_gb"]} GB VRAM' if g.get("vram_total_gb") else "VRAM unknown")
                vram.setStyleSheet(f"font-size: 12px; color: {TEXT2};")
                self.gpu_lay.addWidget(vram)
        else:
            name = QLabel("No dedicated GPU detected")
            name.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT2};")
            sub = QLabel("CPU inference only — models will run slower")
            sub.setStyleSheet(f"font-size: 12px; color: {TEXT3};")
            self.gpu_lay.addWidget(name)
            self.gpu_lay.addWidget(sub)

        # Ollama
        for i in reversed(range(self.ollama_lay.count())):
            w = self.ollama_lay.itemAt(i).widget()
            if w: w.setParent(None)

        ol = QLabel("Ollama")
        ol.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {TEXT3}; letter-spacing: 1px;")
        self.ollama_lay.addWidget(ol)

        ollama = info["ollama"]
        if ollama["installed"]:
            row = QHBoxLayout()
            status = QLabel("Installed")
            status.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {GREEN};")
            row.addWidget(status)
            row.addStretch()
            path = QLabel(ollama.get("path", "ollama"))
            path.setStyleSheet(f"font-size: 11px; color: {TEXT3}; font-family: monospace;")
            row.addWidget(path)
            self.ollama_lay.addLayout(row)
            models = ollama.get("models", [])
            if models:
                ml = QLabel("Installed: " + "  ·  ".join(models[:10]))
                ml.setStyleSheet(f"font-size: 12px; color: {TEXT2};")
                self.ollama_lay.addWidget(ml)
            else:
                ml = QLabel("No models installed — visit Recommendations to download.")
                ml.setStyleSheet(f"font-size: 12px; color: {TEXT3};")
                self.ollama_lay.addWidget(ml)
        else:
            s = QLabel("Not installed")
            s.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {YELLOW};")
            self.ollama_lay.addWidget(s)
            d = QLabel("Install Ollama from ollama.com to run models locally.")
            d.setStyleSheet(f"font-size: 12px; color: {TEXT3};")
            self.ollama_lay.addWidget(d)

    def _stat_card(self, label, value, sub, accent):
        card = QFrame()
        card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {TEXT3}; letter-spacing: 1.2px;")

        val = QLabel(str(value))
        val.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT1};")
        val.setWordWrap(True)

        s = QLabel(str(sub))
        s.setStyleSheet(f"font-size: 11px; color: {TEXT2};")
        s.setWordWrap(True)

        # Accent bar
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"background: {accent}; border-radius: 2px; margin-bottom: 8px;")
        lay.addWidget(bar)
        lay.addWidget(lbl)
        lay.addWidget(val)
        lay.addWidget(s)
        return card

    def show_warning(self):
        self.warn.show()
