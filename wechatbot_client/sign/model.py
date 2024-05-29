from pathlib import Path
from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger


class SIGN(Model):
    id = fields.IntField(pk=True, generated=True)
    user_id = fields.CharField(max_length=255)
    sign_date = fields.CharField(max_length=255)
    sign_count = fields.IntField()

    table = "sign"
    table_description = "签到表"

    class Meta:
        table = "sign"
        table_description = "签到表"


async def signdatabase_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()


async def signdatabase_init() -> None:
    """
    数据库初始化
    """
    logger.debug("<y>正在注册sign数据库...</y>")
    Path(f"./{DATABASE_PATH}/sign/").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/sign/sign.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.sign.model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>sign数据库初始化成功...</g>")
