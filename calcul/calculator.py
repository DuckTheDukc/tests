class Calculator:
    def __init__(self):
        pass

    def plus(self, x, y):
        return x+y

    def minus(self, x, y):
        return x-y

    def multiply(self, x,y):
        return x * y

    def divide(self, x, y):
        if y != 0:
            return x/y
        else:
           return "на 0 делить нельзя"


