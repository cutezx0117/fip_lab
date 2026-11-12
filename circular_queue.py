# -*- coding: utf-8 -*-
"""循环队列 + 状态追踪  ——  第九周研讨课二 / 项目 A

思路
----
拿一块**固定长度**的数组当一条环形跑道：
    front 指队头（下一个要出队的位置）
    rear  指队尾（下一个要入队的位置）
两个下标都只往前走，走到数组末尾就用 `% capacity` 绕回 0。
这一步"绕回"就是循环队列和普通数组队列的全部区别：
数组从头到尾都不搬家，出队腾出来的格子马上能被入队重新用上。

为什么还要一个 count？
    如果只用 front == rear 判空/判满，两者会打架（空和满长得一模一样）。
    count 记元素个数，判空 count==0、判满 count==capacity，就没有二义性了。

状态追踪
--------
每次操作后存一份快照（front / rear / count / 数组内容），
最后能把整段操作过程打印成一张表 —— 既能调试，也是作业要求的"状态追踪"。

运行：python circular_queue.py
"""


class CircularQueue:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity 必须是正整数")
        self.capacity = capacity
        self.items = [None] * capacity   # 固定长度的数组，None 表示空格子
        self.front = 0                   # 队头下标
        self.rear = 0                    # 队尾下标（下一个空位）
        self.count = 0                   # 当前元素个数
        self.history = []                # 每次操作后的状态快照

    # ---------------- 只读状态 ----------------
    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.capacity

    def size(self):
        return self.count

    def __len__(self):
        return self.count

    def peek(self):
        """看一眼队头元素，但不出队"""
        return None if self.is_empty() else self.items[self.front]

    # ---------------- 入队 / 出队 ----------------
    def enqueue(self, value):
        """入队：成功返回 True，队列满了返回 False（不覆盖旧数据）"""
        if self.is_full():
            self._record(f"enqueue({value})  x 已满，拒绝")
            return False
        self.items[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity   # 关键：% capacity 让末尾绕回 0
        self.count += 1
        self._record(f"enqueue({value})")
        return True

    def dequeue(self):
        """出队：返回队头元素，空队列返回 None"""
        if self.is_empty():
            self._record("dequeue()      x 为空，返回 None")
            return None
        value = self.items[self.front]
        self.items[self.front] = None                 # 清成 None，打印时才看得出"空位"
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        self._record(f"dequeue()   -> {value}")
        return value

    # ---------------- 状态追踪 ----------------
    def snapshot(self):
        return {
            "front": self.front,
            "rear": self.rear,
            "count": self.count,
            "items": list(self.items),
        }

    def _record(self, action):
        self.history.append((action, self.snapshot()))

    def trace(self, title=""):
        """把 history 打印成一张表：每一步操作后队列长什么样"""
        if title:
            print(f"\n{'=' * 66}\n{title}\n{'=' * 66}")
        print(f"{'#':>2}  {'操作':<24}{'front':>5}{'rear':>5}{'count':>6}   缓冲区")
        for i, (action, s) in enumerate(self.history, 1):
            cells = " ".join("·" if v is None else str(v) for v in s["items"])
            print(f"{i:>2}  {action:<24}{s['front']:>5}{s['rear']:>5}{s['count']:>6}   [{cells}]")

    def __str__(self):
        cells = " ".join("·" if v is None else str(v) for v in self.items)
        return (f"CircularQueue(cap={self.capacity}, [{cells}], "
                f"front={self.front}, rear={self.rear}, count={self.count})")


# ==================== 演示 ====================

def demo_basic():
    q = CircularQueue(4)
    for x in (1, 2, 3):
        q.enqueue(x)
    print("出队两次：", q.dequeue(), q.dequeue())
    q.trace("演示 1：基本入队 / 出队（front 和 rear 一起往后走）")
    print("当前队列状态：", q)


def demo_wraparound():
    q = CircularQueue(4)
    for x in (1, 2, 3, 4):
        q.enqueue(x)      # rear 从 0 走到 4（第 4 次入队后 rear 绕回 0，队列满）
    q.dequeue()           # 出掉 1，front -> 1
    q.dequeue()           # 出掉 2，front -> 2，空出 [0] 和 [1] 两格
    q.enqueue(5)          # rear 从 0 开始，写进 [0]
    q.enqueue(6)          # 再写进 [1]，两格刚好补满
    q.trace("演示 2：绕回 —— rear 从 3 直接回到 0，补进刚空出来的两格")
    print("队列状态：", q)
    assert q.items == [5, 6, 3, 4], q.items
    assert q.size() == 4 and q.is_full()


def demo_no_growth():
    q = CircularQueue(8)
    for i in range(10000):
        q.enqueue(i)
        q.enqueue(i)
        q.dequeue()
        q.dequeue()
    print(f"\n演示 3：容量 {q.capacity}，跑了 4 万次操作，"
          f"底层数组长度仍然是 {len(q.items)}（一次都没扩容）")
    assert len(q.items) == 8


def demo_vs_deque():
    """随机对拍：和 collections.deque 的行为逐操作比对"""
    import random
    from collections import deque

    random.seed(7)
    for _ in range(300):
        cap = random.randint(1, 6)
        q = CircularQueue(cap)
        ref = deque()                      # 标准库队列，当"正确答案"
        for _ in range(200):
            if random.random() < 0.6:
                v = random.randint(0, 99)
                ok = q.enqueue(v)
                if len(ref) < cap:
                    ref.append(v)
                    assert ok is True
                else:
                    assert ok is False     # 满了要拒绝，不能覆盖队头
            else:
                got = q.dequeue()
                want = ref.popleft() if ref else None
                assert got == want, (cap, list(ref), got, want)
            assert q.size() == len(ref)
            assert q.is_full() == (len(ref) == cap)
            assert q.peek() == (ref[0] if ref else None)
    print("演示 4：300 组随机操作与 collections.deque 对拍，全部一致")


if __name__ == "__main__":
    demo_basic()
    demo_wraparound()
    demo_no_growth()
    demo_vs_deque()
    print("\n全部断言通过 √")
