import random
from sympy import isprime, mod_inverse

def generate_prime(bits):   #Генерирует случайное число с заданным количеством бит
    while True:
        num = random.getrandbits(bits)
        if isprime(num):    #проверяет, является ли переданное число простым
            return num

def generate_rsa_keys(bits=1024):   #Генерирует пару ключей RSA с заданным количеством бит
    phi_n = 0
    e = 65537
    while phi_n <= 65537 or gcd(e, phi_n) != 1:
        p = generate_prime(bits)
        q = generate_prime(bits)
        n = p * q
        phi_n = (p - 1) * (q - 1)
    
    d = mod_inverse(e, phi_n)   #вычисляет мультипликативное обратное числа по модулю
    
    public_key = (e, n)
    private_key = (d, n)
    
    return public_key, private_key

def encrypt_rsa(plaintext, public_key):     #Шифрует сообщение с использованием открытого ключа RSA
    e, n = public_key
    plaintext_int = int.from_bytes(plaintext.encode(), 'big')
    ciphertext_int = pow(plaintext_int, e, n)
    return ciphertext_int

def decrypt_rsa(ciphertext, private_key):   #Расшифровывает сообщение с использованием закрытого ключа RSA
    d, n = private_key
    plaintext_int = pow(ciphertext, d, n)
    plaintext_bytes = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, 'big')
    return plaintext_bytes.decode()

def gcd(a, b):  #Вычисляет наибольший общий делитель
    while b:
        a, b = b, a % b
    return a
