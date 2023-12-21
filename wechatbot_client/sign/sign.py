import json
import os
import datetime
import sqlite3


class Sign:
    def __init__(self):
        self.dbPath = os.path.join(os.getcwd(), 'data/sign', 'sign.db')
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()
        
    async def getList(self):
        sql = "select * from sign"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        print(result)
        return result
    
    async def signIn(self, user_id):
        exit = False
        list = await self.getList()
        for item in list:
            if item[1] == user_id:
                exit = True
                status = 0
                # 获取当前年月日并格式化 YYYY-MM-DD
                currentDate = datetime.date.today().strftime("%Y-%m-%d")
                sign_date = json.loads(item[3])
                if currentDate in sign_date:
                    status = 0
                else:
                    sign_date.append(currentDate)
                    # item['sign_count'] += 1
                    status = 1
                    sql = "update sign set sign_count = ?, sign_date = ? where user_id = ?"
                    self.cursor.execute(sql, (item[2] + 1, json.dumps(sign_date), user_id))
                    self.conn.commit()
                    # f = open(self.filePath, 'w')
                    # f.write(json.dumps(list))
                    # f.close()
                count = 1
                preDate = datetime.datetime.strptime(currentDate, "%Y-%m-%d") - datetime.timedelta(days=1)
                # 判断 preDate 是否在 item['sign_date'] 中
                while preDate.strftime("%Y-%m-%d") in sign_date:
                    count += 1
                    preDate = preDate - datetime.timedelta(days=1)
                return {
                    "status": status,
                    "sign_count": item[2],
                    "count": count
                }
                break
        if not exit:
            currentDate = datetime.date.today().strftime("%Y-%m-%d")
            # obj = {
            #     "user_id": user_id,
            #     "sign_count": 1,
            #     "sign_date": [currentDate]
            # }
            # list.append(obj)
            # f = open(self.filePath, 'w')
            # f.write(json.dumps(list))
            # f.close()
            sql = "insert into sign (user_id, sign_count, sign_date) values (?, ?, ?)"
            self.cursor.execute(sql, (user_id, 1, json.dumps([currentDate])))
            self.conn.commit()
            return {
                "status": 1,
                "sign_count": item[2],
                "count": 1
            }