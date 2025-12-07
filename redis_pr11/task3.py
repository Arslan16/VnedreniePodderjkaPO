"""
2.	Уникальные посетители:
2.1.	Подсчитывать уникальных посетителей за день
2.2.	Определять посетителей, которые были вчера, но не сегодня
2.3.	Находить постоянных посетителей (были все дни недели)
"""
import sys
import calendar
import locale
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel
)
from PyQt6.QtCore import Qt
from redis import Redis
from base import AutoLayoutQFrame


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
redis: Redis = Redis(
    host="localhost",
    port=6379
)


class MainWindow(QMainWindow):
    base_key: str = "task3"

    def __init__(self):
        super().__init__()
        self.days: list[str] = []
        self.frame = AutoLayoutQFrame(QHBoxLayout)
        self.choose_day_frame = AutoLayoutQFrame(QVBoxLayout)
        self.day_frame = AutoLayoutQFrame(QVBoxLayout)
        self.day_frame.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        # Добавление кнопок дней недели с привязкой к функции на клик
        for day_ind in range(7):
            self.days.append(calendar.day_name[day_ind])
            self.choose_day_frame.addWidget(
                QPushButton(
                    text=self.days[day_ind],
                    clicked=lambda
                        status,
                        day=calendar.day_name[day_ind],
                        previous_day=calendar.day_name[day_ind-1 if day_ind-1 >= 0 else 6]: 
                            self.fill_day_frame(
                                day=day,
                                previous_day=previous_day
                        )
                )
            )
        self.statistics_btn: QPushButton = QPushButton(
            text="Постоянники",
            clicked=lambda: self.fill_statistics()
        )
        self.choose_day_frame.addWidget(self.statistics_btn)
        self.frame.addWidget(self.choose_day_frame)
        self.frame.addWidget(self.day_frame)
        self.setCentralWidget(self.frame)

    def fill_day_frame(self, day: str, previous_day: str):
        self.day_frame.clear()
        self.day_frame.addWidget(QLabel(text=day))
        self.visitor_input: QLineEdit = QLineEdit()
        self.day_frame.addWidget(self.visitor_input)
        self.add_visitor_btn: QPushButton = QPushButton(
            text="Добавить посетителя",
            clicked=lambda: self.add_visitor(
                self.visitor_input.text(),
                day
            )
        )
        self.day_frame.addWidget(self.add_visitor_btn)
        
        unique_visitors_counter: int = redis.scard(f'{self.base_key}_{day}')
        self.unique_visitors_counter_label: QLabel = QLabel(text=f"Уникальных посетителей за день: {unique_visitors_counter}")
        self.yesterday_visitors_label: QLabel = QLabel(
            text=(
                "Посетители, бывшие в предыдущие день:\n"
                f"{'\n'.join(
                    [
                        visitor.decode() for visitor in redis.sdiff(
                            f'{self.base_key}_{previous_day}',
                            f'{self.base_key}_{day}'
                        )
                    ]
                )}"
            )
        )
        self.day_frame.addWidget(self.unique_visitors_counter_label)
        self.day_frame.addWidget(self.yesterday_visitors_label)

    def fill_statistics(self):
        self.day_frame.clear()
        self.day_frame.addWidget(
            QLabel(
                text=(
                    "Посетители всех дней:\n"
                    f"{'\n'.join(
                        [
                            visitor.decode() for visitor in redis.sinter(
                                [
                                    f'{self.base_key}_{day}' for day in self.days
                                ]
                            )
                        ]
                    )}"
                )
            )
        )

    def add_visitor(self, visitor: str, day: str):
        redis.sadd(f'{self.base_key}_{day}', visitor)
        unique_visitors_counter: int = redis.scard(f'{self.base_key}_{day}')
        self.unique_visitors_counter_label.setText(f"Уникальных посетителей за день: {unique_visitors_counter}")
        self.visitor_input.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
