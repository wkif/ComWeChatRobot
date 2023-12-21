import json
import os
import sqlite3


class SpeechStatistics:
    def __init__(self):
        self.dbPath = os.path.join(os.getcwd(), 'data/speechStatistics',
                                   'openGroup.db')
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()
# 获取开通发言记录列表

    async def getOpenGroupList(self):
        sql = "select * from openGroup"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
        # with open(self.open_group_file_path, 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        #     f.close()
        #     return data

# 增加开通发言记录群组
    async def addOpenGroupList(self, group_id):
        list = await self.getOpenGroupList()
        for i in list:
            if i[1] == group_id:
                sql = "update openGroup set status = 1 where group_id = ?"
                self.cursor.execute(sql, (group_id,))
                self.conn.commit()
                return True
        sql = "INSERT INTO openGroup (group_id, status) VALUES (?, ?)"
        self.cursor.execute(sql, (group_id, 1))
        self.conn.commit()
        return True

# 移除开通发言记录群组
    async def deleteOpenGroupList(self, group_id):
        list = await self.getOpenGroupList()
        for i in list:
            if i[1] == group_id:
                sql = "update openGroup set status = 0 where group_id = ?"
                self.cursor.execute(sql, (group_id,))
                self.conn.commit()
                return True
        return False

# 是否开通
    async def changeOpenGroupList(self, group_id):
        sql = "select * from openGroup where group_id = ? and status = 1"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        if result:
            return True
        else:
            return False

# 聊天记录
    async def statistics(self, group_id):
        Json_path = os.path.join(self.file_base_path, group_id, 'data.json')
        # 判断文件存在不存在，不存在就创建
        if not os.path.exists(Json_path):
            with open(Json_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
                f.close()
        f = open(Json_path, 'r')
        content = f.read()
        list = json.loads(content)
        f.close()
        pass
