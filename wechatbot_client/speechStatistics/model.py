from pathlib import Path
from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger
class OPENGROUPDB(Model):
    id = fields.IntField(pk=True, generated=True)
    # group_id
    group_id = fields.CharField(max_length=255)
    # status
    recordChatStatus = fields.IntField()
    status = fields.IntField()
    
    table = "openGroup"
    table_description = "群组开通表"
    
    class Meta:
        table = "openGroup"
        table_description = "群组开通表"

async def opengroupdatabase_init() -> None:
    """
    数据库初始化
    """
    logger.debug("<y>正在注册openGroupDB数据库...</y>")
    Path(f"./{DATABASE_PATH}/speechStatistics/").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/speechStatistics/openGroup.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.speechStatistics.model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>openGroupDB数据库初始化成功...</g>")
async def opengroupdatabase_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()
    
class groupMessage(Model):
        id = fields.IntField(pk=True, generated=True)
        sender_user_id = fields.CharField(max_length=255)
        sender_user_name = fields.CharField(max_length=255)
        group_id = fields.CharField(max_length=255)
        group_name = fields.CharField(max_length=255)
        message = fields.CharField(max_length=255)
        time = fields.CharField(max_length=255)
        table = "groupMessage"
        table_description = "群组消息表"
        
        class Meta:
            table = "groupMessage"
            table_description = "群组消息表"
            
async def groupmessage_init() -> None:
        """
        数据库初始化
        """
        logger.debug("<y>正在注册groupMessage数据库...</y>")
        Path(f"./{DATABASE_PATH}/speechStatistics/").mkdir(exist_ok=True)
        database_path = f"./{DATABASE_PATH}/speechStatistics/groupMessage.db"
        db_url = f"sqlite://{database_path}"
        # 这里填要加载的表
        models = [
            "wechatbot_client.speechStatistics.model",
        ]
        modules = {"models": models}
        await Tortoise.init(db_url=db_url, modules=modules)
        await Tortoise.generate_schemas()
        logger.info("<g>groupMessage数据库初始化成功...</g>")

async def groupmessage_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()
    
class privateMessage(Model):
        id = fields.IntField(pk=True, generated=True)
        sender_user_id = fields.CharField(max_length=255)
        message = fields.CharField(max_length=255)
        time = fields.CharField(max_length=255)
        table = "privateMessage"
        table_description = "私聊消息表"
        
        class Meta:
            table = "privateMessage"
            table_description = "私聊消息表"

async def privatemessage_init() -> None:
        """
        数据库初始化
        """
        logger.debug("<y>正在注册privateMessage数据库...</y>")
        Path(f"./{DATABASE_PATH}/speechStatistics/").mkdir(exist_ok=True)
        database_path = f"./{DATABASE_PATH}/speechStatistics/privateMessage.db"
        db_url = f"sqlite://{database_path}"
        # 这里填要加载的表
        models = [
            "wechatbot_client.speechStatistics.model",
        ]
        modules = {"models": models}
        await Tortoise.init(db_url=db_url, modules=modules)
        await Tortoise.generate_schemas()
        logger.info("<g>privateMessage数据库初始化成功...</g>")

async def privatemessage_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()