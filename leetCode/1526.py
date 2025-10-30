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

        target_clone.sort(key=self.sortFunc)

        for value in target_clone:
            group_target[value["value"]].append(value)

        print(group_target)

        return target_clone[0]

if __name__ == '__main__':
    obj = Solution()
    print(obj.minNumberOperations([3, 1, 5, 4, 2, 5, 8, 4]))
