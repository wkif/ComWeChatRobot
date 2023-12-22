import json
import sqlite3
import os


class Group:
    def __init__(self):
        self.groupDbPath = os.path.join(os.getcwd(), 'data/speechStatistics',
                                        'group.db')
        self.groupConn = sqlite3.connect(self.groupDbPath)
        self.groupCursor = self.groupConn.cursor()
        self.personDbPath = os.path.join(os.getcwd(), 'data/speechStatistics',
                                         'person.db')
        self.personConn = sqlite3.connect(self.personDbPath)
        self.personCursor = self.personConn.cursor()

# 更新历史成员列表
    async def updateAllNumberList(self, group_id, current_number_list):
        # 查询 group 表的 all_number_id_list
        sql = "select all_number_id_list from groupDB where group_id = ?"
        self.groupCursor.execute(sql, (group_id,))
        all_number_id_list = self.groupCursor.fetchall()
        if all_number_id_list:
            all_number_id_list = json.loads(all_number_id_list[0][0])
            print("all_number_list")
            print(all_number_id_list)
            # 将 current_number_list 中存在 all_number_id_list 中不存在的成员添加到 all_number_id_list
            for number in current_number_list:
                if number not in all_number_id_list:
                    all_number_id_list.append(number)
            # 更新 all_number_id_list
            sql = "update groupDB set all_number_id_list = ? where group_id = ?"
            self.groupCursor.execute(sql, (json.dumps(all_number_id_list), group_id))
            self.groupConn.commit()
            return True
        else:
            sql = "INSERT INTO groupDB (group_id, all_number_id_list) VALUES (?, ?)"
            self.groupCursor.execute(sql, (group_id,
                                           json.dumps(current_number_list)))
            self.groupConn.commit()
            return True

# 获取退群历史成员
    async def getQuitGroupList(self, group_id, current_number_list):
        QuitGroupList = []
        sql = "select all_number_id_list from groupDB where group_id = ?"
        self.groupCursor.execute(sql, (group_id,))
        all_number_id_list = self.groupCursor.fetchall()
        if all_number_id_list:
            all_number_id_list = json.loads(all_number_id_list[0][0])
            # 将在 all_number_id_list 中但不在 current_number_list 中的成员添加到 QuitGroupList
            for number in all_number_id_list:
                if number not in current_number_list:
                    QuitGroupList.append(number)
            return QuitGroupList
        else:
            return QuitGroupList
