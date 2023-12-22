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

# 群组开启功能
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

# 群组关闭功能
    async def deleteOpenGroupList(self, group_id):
        list = await self.getOpenGroupList()
        for i in list:
            if i[1] == group_id:
                sql = "update openGroup set status = 0 where group_id = ?"
                self.cursor.execute(sql, (group_id,))
                self.conn.commit()
                return True
        return False

# 是否开通功能
    async def checkOpenGroupList(self, group_id):
        sql = "select * from openGroup where group_id = ? and status = 1"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        if result:
            return True
        else:
            return False

# 开启记录
    async def startRecordChat(self, group_id):
        list = await self.getOpenGroupList()
        for i in list:
            if i[1] == group_id:
                if i[3] == 1:
                    return 2
                else:
                    sql = "update openGroup set recordChatStatus = 1 where group_id = ?"
                    self.cursor.execute(sql, (group_id,))
                    self.conn.commit()
                    return 1
        sql = "INSERT INTO openGroup (group_id, status, recordChatStatus) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (group_id, 0, 1))
        self.conn.commit()
        return 1

# 关闭记录
    async def stopRecordChat(self, group_id):
        list = await self.getOpenGroupList()
        for i in list:
            if i[1] == group_id:
                if i[3] == 0:
                    return 2
                sql = "update openGroup set recordChatStatus = 0 where group_id = ?"
                self.cursor.execute(sql, (group_id,))
                self.conn.commit()
                return 1
        return 0

# 是否开启记录
    async def checkRecordChat(self, group_id):
        sql = "select * from openGroup where group_id = ? and recordChatStatus = 1"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        if result:
            return True
        else:
            return False
