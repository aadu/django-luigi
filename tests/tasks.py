from luigi import Task, LocalTarget


class DummyTask(Task):
    def output(self):
        return LocalTarget('example.txt')

    def run(self):
        with open('example.txt', 'w') as f:
            f.write("Hey")


if __name__ == '__main__':
    t = DummyTask()
    t.run()
