from app.services.auth import (
    hash_password,
    verify_password,
)


def main():

    password = "MyPassword123"

    hashed = hash_password(password)

    print("=" * 60)
    print("HASHED PASSWORD")
    print("=" * 60)
    print(hashed)

    print()

    print("=" * 60)
    print("VERIFY CORRECT PASSWORD")
    print("=" * 60)
    print(verify_password(password, hashed))

    print()

    print("=" * 60)
    print("VERIFY WRONG PASSWORD")
    print("=" * 60)
    print(verify_password("WrongPassword", hashed))


if __name__ == "__main__":
    main()