"""
2.	Временные ряды
2.1.	Сохранять показания датчиков температуры каждый час
2.2.	Получать среднюю температуру за период
2.3.	Находить пиковые значения
"""
import sys
from datetime import datetime
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
    base_key: str = "task4_timerow"

    def __init__(self):
        super().__init__()
        self.days: list[str] = []
        self.frame = AutoLayoutQFrame(QVBoxLayout)
        self.frame.addWidget(QLabel(text="Добавить значение температуры: "))
        self.temperature_input: QLineEdit = QLineEdit()
        self.add_temperature_btn: QPushButton = QPushButton(
            text="Добавить температуру",
            clicked=lambda:
                self.add_temperature(self.temperature_input.text())
        )
        self.averange_temp_label: QLabel = QLabel(text=f"Средняя температура: {self.get_avg_temp()}")
        self.max_temp_label: QLabel = QLabel(text=f"Максимальная температура: {self.get_max_temp()}")
        self.frame.addWidget(self.temperature_input)
        self.frame.addWidget(self.add_temperature_btn)
        self.frame.addWidget(self.averange_temp_label)
        self.frame.addWidget(self.max_temp_label)
        self.setCentralWidget(self.frame)

    def add_temperature(self, temp: str):
        if temp.isdigit():
            self.temperature_input.setText("")
            redis.zadd(self.base_key, {int(temp): datetime.now().timestamp()})
            self.averange_temp_label.setText(f"Средняя температура: {self.get_avg_temp()}")
            self.max_temp_label.setText(f"Максимальная температура: {self.get_max_temp()}")

    def get_avg_temp(self) -> float:
        temps: set = redis.zrange(
            self.base_key,
            start=0,
            end=-1
        )
        temps = [float(temp) for temp in temps]
        return sum(temps) / len(temps) if temps else 0.0

    def get_max_temp(self) -> float:
        return float(redis.zrevrange(self.base_key, 0, 0)[0] or 0.0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

