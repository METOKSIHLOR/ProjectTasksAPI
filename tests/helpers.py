import httpx


async def register_user(client: httpx.AsyncClient, name: str, email: str, password: str = "secret123"):
    return await client.post(
        "/users/registration",
        json={"name": name, "email": email, "password": password},
    )


async def login_user(client: httpx.AsyncClient, email: str, password: str = "secret123"):
    return await client.post(
        "/users/auth/login",
        json={"email": email, "password": password},
    )
