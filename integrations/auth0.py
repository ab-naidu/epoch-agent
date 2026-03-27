import os, requests

class Auth0Client:
    def __init__(self):
        self.domain = os.getenv("AUTH0_DOMAIN")
        self.client_id = os.getenv("AUTH0_CLIENT_ID")
        self.client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        self.audience = os.getenv("AUTH0_AUDIENCE")
        self._token = None

    def get_token(self) -> str:
        if self._token:
            return self._token
        resp = requests.post(f"https://{self.domain}/oauth/token", json={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.audience,
            "grant_type": "client_credentials"
        })
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def verify_token(self, token: str) -> dict:
        """Verify a user JWT and return claims."""
        resp = requests.get(
            f"https://{self.domain}/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        resp.raise_for_status()
        return resp.json()

    def get_auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}
