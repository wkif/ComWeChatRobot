import os
import sqlite3


class Admin:
    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd(), "data/admin")):
            os.makedirs(os.path.join(os.getcwd(), "data/admin"))
        self.dbPath = os.path.join(os.getcwd(), "data/admin", "admin.db")
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()

    async def read(self):
        sql = "select * from admin"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    async def search(self, user_id):
        list = await self.read()
        for i in list:
            if i[2] == user_id:
                return i
        return None

    async def searchByGroup(self, group_id):
        sql = "select * from admin where group_id = ?"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        return result

    async def isAdmin(self, user_id, group_id):
        sql = "select * from admin where user_id = ? and group_id = ?"
        self.cursor.execute(sql, (user_id, group_id))
        result = self.cursor.fetchall()
        if result:
            return True
        else:
            return False

    async def addAdmin(self, user_id, group_id, name="admin"):
        name = name.replace("@", "")
        sql = "INSERT INTO admin (name, user_id, group_id) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (name, user_id, group_id))
        self.conn.commit()
        return True

    async def deleteAdmin(self, user_id, group_id):
        # list = await self.read()
        # for i in list:
        #     if i[2] == user_id and i[1] == group_id:
        #         sql = "DELETE FROM admin WHERE user_id = ? AND group_id = ?"
        #         self.cursor.execute(sql, (user_id, group_id))
        #         self.conn.commit()
        #         break
        # return True
        sql = "DELETE FROM admin WHERE user_id = ? AND group_id = ?"
        self.cursor.execute(sql, (user_id, group_id))
        self.conn.commit()
        return True
