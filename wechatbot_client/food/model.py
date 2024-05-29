from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger
class Food(Model):
    id = fields.IntField(pk=True, generated=True)
    user_id = fields.CharField(max_length=255)
    user_name = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)
    food_name = fields.CharField(max_length=255)
    table = "food"
    table_description = "食物表"
    def __str__(self):
        return self.food_name
    

async def fooddatabase_init() -> None:
    """
    数据库初始化
    """
    logger.debug("<y>正在注册Food数据库...</y>")
    Path(f"./{DATABASE_PATH}").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/food/food.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.food.model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>Food数据库初始化成功...</g>")
async def fooddatabase_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()