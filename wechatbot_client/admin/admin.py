import os
import sqlite3


class Admin:
    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd(), 'data/admin')):
            os.makedirs(os.path.join(os.getcwd(), 'data/admin'))
        self.dbPath = os.path.join(os.getcwd(), 'data/admin', 'admin.db')
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()

    async def read(self, group_id):
        sql = "select * from admin where group_id = ?"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        return result

    async def search(self, user_id, group_id):
        list = await self.read(group_id)
        for i in list:
            if i[1] == user_id:
                return i
        return None

    async def addAdmin(self, name, user_id, group_id):
        list = await self.read(group_id)
        for i in list:
            if i[1] == user_id:
                return 2
        name = name.replace("@", "")
        sql = "INSERT INTO admin (name, user_id, group_id) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (name, user_id, group_id))
        self.conn.commit()
        return 1

    async def deleteAdmin(self, user_id, group_id):
        list = await self.read(group_id)
        for i in list:
            if i[1] == user_id:
                sql = "DELETE FROM admin WHERE user_id = ?"
                self.cursor.execute(sql, (user_id,))
                self.conn.commit()
                return True
        return False

    async def checkIsAdmin(self, user_id, group_id):
        list = await self.read(group_id)
        for i in list:
            if i[1] == user_id:
                return True
        return False
