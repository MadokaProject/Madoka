"""有头双向循环链表"""


class ListNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

    def __str__(self):
        return f"<ListNode::data={self.data}>"

    def is_empty(self) -> bool:
        return self.next == self

    def append(self, data):
        s = ListNode(data)
        s.next = self.next
        s.prev = self
        self.next.prev = s
        self.next = s

    def delete(self):
        self.next.prev = self.prev
        self.prev.next = self.next
        del self


class ListIter:
    def __init__(self, head: ListNode):
        self.head = head
        self.curr_node = head.next

    def __next__(self) -> ListNode:
        if self.curr_node == self.head:
            raise StopIteration
        node, self.curr_node = self.curr_node, self.curr_node.next
        return node

    def __iter__(self):
        return self


class ListCreate:
    def __init__(self):
        self.__head = ListNode(None)
        self.__head.next = self.__head
        self.__head.prev = self.__head

    def __iter__(self):
        return ListIter(self.head)

    @property
    def head(self):
        return self.__head

    def is_empty(self) -> bool:
        return self.head.is_empty()

    def push_head(self, data):
        """头插"""
        p = self.head
        p.append(data)

    def pop_head(self):
        """头删"""
        p = self.head.next
        p.delete()

    def push_back(self, data):
        """尾插"""
        p = self.head.prev  # 获取链表尾节点
        p.append(data)

    def pop_back(self):
        """尾删"""
        p = self.head.prev
        p.delete()

    def show(self):
        p = self.head.next
        while p != self.head:
            print(p)
            p = p.next
