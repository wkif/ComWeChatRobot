from pathlib import Path
from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger
class GROUPDB(Model):
    id = fields.IntField(pk=True, generated=True)
    # group_id
    group_id = fields.CharField(max_length=255, null=True)
    # all_number_id_list
    all_number_id_list = fields.CharField(max_length=255, null=True)
    
    class Meta:
        table = "groupDB"
        table_description = "群组表"
        
class PERSON(Model):
    id = fields.IntField(pk=True, generated=True)

async def groupdatabase_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()


async def groupdatabase_init() -> None:
    """
    数据库初始化
    """
    logger.debug("<y>正在注册group数据库...</y>")
    Path(f"./{DATABASE_PATH}/speechStatistics/").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/speechStatistics/group.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.group.model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>group数据库初始化成功...</g>")
    