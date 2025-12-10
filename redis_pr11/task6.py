"""
2.	Аудиты и логи изменений:
2.1.	Записывать все изменения в систему
2.2.	Реализовать механизм "воспроизведения" события, последовательная выполняя действия записанных логов автоматически
2.3.	Создать потребительские группы в самом Redis, чтобы обработать логи
"""
import sys
import time

from typing import Any
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QLineEdit,
    QPushButton
)
from redis import Redis
from base import AutoLayoutQFrame


redis: Redis = Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


class MainWindow(QMainWindow):
    base_key: str = "task6"
    write_stream_name: str = f"{base_key}:write_logs"
    consumer_group: str = f"{base_key}:replay_group"

    def __init__(self):
        super().__init__()
        self.frame: AutoLayoutQFrame = AutoLayoutQFrame(QVBoxLayout)
        self.input: QLineEdit = QLineEdit()
        self.frame.addWidget(self.input)
        self.frame.addWidget(
             QPushButton(
                 text="Один",
                 clicked=lambda: self.insert_text("Один")
            )
        )
        self.frame.addWidget(
            QPushButton(
                text="Два",
                clicked=lambda: self.insert_text("Два")
            )
        )
        self.frame.addWidget(
            QPushButton(
                text="Три",
                clicked=lambda: self.insert_text("Три")
            )
        )
        self.frame.addWidget(
            QPushButton(
                text="Воспроизвести",
                clicked=lambda: self.replay_logs()
            )
        )
        self.setup_consumer_group()
        self.setCentralWidget(self.frame)

    def setup_consumer_group(self):
        try:
            response = redis.xgroup_create(
                name=self.write_stream_name,
                groupname=self.consumer_group,
                id="0",  # Начать с самого начала
                mkstream=True  # Создать stream если не существует
            )
            print(f"Создана consumer group: {self.consumer_group} {response=}")
        except Exception as e:
            # Группа уже существует
            print(f"Consumer group уже существует: {e} {self.consumer_group=}")

    def insert_text(self, text: str):
        self.input.setText(text)
        self.add_log(
            {
                "action": "text_changed",
                "text": text
            }
        )

    def add_log(self, data: dict[str, Any]):
        try:
            message_id = redis.xadd(
                name=self.write_stream_name,
                fields=data
            )
            print(f"Запись добавлена: {message_id} - {data}")
        except Exception as e:
            print(f"Ошибка записи лога: {e}")

    def replay_logs(self):
        try:
            messages = redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=f"consumer1",
                streams={self.write_stream_name: ">"},
                count=100
            )
            
            if messages:
                for write_stream_name, stream_messages in messages:
                    print(f"Stream: {write_stream_name}")
                    for message_id, message_data in stream_messages:
                        print(f"  ID: {message_id}, Data: {message_data}")
                        
                        # Воспроизводим действие
                        self.replay_action(message_data)
                        
                        # Подтверждаем обработку
                        redis.xack(self.write_stream_name, self.consumer_group, message_id)
                        
                        # Небольшая пауза для наглядности
                        QApplication.processEvents()
                        time.sleep(1)
                
                print(f"=== Воспроизведено {len(stream_messages)} сообщений ===")
            else:
                print("Нет сообщений для воспроизведения")
                
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def replay_action(self, data: dict[str, Any]):
        """Воспроизвести одно действие из лога"""
        action = data.get("action")
        print(f"{action=}")
        if action == "text_changed":
            new_value = data.get("text", "")
            print(f"Воспроизведение: установка текста '{new_value}'")
            
            # 2.2. Последовательное выполнение действий
            self.input.setText(new_value)
            
            # Небольшая задержка для наглядности
            QApplication.processEvents()
            time.sleep(1)


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
