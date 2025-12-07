"""
2.	Аудиты и логи изменений:
2.1.	Записывать все изменения в систему
2.2.	Реализовать механизм "воспроизведения" события, последовательная выполняя действия записанных логов автоматически
2.3.	Создать потребительские группы в самом Redis, чтобы обработать логи
"""
import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel
)
from redis import Redis
from base import AutoLayoutQFrame


redis: Redis = Redis(
    host="localhost",
    port=6379
)


class MainWindow(QMainWindow):
    base_key: str = "task6"

    def __init__(self):
        self.frame: AutoLayoutQFrame = AutoLayoutQFrame(QVBoxLayout)
        self.setCentralWidget(self.frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
