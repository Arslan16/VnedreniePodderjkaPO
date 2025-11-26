import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QFrame,
    QTextEdit,
    QLineEdit,
    QLabel,
)

from sqlalchemy import select
from sqlalchemy.sql import Select

from config import redis_client, engine, app_sessionmaker
from models import Base, User


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Widgets App")
        self.setGeometry(100, 100, 600, 400)

        self.user_entry: QLineEdit = QLineEdit()
        self.notification_label: QLabel = QLabel(text="Напишите имя")
        self.notification_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.append_user_btn: QPushButton = QPushButton(text="Добавить пользователя")
        self.append_user_btn.clicked.connect(self.append_user)
        self.load_users_btn: QPushButton = QPushButton(text="Загрузка пользователей")
        self.load_users_btn.clicked.connect(lambda: self.show_user_list())
        self.text_field: QTextEdit = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.user_entry)
        layout.addWidget(self.notification_label, stretch=0)
        layout.addWidget(self.append_user_btn)
        layout.addWidget(self.load_users_btn)
        layout.addWidget(self.text_field)
    
        central_widget: QFrame = QFrame()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def append_user(self):
        try:
            new_user_name: str = self.user_entry.text()
            with app_sessionmaker() as session:  
                incoming_user: User = User(
                    name=new_user_name
                )
                session.add(incoming_user)
                session.commit()
            redis_client.rpush('users', new_user_name)
            self.notification_label.setText("Новый пользователь добавлен!")
            self.user_entry.setText("")
        except Exception as exc:
            print(exc)
            self.notification_label.setText("Ошибка при добавлении пользователяы!")
    
    def show_user_list(self, limit: int = 5):
        try:
            users: list[str] = redis_client.lrange('users', -1, -5)
            if users is None:
                users = []
            else:
                users = [usr.decode() for usr in users]
            # Извлекаем последние 5 значений списка
            if len(users) < limit:
                with app_sessionmaker() as session:
                    need_users = limit - len(users)
                    stmt: Select = select(
                        User.name
                    ).where(
                        User.name.not_in(users)
                    ).limit(
                        need_users
                    )
                    result = session.scalars(stmt)
                    for user in result:
                        users.append(user)
            else:
                users = users[0:limit]
            self.text_field.clear()
            self.text_field.setText(
                "\n".join(users)
            )
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    # Создание таблицы пользователей в бд
    Base.metadata.create_all(engine)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
