"""
2.	Счетчик посещений:
2.1.	Создать атомарный счетчик для подсчета посещений страницы
2.2.	Реализовать суточный счетчик с автоматическим сбросом
2.3.	Добавить счетчик уникальных посещений за месяц
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
    base_key: str = "task1"
    def __init__(self):
        if redis.exists("task1_user_daily_counter") == 0:
            redis.set("task1_user_daily_counter", 0, ex=24*60*60)

        self.user_counter: int = redis.get("task1_users_counter") or 0
        self.user_daily_counter: int = redis.get("task1_user_daily_counter") or 0
        self.user_unique_logins_counter: int = redis.scard("task1_users_login_list") or 0

        super().__init__()

        self.frame = AutoLayoutQFrame(QVBoxLayout)
        self.login_input: QLineEdit = QLineEdit(self.frame)
        self.login_btn: QPushButton = QPushButton("Войти", self.frame)
        self.login_btn.clicked.connect(lambda: self.log_in(self.login_input.text()))
        self.user_counter_label: QLabel = QLabel(text=f"Количество посищений: {self.user_counter}")
        self.daily_user_counter_label: QLabel = QLabel(text=f"Количество посещений в сутки: {self.user_daily_counter}")
        self.user_unique_logins_label: QLabel = QLabel(text=f"Количество уникальных посещений за месяц: {self.user_unique_logins_counter}")

        self.frame.addWidget(self.login_input)
        self.frame.addWidget(self.login_btn)
        self.frame.addWidget(self.user_counter_label)
        self.frame.addWidget(self.daily_user_counter_label)
        self.frame.addWidget(self.user_unique_logins_label)
        self.setCentralWidget(self.frame)

    def log_in(self, login: str):
        if redis.sismember("task1_users_login_list", login) == 0:
            redis.sadd("task1_users_login_list", login)
            self.user_unique_logins_counter: int = redis.scard("task1_users_login_list")

        self.user_counter: int = redis.incr("task1_users_counter", 1)
        self.user_daily_counter: int = redis.incr("task1_user_daily_counter", 1)

        self.user_counter_label.setText(f"Количество посищений: {self.user_counter}")
        self.daily_user_counter_label.setText(f"Количество посещений в сутки: {self.user_daily_counter}")
        self.user_unique_logins_label.setText(f"Количество уникальных посещений за месяц: {self.user_unique_logins_counter}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
