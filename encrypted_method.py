import secrets
import hashlib


def generate_token(length=32):
    # Генерируем случайную строку указанной длины из символов A-Z, a-z, 0-9
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token
# Функция использует алфавит, состоящий из символов A-Z, a-z и 0-9.
# Генерирует случайную строку заданной длины (по умолчанию 32 символа) с использованием библиотеки secrets,
# Которая предназначена для генерации криптографически стойких случайных чисел.

def hash_token(token):
    # Хэшируем токен с использованием SHA-3 512
    sha3_512 = hashlib.sha3_512()
    sha3_512.update(token.encode('utf-8'))
    hashed_token = sha3_512.hexdigest()
    return hashed_token
# Создает объект хэширования SHA-3 512 из библиотеки hashlib.
# Обновляет хэш-объект с байтовым представлением токена.
# Возвращает хэшированную строку в шестнадцатеричном формате.


# Пример использования
if __name__ == "__main__":
    token = generate_token()
    hashed_token = hash_token(token)

    print("Generated Token:", token)
    print("Hashed Token (SHA-3 512):", hashed_token)
