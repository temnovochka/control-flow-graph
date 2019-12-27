def compareTo(x, y):
    a = x + y
    if a > 0:
        result = 1
    elif a < 0:
        result = -1
    else:
        result = 0
    return result


def cycle_something():
    x = 0
    z = 0
    while x < 10:
        x += compareTo(x, z)
        z += x
        x += 1
    return z


def for_cycle():
    x = 1
    for i in range(10):
        x *= i
        if x > 100:
            break
    return x


def for_if(x):
    for i in range(10):
        if x == i:
            print('good')
    return x


def for_while():
    x = 1
    for i in range(10):
        while x < 10:
            x *= i
        x += 10 + i
    return x


def multiple_returns():
    x = 0
    while x < 10:
        if x == 20:
            return 20
        elif x == 50:
            return x
        else:
            x += 1
            continue
        x *= 20
    return x
