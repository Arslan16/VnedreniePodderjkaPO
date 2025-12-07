"""
2.	Конфигурация приложения:
2.1.	Хранить настройки приложения в Redis
2.2.	Реализовать кэширование настроек
2.3.	Обновлять настройки без перезапуска приложения
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
    base_key: str = "task5"

    def __init__(self):
        super().__init__()
        self.frame: AutoLayoutQFrame = AutoLayoutQFrame(QVBoxLayout)
        self.login_input: QLineEdit = QLineEdit()
        self.password_input: QLineEdit = QLineEdit()
        self.save_btn: QPushButton = QPushButton(
            text="Сохранить настройки",
            clicked=lambda:
                self.save_settings(
                    {
                        "login": self.login_input.text(),
                        "password": self.password_input.text()
                    }
            )
        )
        self.saved_settings_label: QLabel = QLabel(text=f"Сохраненный кеш:\n{self.get_settings()}")
        self.frame.addWidget(QLabel(text="Логин:"))
        self.frame.addWidget(self.login_input)
        self.frame.addWidget(QLabel(text="Пароль:"))
        self.frame.addWidget(self.password_input)
        self.frame.addWidget(self.save_btn)
        self.frame.addWidget(self.saved_settings_label)
        
        self.setCentralWidget(self.frame)

    def get_settings(self):
        return {
            key.decode() : value.decode() for key, value in redis.hgetall(self.base_key).items() or {}
        }
    def save_settings(self, cash: dict):
        redis.hset(self.base_key, mapping=cash)
        # Проще показывать сразу cash как он есть но для демонстрации работы
        # новый кеш повторно извлекается из редиса, хотя логической необходимости в этом нет
        self.saved_settings_label.setText(f"Сохраненный кеш:\n{self.get_settings()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
