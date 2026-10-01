def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def subtract(a, b):
    return a - b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


if __name__ == "__main__":
    print("Python CI/CD Demo")
    print("2 + 3 =", add(2, 3))
    print("2 * 3 =", multiply(2, 3))
    print("5 - 2 =", subtract(5, 2))
    print("10 / 2 =", divide(10, 2))
