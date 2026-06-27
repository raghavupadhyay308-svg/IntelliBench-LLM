from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QPainter, QColor, QPen
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from recommender.model_recommender import recommend_models
from benchmark.inference_test import run_benchmark

PAGE_BG  = "#111318"
CARD_BG  = "#14171f"
BORDER   = "#1e2130"
BORDER2  = "#252a3d"
TEXT1    = "#e2e8f0"
TEXT2    = "#8b92a5"
TEXT3    = "#4a5068"
PURPLE   = "#7c3aed"
PURPLEL  = "#a78bfa"
GREEN    = "#10b981"
YELLOW   = "#f59e0b"
RED      = "#ef4444"
ORANGE   = "#f97316"
INDIGO   = "#6366f1"

TIER_COLORS = {
    "Won't Run": RED,
    "Slow":      ORANGE,
    "Okay":      YELLOW,
    "Good":      GREEN,
    "Great":     INDIGO,
}

COMBO_STYLE = f"""
QComboBox {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 7px;
    color: {TEXT1};
    padding: 6px 10px;
    font-size: 12px;
    min-width: 260px;
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: #1a1d2e;
    color: {TEXT1};
    border: 1px solid {BORDER2};
    selection-background-color: {PURPLE};
    outline: none;
    font-size: 12px;
}}
"""

BTN = f"""
QPushButton {{
    background: {PURPLE};
    color: #ffffff;
    border: none;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
    padding: 0 18px;
}}
QPushButton:hover {{ background: #6d28d9; }}
QPushButton:disabled {{ background: {BORDER}; color: {TEXT3}; }}
"""

BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {PURPLEL};
    border: 1px solid {BORDER2};
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
    padding: 0 16px;
}}
QPushButton:hover {{ background: rgba(124,58,237,0.1); border-color: {PURPLE}; }}
QPushButton:disabled {{ color: {TEXT3}; border-color: {BORDER}; }}
"""


class BenchmarkSignals(QObject):
    progress = Signal(str)
    result   = Signal(dict)


class ScoreRing(QWidget):
    """Circular score gauge widget."""
    def __init__(self, score=0, color="#6366f1", parent=None):
        super().__init__(parent)
        self.score = score
        self.color = color
        self.setFixedSize(120, 120)

    def set_score(self, score, color):
        self.score = score
        self.color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        size = self.width()
        margin = 10
        rect_size = size - margin * 2

        # Background ring
        p.setPen(QPen(QColor("#1e2130"), 10, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(margin, margin, rect_size, rect_size, 0, 360 * 16)

        # Score arc
        span = int((self.score / 100) * 360 * 16)
        p.setPen(QPen(QColor(self.color), 10, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(margin, margin, rect_size, rect_size, 90 * 16, -span)

        # Score text
        p.setPen(QColor(TEXT1))
        font = p.font()
        font.setPointSize(18)
        font.setBold(True)
        p.setFont(font)
        p.drawText(0, 0, size, size, Qt.AlignCenter, str(self.score))


class BenchmarkPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAGE_BG};")
        self.signals  = BenchmarkSignals()
        self.signals.progress.connect(self._on_progress)
        self.signals.result.connect(self._on_real_result)
        self._system_info = None
        self._models_list = []
        self._current_model = None
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
                       f'<span style="color:{TEXT1}; font-weight:600">Benchmark</span>')
        crumb.setStyleSheet("font-size: 13px;")
        tb.addWidget(crumb)
        outer.addWidget(top)

        # Scroll
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
        h = QLabel("Model Benchmark")
        h.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {TEXT1}; letter-spacing: -0.5px;")
        sub = QLabel("Select any model — get an ML-predicted performance score instantly, even without installing it.")
        sub.setStyleSheet(f"font-size: 13px; color: {TEXT2};")
        lay.addWidget(h)
        lay.addWidget(sub)

        # Model selector row
        sel = QHBoxLayout()
        sel.setSpacing(10)
        self.combo = QComboBox()
        self.combo.setStyleSheet(COMBO_STYLE)
        self.combo.currentIndexChanged.connect(self._on_model_select)

        self.predict_btn = QPushButton("▶  Predict performance")
        self.predict_btn.setFixedHeight(36)
        self.predict_btn.setStyleSheet(BTN)
        self.predict_btn.setCursor(Qt.PointingHandCursor)
        self.predict_btn.clicked.connect(self._run_predict)
        self.predict_btn.setEnabled(False)

        self.real_btn = QPushButton("⏱  Run real benchmark")
        self.real_btn.setFixedHeight(36)
        self.real_btn.setStyleSheet(BTN_GHOST)
        self.real_btn.setCursor(Qt.PointingHandCursor)
        self.real_btn.clicked.connect(self._run_real)
        self.real_btn.setEnabled(False)
        self.real_btn.setToolTip("Only available if model is installed via Ollama")

        sel.addWidget(self.combo)
        sel.addWidget(self.predict_btn)
        sel.addWidget(self.real_btn)
        sel.addStretch()
        lay.addLayout(sel)

        # Status
        self.status = QLabel("")
        self.status.setStyleSheet(f"font-size: 12px; color: {PURPLEL};")
        lay.addWidget(self.status)

        # Results area (hidden until predict runs)
        self.results_frame = QWidget()
        self.results_frame.hide()
        rf = QVBoxLayout(self.results_frame)
        rf.setContentsMargins(0, 0, 0, 0)
        rf.setSpacing(16)

        # Top row: score ring + metric cards
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # Score ring card
        ring_card = QFrame()
        ring_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        ring_card.setFixedWidth(200)
        ring_lay = QVBoxLayout(ring_card)
        ring_lay.setContentsMargins(16, 16, 16, 16)
        ring_lay.setAlignment(Qt.AlignCenter)
        ring_lay.setSpacing(8)

        score_lbl = QLabel("PERFORMANCE SCORE")
        score_lbl.setStyleSheet(f"font-size: 10px; color: {TEXT3}; letter-spacing: 1px; font-weight: 600;")
        score_lbl.setAlignment(Qt.AlignCenter)
        self.ring = ScoreRing(0, INDIGO)
        self.tier_badge = QLabel("—")
        self.tier_badge.setAlignment(Qt.AlignCenter)
        self.tier_badge.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {TEXT1};")

        ring_lay.addWidget(score_lbl)
        ring_lay.addWidget(self.ring, alignment=Qt.AlignCenter)
        ring_lay.addWidget(self.tier_badge)
        top_row.addWidget(ring_card)

        # Metric cards grid
        metrics_grid = QVBoxLayout()
        metrics_grid.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.card_tps    = self._metric_card("Predicted tokens/sec", "—", PURPLEL)
        self.card_tier   = self._metric_card("Quality tier", "—", GREEN)
        row1.addWidget(self.card_tps[0])
        row1.addWidget(self.card_tier[0])

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.card_size   = self._metric_card("Model size", "—", YELLOW)
        self.card_req    = self._metric_card("RAM required", "—", ORANGE)
        row2.addWidget(self.card_size[0])
        row2.addWidget(self.card_req[0])

        metrics_grid.addLayout(row1)
        metrics_grid.addLayout(row2)
        top_row.addLayout(metrics_grid)
        rf.addLayout(top_row)

        # Probability breakdown card
        prob_card = QFrame()
        prob_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        prob_lay = QVBoxLayout(prob_card)
        prob_lay.setContentsMargins(20, 16, 20, 16)
        prob_lay.setSpacing(10)

        prob_title = QLabel("TIER PROBABILITY BREAKDOWN")
        prob_title.setStyleSheet(f"font-size: 10px; color: {TEXT3}; letter-spacing: 1px; font-weight: 600;")
        prob_lay.addWidget(prob_title)

        self.prob_bars = {}
        for tier_name, color in TIER_COLORS.items():
            row = QHBoxLayout()
            row.setSpacing(10)
            lbl = QLabel(tier_name)
            lbl.setFixedWidth(80)
            lbl.setStyleSheet(f"font-size: 12px; color: {TEXT2};")

            bar_bg = QFrame()
            bar_bg.setFixedHeight(8)
            bar_bg.setStyleSheet(f"background: {BORDER}; border-radius: 4px;")
            bar_bg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            bar_fill = QFrame(bar_bg)
            bar_fill.setFixedHeight(8)
            bar_fill.setStyleSheet(f"background: {color}; border-radius: 4px;")
            bar_fill.setFixedWidth(0)

            pct = QLabel("0%")
            pct.setFixedWidth(36)
            pct.setAlignment(Qt.AlignRight)
            pct.setStyleSheet(f"font-size: 11px; color: {TEXT3};")

            row.addWidget(lbl)
            row.addWidget(bar_bg)
            row.addWidget(pct)
            prob_lay.addLayout(row)
            self.prob_bars[tier_name] = (bar_bg, bar_fill, pct)

        rf.addWidget(prob_card)

        # ML model info card
        ml_card = QFrame()
        ml_card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        ml_lay = QHBoxLayout(ml_card)
        ml_lay.setContentsMargins(20, 12, 20, 12)
        ml_lay.setSpacing(24)

        ml_title = QLabel("ML Model:")
        ml_title.setStyleSheet(f"font-size: 11px; color: {TEXT3};")
        self.ml_r2  = QLabel("Regressor R²: —")
        self.ml_acc = QLabel("Classifier Accuracy: —")
        self.ml_tag = QLabel("RandomForest · scikit-learn")
        for w in [ml_title, self.ml_r2, self.ml_acc, self.ml_tag]:
            w.setStyleSheet(f"font-size: 11px; color: {TEXT3};")
        ml_lay.addWidget(ml_title)
        ml_lay.addWidget(self.ml_r2)
        ml_lay.addWidget(self.ml_acc)
        ml_lay.addStretch()
        ml_lay.addWidget(self.ml_tag)
        rf.addWidget(ml_card)

        # Real benchmark section (shown only if Ollama model installed)
        self.real_section = QFrame()
        self.real_section.hide()
        self.real_section.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;")
        rs_lay = QVBoxLayout(self.real_section)
        rs_lay.setContentsMargins(20, 16, 20, 16)
        rs_lay.setSpacing(10)

        rs_title = QLabel("REAL BENCHMARK RESULT")
        rs_title.setStyleSheet(f"font-size: 10px; color: {TEXT3}; letter-spacing: 1px; font-weight: 600;")
        rs_lay.addWidget(rs_title)

        compare_row = QHBoxLayout()
        compare_row.setSpacing(16)
        self.real_tps_lbl  = QLabel("Actual: —")
        self.pred_tps_lbl  = QLabel("Predicted: —")
        self.diff_lbl      = QLabel("")
        for w in [self.real_tps_lbl, self.pred_tps_lbl, self.diff_lbl]:
            w.setStyleSheet(f"font-size: 13px; color: {TEXT1}; font-weight: 600;")
        compare_row.addWidget(self.real_tps_lbl)
        compare_row.addWidget(self.pred_tps_lbl)
        compare_row.addWidget(self.diff_lbl)
        compare_row.addStretch()
        rs_lay.addLayout(compare_row)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFixedHeight(120)
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background: #0c0e14;
                border: 1px solid {BORDER};
                border-radius: 8px;
                color: {TEXT2};
                font-size: 12px;
                font-family: 'Consolas', monospace;
                padding: 10px;
            }}
        """)
        self.output_text.setPlaceholderText("Model output appears here…")
        rs_lay.addWidget(self.output_text)
        rf.addWidget(self.real_section)

        lay.addWidget(self.results_frame)
        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _metric_card(self, label, value, color):
        card = QFrame()
        card.setStyleSheet(f"background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 10px;")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"background: {color}; border-radius: 2px;")
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"font-size: 10px; color: {TEXT3}; letter-spacing: 1px; font-weight: 600;")
        val = QLabel(value)
        val.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT1};")

        lay.addWidget(bar)
        lay.addWidget(lbl)
        lay.addWidget(val)
        return card, val

    def load(self, system_info):
        self._system_info = system_info
        self._models_list = recommend_models(system_info)
        installed = set(system_info.get("ollama", {}).get("models", []))

        self.combo.clear()
        for m in self._models_list:
            suffix = " ✓" if m["ollama_tag"] in installed else ""
            self.combo.addItem(f"{m['name']}  ({m['size_gb']}GB){suffix}", m)

        self.predict_btn.setEnabled(True)
        self.real_section.hide()

    def _on_model_select(self, idx):
        if idx < 0 or not self._system_info:
            return
        model = self.combo.itemData(idx)
        self._current_model = model
        installed = set(self._system_info.get("ollama", {}).get("models", []))
        self.real_btn.setEnabled(model and model["ollama_tag"] in installed)

    def _run_predict(self):
        if not self._current_model or not self._system_info:
            return
        try:
            from ml.predictor import predict
            result = predict(self._system_info, self._current_model)
            self._show_prediction(result)
        except Exception as e:
            self.status.setText(f"ML prediction error: {e}")

    def _show_prediction(self, result):
        self.results_frame.show()
        self.status.setText("")

        score = result["score"]
        color = result["tier_color"]
        self.ring.set_score(score, color)
        self.tier_badge.setText(f"{result['tier_emoji']}  {result['tier_name']}")
        self.tier_badge.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {color};")

        tps = result["tokens_per_sec"]
        self.card_tps[1].setText(f"{tps}" if tps > 0 else "0")
        self.card_tier[1].setText(result["tier_name"])
        self.card_tier[1].setStyleSheet(f"font-size: 20px; font-weight: 700; color: {color};")
        self.card_size[1].setText(f"{self._current_model['size_gb']} GB")
        self.card_req[1].setText(f"{self._current_model['min_ram_gb']} GB")

        # Probability bars
        probs = result["tier_probs"]
        for tier_name, (bar_bg, bar_fill, pct_lbl) in self.prob_bars.items():
            p = probs.get(tier_name, 0)
            pct_lbl.setText(f"{p:.0f}%")
            bar_bg.update()
            bar_bg.resizeEvent = lambda e, bf=bar_fill, pp=p: (
                bf.setFixedWidth(int(e.size().width() * pp / 100))
            )
            bar_fill.setFixedWidth(int(bar_bg.width() * p / 100))

        self.ml_r2.setText(f"Regressor R²: {result['model_r2']:.4f}")
        self.ml_acc.setText(f"Classifier Accuracy: {result['model_acc']*100:.1f}%")

        # Store predicted tps for comparison
        self._predicted_tps = tps

    def _run_real(self):
        if not self._current_model:
            return
        self.real_btn.setEnabled(False)
        self.real_section.show()
        self.output_text.setPlainText("")
        self.real_tps_lbl.setText("Running…")

        run_benchmark(
            self._current_model["ollama_tag"],
            progress_callback=lambda m: self.signals.progress.emit(m),
            result_callback=lambda r: self.signals.result.emit(r),
        )

    def _on_progress(self, msg):
        self.status.setText(f"⏳ {msg}")

    def _on_real_result(self, result):
        self.real_btn.setEnabled(True)
        self.status.setText("")

        if not result["success"]:
            self.real_tps_lbl.setText(f"Error: {result['error']}")
            return

        actual = result["tokens_per_sec"]
        predicted = getattr(self, "_predicted_tps", 0)

        self.real_tps_lbl.setText(f"Actual: {actual} t/s")
        self.pred_tps_lbl.setText(f"Predicted: {predicted} t/s")

        if predicted > 0:
            diff = ((actual - predicted) / predicted) * 100
            sign = "+" if diff >= 0 else ""
            color = GREEN if abs(diff) < 25 else YELLOW
            self.diff_lbl.setText(f"({sign}{diff:.1f}% vs prediction)")
            self.diff_lbl.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: 600;")

        self.output_text.setPlainText(result.get("output", ""))
