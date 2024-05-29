from pathlib import Path
from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger


class OPENGROUPDB(Model):
    id = fields.IntField(pk=True, generated=True)
    group_id = fields.CharField(max_length=255)
    status = fields.IntField()

    table = "openGroup"
    table_description = "群组开通表"

    class Meta:
        table = "openGroup"
        table_description = "群组开通表"


async def opengroup_database_init() -> None:
    """
    数据库初始化
    """
    logger.debug("<y>正在注册openGroupDB数据库...</y>")
    Path(f"./{DATABASE_PATH}/group/").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/group/openGroup.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.group.open_group_model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>openGroupDB数据库初始化成功...</g>")


async def opengroup_database_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()
