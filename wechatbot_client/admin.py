import os
import sqlite3


class Admin:
    def __init__(self):
        self.dbPath = os.path.join(os.getcwd(), 'data/admin', 'admin.db')
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()

    async def read(self):
        sql = "select * from admin"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        print(result)
        return result

    async def search(self, user_id):
        list = await self.read()
        for i in list:
            if i[2] == user_id:
                return i
        return None

    async def addAdmin(self, name, user_id):
        name = name.replace("@", "")
        sql = "INSERT INTO admin (name, user_id) VALUES (?, ?)"
        self.cursor.execute(sql, (name, user_id))
        self.conn.commit()
        return True

    async def deleteAdmin(self, user_id):
        list = await self.read()
        for i in list:
            if i[2] == user_id:
                sql = "DELETE FROM admin WHERE user_id = ?"
                self.cursor.execute(sql, (user_id,))
                self.conn.commit()
                break
        return True
