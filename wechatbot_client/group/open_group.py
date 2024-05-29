import json
import os
import sqlite3


class OpenGroup:
    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd(), "data/group")):
            os.makedirs(os.path.join(os.getcwd(), "data/group"))
        self.dbPath = os.path.join(os.getcwd(), "data/group", "openGroup.db")
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()

    # 是否开通
    async def isOpen(self, group_id):
        sql = "SELECT * FROM openGroup WHERE group_id = ? AND status = 1"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        if result:
            return True
        else:
            return False

    # 开通
    async def open(self, group_id):
        # 是否已经存在
        sql = "SELECT * FROM openGroup WHERE group_id = ?"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchone()
        if result:
            sql2 = "UPDATE openGroup SET status = 1 WHERE group_id = ?"
            self.cursor.execute(sql2, (group_id,))
            self.conn.commit()
            return True
        else:
            sql3 = "INSERT INTO openGroup(group_id, status) VALUES(?, 1)"
            self.cursor.execute(sql3, (group_id,))
            self.conn.commit()
            return True

    # 关闭
    async def close(self, group_id):
        sql = "UPDATE openGroup SET status = 0 WHERE group_id = ?"
        self.cursor.execute(sql, (group_id,))
        self.conn.commit()
        return True
