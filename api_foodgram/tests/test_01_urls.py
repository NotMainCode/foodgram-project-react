"""URL accessibility testing."""

from http import HTTPStatus

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from users.models import User


class URLTest(APITestCase):
    """URL accessibility testing."""

    url_arg_id = 1

    def test_public_urls_available_anonymous(self):
        """Public URLs are available to anonymous user."""
        public_urls = (
            "/api/users/",
            f"/api/users/{self.url_arg_id}/",
            "/api/auth/token/login/",
            "/api/ingredients/",
            f"/api/ingredients/{self.url_arg_id}/",
            "/api/tags/",
            f"/api/tags/{self.url_arg_id}/",
            "/api/recipes/",
            f"/api/recipes/{self.url_arg_id}/",
        )

        for public_url in public_urls:
            with self.subTest():
                response = self.client.options(public_url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    msg=(
                        f"Page '{public_url}' "
                        f"is unavailable to anonymous user."
                    ),
                )

    def test_private_urls_available_auth_user(self):
        """Private URLs are available to authenticated user."""
        user = User.objects.create_user(
            username="User", email="user@email.fake"
        )
        Token(user=user).save()
        token = Token.objects.get(user=user)
        authenticated_client = APIClient()
        authenticated_client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )
        private_urls = (
            "/api/users/me/",
            "/api/users/set_password/",
            "/api/users/subscriptions/",
            "/api/recipes/download_shopping_cart/",
            f"/api/users/{self.url_arg_id}/subscribe/",
            f"/api/recipes/{self.url_arg_id}/favorite/",
            f"/api/recipes/{self.url_arg_id}/shopping_cart/",
            "/api/auth/token/logout/",
        )
        for private_url in private_urls:
            with self.subTest():
                response = authenticated_client.options(private_url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    msg=(
                        f"Page '{private_url}' "
                        f"is unavailable to authenticated user."
                    ),
                )

    def test_private_urls_not_available_anonymous(self):
        """Private URLs are not available to the anonymous user."""
        private_urls = (
            "/api/users/me/",
            "/api/users/set_password/",
            "/api/users/subscriptions/",
            "/api/recipes/download_shopping_cart/",
            f"/api/users/{self.url_arg_id}/subscribe/",
            f"/api/recipes/{self.url_arg_id}/favorite/",
            f"/api/recipes/{self.url_arg_id}/shopping_cart/",
            "/api/auth/token/logout/",
        )
        for private_url in private_urls:
            with self.subTest():
                response = self.client.options(private_url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.UNAUTHORIZED,
                    msg=(
                        f"Page '{private_url}' "
                        f"must be inaccessible to anonymous user."
                    ),
                )
