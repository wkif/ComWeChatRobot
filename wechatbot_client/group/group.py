import json
import os


class Group:
    def __init__(self):
        self.filePath = os.path.join(os.getcwd(), 'data', 'groupnumber.json')
    # 获取退群成员列表

    async def getQuitGroupList(self, group_id, current_number_list):
        f = open(self.filePath, 'r')
        content = f.read()
        all = json.loads(content)
        hasExit = False
        for group in all:
            if group['group_id'] == group_id:
                hasExit = True
                # 将 current_number_list 中存在 而all_number_list 中不存在的成员添加到
                # all_number_list
                for j in current_number_list:
                    if j not in group['all_number_list']:
                        group['all_number_list'].append(j)
                list = []
                # 将 all_number_list 中存在 而current_number_list 中不存在的成员添加到list
                for k in group['all_number_list']:
                    if k not in current_number_list:
                        list.append(k)
                f = open(self.filePath, 'w')
                f.write(json.dumps(all))
                f.close()
                return list
        if not hasExit:
            group = {}
            group['group_id'] = group_id
            group['all_number_list'] = current_number_list
            all.append(group)
            f = open(self.filePath, 'w')
            f.write(json.dumps(all))
            f.close()
        return None