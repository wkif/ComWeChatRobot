import os
import sqlite3
from datetime import datetime
import time


class GroupMessage:
    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd(), "data/group")):
            os.makedirs(os.path.join(os.getcwd(), "data/group"))
        self.dbPath = os.path.join(os.getcwd(), "data/group", "groupMessage.db")
        self.conn = sqlite3.connect(self.dbPath)
        self.cursor = self.conn.cursor()

    async def listenMessage(
        self, sender_user_id, sender_user_name, message, time, group_id, group_name
    ):

        sql = "INSERT INTO groupMessage (sender_user_id, group_id,\
                message, time, sender_user_name, group_name) VALUES (?,\
                ?, ?, ?, ?, ?) "
        self.cursor.execute(
            sql,
            (sender_user_id, group_id, message, time, sender_user_name, group_name),
        )
        self.conn.commit()

    async def getMessageRanking_today(self, group_id):
        now = datetime.now().date()
        midnight = datetime.combine(now, datetime.min.time())
        timestamp = int(time.mktime(midnight.timetuple()))
        sql = "select * from groupMessage where group_id = ? and time > ?"
        self.cursor.execute(sql, (group_id, timestamp))
        result = self.cursor.fetchall()
        RankingMap = {}
        for mess in result:
            (
                _,
                sender_user_id,
                sender_user_name,
                _,
                _,
                _,
                _,
            ) = mess
            if sender_user_id not in RankingMap:
                RankingMap[sender_user_id] = {
                    "number": 1,
                    "user_name": sender_user_name,
                }
            else:
                RankingMap[sender_user_id] = {
                    "number": RankingMap[sender_user_id]["number"] + 1,
                    "user_name": sender_user_name,
                }
        sorted_data = sorted(
            RankingMap.items(), key=lambda x: x[1]["number"], reverse=True
        )
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
            (
                _,
                sender_user_id,
                sender_user_name,
                _,
                _,
                _,
                _,
            ) = mess
            if sender_user_id not in RankingMap:
                RankingMap[sender_user_id] = {
                    "number": 1,
                    "user_name": sender_user_name,
                }
            else:
                RankingMap[sender_user_id] = {
                    "number": RankingMap[sender_user_id]["number"] + 1,
                    "user_name": sender_user_name,
                }
        sorted_data = sorted(
            RankingMap.items(), key=lambda x: x[1]["number"], reverse=True
        )
        sorted_dict = {k: v for k, v in sorted_data}
        return sorted_dict

    # 总排行
    async def getMessageRanking_all(self, group_id):
        sql = "select * from groupMessage where group_id = ?"
        self.cursor.execute(sql, (group_id,))
        result = self.cursor.fetchall()
        RankingMap = {}
        for mess in result:
            (
                _,
                sender_user_id,
                sender_user_name,
                _,
                _,
                _,
                _,
            ) = mess
            if sender_user_id not in RankingMap:
                RankingMap[sender_user_id] = {
                    "number": 1,
                    "user_name": sender_user_name,
                }
            else:
                RankingMap[sender_user_id] = {
                    "number": RankingMap[sender_user_id]["number"] + 1,
                    "user_name": sender_user_name,
                }
        sorted_data = sorted(
            RankingMap.items(), key=lambda x: x[1]["number"], reverse=True
        )
        sorted_dict = {k: v for k, v in sorted_data}
        return sorted_dict
