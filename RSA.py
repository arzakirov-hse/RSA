# -*- coding: utf-8 -*-
"""
==========================================================
РЕАЛИЗАЦИЯ КРИПТОСИСТЕМЫ RSA
==========================================================

Функциональность:
1. Генерация ключевой пары
2. Ручной ввод параметров RSA (p, q, e)
3. Шифрование файлов
4. Расшифрование файлов
5. Блочная обработка данных

ВАЖНО:
Данная реализация является учебной:
- не используется padding (OAEP)
- не предназначена для реальной защиты данных
"""

import random


# ============================================================
# МАТЕМАТИЧЕСКИЕ ФУНКЦИИ
# ============================================================

def gcd(a, b):
    """
    Нахождение наибольшего общего делителя (НОД)
    с помощью алгоритма Евклида.

    Используется для проверки:
    gcd(e, φ(n)) = 1
    """
    while b != 0:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.

    Позволяет найти такие x и y:
        ax + by = gcd(a, b)

    Возвращает:
    (g, x, y)
    """
    if b == 0:
        return a, 1, 0

    g, x1, y1 = extended_gcd(b, a % b)

    x = y1
    y = x1 - (a // b) * y1

    return g, x, y


def mod_inverse(e, phi):
    """
    Нахождение обратного элемента по модулю.

    Находит d:
        e * d ≡ 1 (mod φ(n))
    """
    g, x, _ = extended_gcd(e, phi)

    if g != 1:
        raise Exception("Ошибка: e не взаимно просто с φ(n)")

    return x % phi


def mod_exp(base, exp, mod):
    """
    Быстрое возведение в степень по модулю.

    Вычисляет:
        base^exp mod mod

    Используется в RSA:
    - шифрование: m^e mod n
    - расшифрование: c^d mod n
    """
    result = 1
    base %= mod

    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod

        base = (base * base) % mod
        exp //= 2

    return result


# ============================================================
# ПРОВЕРКА ПРОСТОТЫ (Миллер-Рабин)
# ============================================================

def is_prime(n, k=5):
    """
    Вероятностный тест простоты.

    k — количество итераций
    """
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11]
    for p in small_primes:
        if n % p == 0:
            return n == p

    # представление n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = mod_exp(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits=512):
    """
    Генерация случайного простого числа.

    bits — длина числа в битах
    """
    while True:
        p = random.getrandbits(bits)

        # делаем число нечётным и нужной длины
        p |= (1 << bits - 1) | 1

        if is_prime(p):
            return p


# ============================================================
# ГЕНЕРАЦИЯ КЛЮЧЕЙ
# ============================================================

def generate_keys(bits=512):
    """
    Автоматическая генерация ключей RSA.
    """
    p = generate_prime(bits)
    q = generate_prime(bits)

    while p == q:
        q = generate_prime(bits)

    return generate_keys_manual(p, q, 65537)


def generate_keys_manual(p, q, e):
    """
    Генерация ключей из заданных параметров.
    """
    n = p * q
    phi = (p - 1) * (q - 1)

    if gcd(e, phi) != 1:
        raise Exception("e должно быть взаимно простым с φ(n)")

    d = mod_inverse(e, phi)

    return (e, n), (d, n)


# ============================================================
# РАБОТА С БЛОКАМИ
# ============================================================

def get_block_size(n):
    """
    Определение размера блока.

    Условие:
        m < n

    Поэтому:
        размер блока = длина n в байтах - 1
    """
    size = (n.bit_length() // 8) - 1
    return max(1, size)


# ============================================================
# ШИФРОВАНИЕ
# ============================================================

def encrypt_file(infile, outfile, e, n):
    """
    Шифрование файла.

    1. Читаем файл
    2. Делим на блоки
    3. Каждый блок -> число
    4. Применяем RSA
    """
    with open(infile, "rb") as f:
        data = f.read()

    block_size = get_block_size(n)

    encrypted = []

    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]

        # преобразование блока в число
        m = int.from_bytes(block, 'big')

        # RSA
        c = mod_exp(m, e, n)

        encrypted.append(str(c))

    with open(outfile, "w") as f:
        f.write(" ".join(encrypted))


# ============================================================
# РАСШИФРОВАНИЕ
# ============================================================

def decrypt_file(infile, outfile, d, n):
    """
    Расшифрование файла.

    1. Читаем числа
    2. Применяем RSA
    3. Преобразуем в байты
    """
    with open(infile, "r") as f:
        data = f.read().split()

    block_size = get_block_size(n)

    decrypted = bytearray()

    for num in data:
        c = int(num)

        # RSA
        m = mod_exp(c, d, n)

        # обратно в байты
        block = m.to_bytes(block_size, 'big')

        decrypted.extend(block.lstrip(b'\x00'))

    with open(outfile, "wb") as f:
        f.write(decrypted)


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def main():
    """
    Главное меню программы.
    """

    while True:
        print("\n===== RSA МЕНЮ =====")
        print("1. Сгенерировать ключи")
        print("2. Ввести p, q, e вручную")
        print("3. Зашифровать файл")
        print("4. Расшифровать файл")
        print("0. Выход")

        choice = input("Выберите действие: ")

        # ----------------------------------
        # Генерация ключей
        # ----------------------------------
        if choice == "1":
            bits = int(input("Введите размер ключа (например 256 или 512): "))
            public, private = generate_keys(bits)

            print("\nОткрытый ключ (e, n):", public)
            print("Закрытый ключ (d, n):", private)

        # ----------------------------------
        # Ручной ввод
        # ----------------------------------
        elif choice == "2":
            p = int(input("Введите p: "))
            q = int(input("Введите q: "))
            e = int(input("Введите e: "))

            public, private = generate_keys_manual(p, q, e)

            print("\nОткрытый ключ:", public)
            print("Закрытый ключ:", private)

        # ----------------------------------
        # Шифрование
        # ----------------------------------
        elif choice == "3":
            infile = input("Входной файл: ")
            outfile = input("Выходной файл: ")

            e = int(input("Введите e: "))
            n = int(input("Введите n: "))

            encrypt_file(infile, outfile, e, n)

            print("Файл зашифрован.")

        # ----------------------------------
        # Расшифрование
        # ----------------------------------
        elif choice == "4":
            infile = input("Входной файл: ")
            outfile = input("Выходной файл: ")

            d = int(input("Введите d: "))
            n = int(input("Введите n: "))

            decrypt_file(infile, outfile, d, n)

            print("Файл расшифрован.")

        elif choice == "0":
            break

        else:
            print("Ошибка ввода!")


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    main()