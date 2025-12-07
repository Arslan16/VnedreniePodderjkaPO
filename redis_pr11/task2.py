"""
2.	Очередь задач:
2.1.	Создать FIFO (First-In-First-Out) очередь задач
2.2.	Реализовать механизм обработки задач с подтверждением
2.3.	Добавить возможность приоритизации задач
"""
import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget
)
from redis import Redis
from base import AutoLayoutQFrame

redis: Redis = Redis(
    host="localhost",
    port=6379
)


class MainWindow(QMainWindow):
    """
    В условии задачи противорчеие!
    FIFO и приоритезация это диаметрально противоположные принципы
    Механизм приоритезации не может быть реализован для обычного FIFO задачника
    """
    base_key: str = "task2"

    def __init__(self):
        super().__init__()
        
        self.frame = AutoLayoutQFrame(QVBoxLayout)
        self.task_list = QListWidget()
        self.task_list.setMaximumHeight(200)
        
        self.task_input = QLineEdit(self.frame)
        self.add_task_btn = QPushButton(self.frame, text="Добавить задачу")
        self.add_task_btn.clicked.connect(lambda: self.add_task(self.task_input.text()))
        self.finish_task_btn: QPushButton = QPushButton(text="Завершить задачу")
        self.finish_task_btn.clicked.connect(lambda: self.finish_task())
        
        # Размещение созданных виджетов на окне
        self.frame.addWidget(self.task_list)
        self.frame.addWidget(self.task_input)
        self.frame.addWidget(self.add_task_btn)
        self.frame.addWidget(self.finish_task_btn)
        
        self.setCentralWidget(self.frame)
        self.fill_tasklist()
    
    def add_task(self, task: str):
        redis.lpush(f"{self.base_key}_list", task) # В редис добавляем в начало списка
        self.task_list.insertItem(0, task)  # Добавляем в начало
        self.task_input.setText("") # Удаляем задачу из поля ввода
    
    def fill_tasklist(self):
        tasks = redis.lrange(f"{self.base_key}_list", 0, -1) or [] # Получение всего списка
        self.task_list.clear() # Очистка существующих задач из окна
        for task in tasks:
            task_str = task.decode('utf-8') if isinstance(task, bytes) else str(task)
            self.task_list.addItem(task_str) # Добавляем задачи последовательно

    def finish_task(self):
        # Удаляем первый элемент из списка редис
        redis.lpop(f"{self.base_key}_list")
        # Удаляем элемент из начала списка
        self.task_list.takeItem(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
