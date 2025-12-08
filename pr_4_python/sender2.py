import aio_pika
import asyncio
import json

from custom_types import RabbitMQCredentials, RabbitMQManager


credintails: RabbitMQCredentials = RabbitMQCredentials(
    host="localhost",
    port=5672,
    login="guest",
    password="guest"
)
rmq_manager: RabbitMQManager = RabbitMQManager(credintails)

user1_queue: str = "task4_user1_messages"
user2_queue: str = "task4_user2_messages"


async def on_message(message: aio_pika.IncomingMessage):
    try:
        async with message.process():
            body = json.loads(message.body)
            print(body)
            answer: str = input("Введите ваш ответ: ")
            await rmq_manager.send_message_to_queue(
                queue_name=user1_queue,
                message=answer
            )
    except asyncio.CancelledError:
        # Фоновые таски могут быть отменены при shutdown loop
       print("Callback on_message был отменён")
    except Exception as e:
        # Любые другие ошибки при обработке сообщения
        print(f"Ошибка при обработке RMQ сообщения: {e}")


async def main():
    await rmq_manager.connect()
    await rmq_manager.register_callback_on_queue(
        queue_name=user2_queue,
        callback=on_message
    )

    try:
        await asyncio.Event().wait()  # держим loop открытым
    finally:
        await rmq_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
