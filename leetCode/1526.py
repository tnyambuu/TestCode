from typing import List
from collections import defaultdict

class Solution:

    def sortFunc(self, e):
        return  e["value"]


    def minNumberOperations(self, target: List[int]) -> int:
        op_list = [0] * len(target)
        op_count = 0
        op_change_list = []
        target_clone = []
        target_clone_obj = []
        group_target = defaultdict(list)

        for idx, value in enumerate(target):
            target_clone.append({
                "old_pos": idx,
                "value": value
            })

        #sort by value
        target_clone.sort(key=self.sortFunc)

        #group by value
        for value in target_clone:
            group_target[value["value"]].append(value)

        for idx, grouped_value in enumerate(group_target):
            if idx == 0:
                for value, value_list in grouped_value.items():
                    op_list = [int(value) for op_list_value in op_list]
                    op_count += int(value)
            else:
                op_list[grouped_value["old_pos"]] = grouped_value["value"] - group_target[idx - 1]["value"]

        print(group_target)

        return target_clone[0]

if __name__ == '__main__':
    obj = Solution()
    print(obj.minNumberOperations([3, 1, 5, 4, 2, 5, 8, 4]))
