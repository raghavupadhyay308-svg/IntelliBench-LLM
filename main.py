import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LLM Bench")
    app.setApplicationVersion("1.0.0")
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
