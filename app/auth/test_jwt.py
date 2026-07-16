from app.auth.jwt_handler import (
    create_access_token,
    verify_access_token,
)


def main():

    token = create_access_token(
        {
            "sub": "anuj",
        }
    )

    print("=" * 60)
    print("TOKEN")
    print("=" * 60)
    print(token)

    print()

    print("=" * 60)
    print("DECODED")
    print("=" * 60)
    print(
        verify_access_token(token)
    )


if __name__ == "__main__":
    main()