import secrets


def generate_secret_key(length: int = 32) -> str:
    return secrets.token_hex(length)


# Генерация секретного ключа
secret_key = generate_secret_key()
print("Generated SECRET_KEY:", secret_key)
