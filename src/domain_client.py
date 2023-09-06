import base64

import requests


class DomainClient:
    BASE_URL = "https://api.domain.com.au/v1"
    AUTH_URL = "https://auth.domain.com.au/v1/connect/token"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str = "api_listings_read api_salesresults_read",
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._token_info = None

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def scope(self) -> str:
        return self._scope

    @property
    def token_info(self) -> dict:
        return self._token_info

    @property
    def client_credentials(self) -> str:
        client_credentials = f"{self.client_id}:{self.client_secret}"
        self._client_credentials = base64.b64encode(client_credentials.encode())
        return self._client_credentials.decode()

    @property
    def auth_headers(self) -> dict:
        self._auth_headers = {
            "Authorization": f"Basic {self.client_credentials}",
        }
        return self._auth_headers

    @property
    def auth_data(self) -> dict:
        self._auth_data = {
            "grant_type": "client_credentials",
            "scope": self.scope,
        }
        return self._auth_data

    @property
    def headers(self) -> dict:
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        return self._headers

    @property
    def token(self) -> str:
        if not self._token_info:
            raise ValueError("There is no valid token, you need to authorise first!")
        return self._token_info["access_token"]

    def authorise(self) -> None:
        if not self.client_id or not self.client_secret or not self.scope:
            raise ValueError("client_id, client_secret and scope are required")
        r = requests.post(self.AUTH_URL, headers=self.auth_headers, data=self.auth_data)
        if r.status_code not in range(200, 300):
            raise ValueError(f"Authorisation Error: {r.content}")
        self._token_info = r.json()

    def get_city_listings(self, city: str) -> dict:
        url = f"{self.BASE_URL}/salesResults/{city}/listings"
        r = requests.get(url, headers=self.headers)
        if r.status_code not in range(200, 300):
            raise ValueError(f"API Error: {r.content}")
        return r.json()
