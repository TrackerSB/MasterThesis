class Super:
    from abc import abstractmethod

    def __init__(self) -> None:
        print("Super::init")
        self.func_res = self.func()

    @abstractmethod
    def func(self) -> int:
        pass


class Sub(Super):
    def __init__(self):
        super().__init__()
        print("Sub::init")

    def func(self) -> int:
        return 42


if __name__ == '__main__':
    print(Sub().func_res)
