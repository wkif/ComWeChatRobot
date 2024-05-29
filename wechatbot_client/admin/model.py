from pathlib import Path
from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger
class ADMIN(Model):
    id = fields.IntField(pk=True, generated=True)
    # group_id
    group_id = fields.TextField()
    user_id = fields.TextField()
    name = fields.TextField()
    
    class Meta:
        table = "admin"
        table_description = "管理员表"
        
async def adminbase_init():
    """
    数据库初始化
    """
    logger.debug("<y>正在注册admin数据库...</y>")
    Path(f"./{DATABASE_PATH}/admin/").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/admin/admin.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.admin.model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>admin数据库初始化成功...</g>")
async def adminbase_close():
    await Tortoise.close_connections()