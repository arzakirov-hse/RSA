# -*- coding: utf-8 -*-
import math


# =========================================================
# МАТЕМАТИЧЕСКИЕ ФУНКЦИИ
# =========================================================

def gcd(a, b):
    """НОД двух чисел (алгоритм Евклида)"""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает (g, x, y), где:
    a*x + b*y = g = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(e, phi):
    """Обратный элемент e mod phi"""
    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        raise Exception("Обратного элемента не существует")
    return x % phi


# =========================================================
# 1. АТАКА ФЕРМА (ФАКТОРИЗАЦИЯ n)
# =========================================================

def fermat_factor(n):
    """
    Факторизация числа методом Ферма.
    Работает эффективно, если p и q близки.
    """
    a = math.isqrt(n)

    if a * a < n:
        a += 1

    while True:
        b2 = a * a - n
        b = math.isqrt(b2)

        if b * b == b2:
            p = a - b
            q = a + b
            return p, q

        a += 1


def fermat_attack():
    print("\n=== АТАКА ФЕРМА ===")

    n = int(input("Введите n: "))
    e = int(input("Введите e: "))

    p, q = fermat_factor(n)

    print("\nНайденные множители:")
    print("p =", p)
    print("q =", q)

    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)

    print("\nВосстановленный закрытый ключ:")
    print("d =", d)
    print("n =", n)


# =========================================================
# 2. АТАКА НА МАЛУЮ ЭКСПОНЕНТУ (LOW EXPONENT)
# =========================================================

def integer_root(c, e):
    """
    Поиск точного e-го корня (без библиотек).
    """
    low = 0
    high = c

    while low <= high:
        mid = (low + high) // 2
        val = mid ** e

        if val == c:
            return mid
        elif val < c:
            low = mid + 1
        else:
            high = mid - 1

    return None


def low_exponent_attack():
    print("\n=== LOW EXPONENT ATTACK ===")

    c = int(input("Введите шифртекст c: "))
    e = int(input("Введите e: "))
    n = int(input("Введите n: "))

    if c >= n:
        print("Атака невозможна: c >= n")
        return

    m = integer_root(c, e)

    print("\nРезультат атаки:")
    print("m =", m)


# =========================================================
# МЕНЮ
# =========================================================

def main():
    while True:
        print("\n============================")
        print("      RSA ATTACK TOOL")
        print("============================")
        print("1. Атака Ферма (факторизация n)")
        print("2. Low Exponent Attack")
        print("0. Выход")

        choice = input("Выбор: ")

        if choice == "1":
            fermat_attack()

        elif choice == "2":
            low_exponent_attack()

        elif choice == "0":
            break

        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()