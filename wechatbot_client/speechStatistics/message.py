import os
import sqlite3
from datetime import datetime
import time


class MessageDb:
    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd(), 'data/speechStatistics')):
            os.makedirs(os.path.join(os.getcwd(), 'data/speechStatistics'))
        self.dbPath = os.path.join(os.getcwd(), 'data/speechStatistics',
                                   'groupMessage.db')
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()
        
   
        self.dbPath_p = os.path.join(os.getcwd(), 'data/speechStatistics',
                                   'privateMessage.db')
        self.conn_p = sqlite3.connect(self.dbPath_p)
        self.cursor_p = self.conn_p.cursor()

    async def listenMessage(self, sender_user_id, sender_user_name, message,
                            time, detail_type, group_id=None, group_name=None):
        if detail_type == "group":
            sql = "INSERT INTO groupMessage (sender_user_id, group_id,\
                message, time, sender_user_name, group_name) VALUES (?,\
                ?, ?, ?, ?, ?) "
            self.cursor.execute(sql, (sender_user_id, group_id, message,
                                      time, sender_user_name,  group_name))
            self.conn.commit()
        else:
            sql = "INSERT INTO privateMessage (sender_user_id,\
                message, time) VALUES (?, ?, ?) "
            self.cursor_p.execute(sql, (sender_user_id, message, time))
            self.conn_p.commit()
        return
    
    async def getMessageRanking_today(self, group_id):
        now = datetime.now().date()
        midnight = datetime.combine(now, datetime.min.time())
        timestamp = int(time.mktime(midnight.timetuple()))
        sql = "select * from groupMessage where group_id = ? and time > ?"
        self.cursor.execute(sql, (group_id, timestamp))
        result = self.cursor.fetchall()
        RankingMap = {}
        for mess in result:
            if mess[1] not in RankingMap:
                RankingMap[mess[1]] = {
                    "number": 1,
                    "user_name": mess[5],
                }
            else:
                RankingMap[mess[1]] = {
                    "number": RankingMap[mess[1]]["number"] + 1,
                    "user_name": mess[5],
                }
        sorted_data = sorted(RankingMap.items(), key=lambda x: x[1]["number"],
                             reverse=True)
        sorted_dict = {k: v for k, v in sorted_data}
        return sorted_dict

    async def getMessageRanking_month(self, group_id):
        # 本月的第一天00:00
        now = datetime.now()
        first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        timestamp = int(time.mktime(first.timetuple()))
        sql = "select * from groupMessage where group_id = ? and time > ?"
        self.cursor.execute(sql, (group_id, timestamp))
        result = self.cursor.fetchall()
        RankingMap = {}
        for mess in result:
            if mess[1] not in RankingMap:
                RankingMap[mess[1]] = {
                    "number": 1,
                    "user_name": mess[5],
                }
            else:
                RankingMap[mess[1]] = {
                    "number": RankingMap[mess[1]]["number"] + 1,
                    "user_name": mess[5],
                }
        sorted_data = sorted(RankingMap.items(), key=lambda x: x[1]["number"],
                             reverse=True)
        sorted_dict = {k: v for k, v in sorted_data}
        return sorted_dict

# 总排行
    async def getMessageRanking_all(self, group_id):
        sql = "select * from groupMessage where group_id = ?"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        RankingMap = {}
        for mess in result:
            if mess[1] not in RankingMap:
                RankingMap[mess[1]] = {
                    "number": 1,
                    "user_name": mess[5],
                }
            else:
                RankingMap[mess[1]] = {
                    "number": RankingMap[mess[1]]["number"] + 1,
                    "user_name": mess[5],
                }
        sorted_data = sorted(RankingMap.items(), key=lambda x: x[1]["number"],
                             reverse=True)
        sorted_dict = {k: v for k, v in sorted_data}
        return sorted_dict