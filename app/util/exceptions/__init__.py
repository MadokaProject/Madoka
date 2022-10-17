class Error(Exception):
    """Base class for Madoka exceptions"""

    def __init__(self, msg=""):
        self.msg = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.msg

    __str__ = __repr__


class AsyncioTasksGetResultError(Error):
    """task得到结果提前结束"""

    def __init__(self, task):
        Error.__init__(self, "Task %r get result too early" % task)
        self.task = task
        self.args = (task,)
