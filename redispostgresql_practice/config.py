import json
from redis import Redis
from sqlalchemy import (
    create_engine,
    Engine,
    URL
)
from sqlalchemy.orm import sessionmaker


redis_client: Redis = Redis(
    host="localhost",
    port=6379
)

engine: Engine = create_engine(
    url = URL.create(
        # Для mysql использовать drivername="mysql+mysqlconnector"
        drivername=f"postgresql+psycopg2",
        username="postgres",
        password="postgres",
        database="practice_5_redis",
        host="localhost"
    ),
    pool_pre_ping=True,
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
)
app_sessionmaker = sessionmaker(engine) 
