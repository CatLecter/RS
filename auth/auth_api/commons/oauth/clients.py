from typing import Any, Dict, Optional

from auth_api.extensions import settings
from flask import request
from rauth import OAuth2Service


class OAuthClient:
    providers = None

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.service = None
        credentials = getattr(settings.oauth, provider_name)
        self.consumer_id = credentials.id
        self.consumer_secret = credentials.secret
        self.consumer_scope = credentials.scope
        self.consumer_redirect_uri = credentials.redirect_uri
        self.authorize_url = credentials.authorize_url
        self.base_url = credentials.base_url

    def get_data_for_authorize(self) -> Dict:
        data_for_authorize = {
            "compiled_url": self.service.get_authorize_url(
                response_type="token",
                redirect_uri=self.consumer_redirect_uri,
                scope=self.consumer_scope,
            ),
            "authorize_params": {
                "authorize_url": self.service.authorize_url,
                "response_type": "token",
                "redirect_uri": self.consumer_redirect_uri,
                "client_id": self.service.client_id,
                "scope": self.consumer_scope,
            },
        }
        return data_for_authorize

    @classmethod
    def get_provider(cls, provider_name: str) -> Any:
        if cls.providers is None:
            cls.load_providers()
        return cls.providers.get(provider_name)

    @classmethod
    def load_providers(cls):
        cls.providers = {}
        for provider_class in cls.__subclasses__():
            provider = provider_class(None)
            cls.providers[provider.provider_name] = provider


class YandexOAuthClient(OAuthClient):
    def __init__(self, provider_name: str):
        super(YandexOAuthClient, self).__init__("yandex")
        self.service = OAuth2Service(
            name="yandex",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            base_url=self.base_url,
        )

    def get_user_info(self) -> Optional[Dict]:
        access_token = request.json.get("access_token")
        if not access_token:
            return None
        oauth_session = self.service.get_session(token=access_token)
        user_data = oauth_session.get("info?format=json").json()
        print(user_data)
        return {
            "social_id": f'yandex::{user_data["client_id"]}',
            "email": user_data["default_email"],
        }


class GoogleOAuthClient(OAuthClient):
    def __init__(self, provider_name: str):
        super(GoogleOAuthClient, self).__init__("google")
        self.service = OAuth2Service(
            name="google",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            base_url=self.base_url,
        )

    def get_user_info(self) -> Optional[Dict]:
        access_token = request.json.get("access_token")
        if not access_token:
            return None
        oauth_session = self.service.get_session(token=access_token)
        user_data = oauth_session.get("userinfo").json()
        return {
            "social_id": f'google::{user_data["id"]}',
            "email": user_data["email"],
        }


class VkOAuthClient(OAuthClient):
    def __init__(self, provider_name: str):
        super(VkOAuthClient, self).__init__("vk")
        self.service = OAuth2Service(
            name="vk",
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.authorize_url,
            base_url=self.base_url,
        )

    def get_user_info(self) -> Optional[Dict]:
        access_token = request.json.get("access_token")
        if not access_token:
            return None
        oauth_session = self.service.get_session(token=access_token)
        response = oauth_session.get("method/users.get?v=5.131").json()
        user_data = response.get("response")
        user_data = user_data[0]
        return {
            "social_id": f'vk::{user_data["id"]}',
            "email": None,
        }
