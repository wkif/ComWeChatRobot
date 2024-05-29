import random
import os
import sqlite3


class Food:
    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd(), 'data/food')):
            os.makedirs(os.path.join(os.getcwd(), 'data/food'))
        self.dbPath = os.path.join(os.getcwd(), 'data/food', 'food.db')
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()
        
    async def getList(self, type):
        sql = "select * from food where type = ?"
        self.cursor.execute(sql, (type,))
        result = self.cursor.fetchall()
        return result

# 新增数据
    async def addFood(self, user_id, username, food, type):
        list = await self.getList(type)
        for fo in list:
            if fo[1] == food:
                return False
        sql = "insert into food(user_id,user_name, type, food_name) values(?, ?, ?, ?)"
        self.cursor.execute(sql, (user_id, username, type, food))
        self.conn.commit()
        return True

# # 删除数据
#     async def deleteFood(self, food):
#         list = await self.getList()
#         print(list)
#         for fo in list:
#             print(fo[1])
#             if fo[1] == food:
#                 sql = "delete from food where food_name = ?"
#                 self.cursor.execute(sql, (food,))
#                 self.conn.commit()
#                 return True
#         return False

# 随机返回一条数据
    async def getRandomFood(self, type):
        list = await self.getList(type)
        length = len(list)
        # 0-length-1 随机一个数据
        index = random.randint(0, length - 1)
        return list[index]
