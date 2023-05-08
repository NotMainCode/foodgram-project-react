"""Testing user registration and login."""

import unittest
from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from users.models import User


@unittest.skipIf(
    APIClient().options(reverse("api:users-list")).status_code
    == HTTPStatus.NOT_FOUND,
    "Endpoint {0} not available)".format(reverse("api:users-list")),
)
class UserSignUpTest(APITestCase):
    """Testing user registration."""

    url_signup = reverse("api:users-list")

    def test_signup_without_required_field(self):
        """User is not created if the required data is not set."""
        response = self.client.post(self.url_signup)
        self.assertEqual(
            response.status_code,
            HTTPStatus.BAD_REQUEST,
            msg=(
                f"Check that the POST request to `{self.url_signup}` "
                f"with no parameters returns status {HTTPStatus.BAD_REQUEST}"
            ),
        )
        required_fields = [
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
        ]
        for field in required_fields:
            with self.subTest():
                self.assertIn(
                    field,
                    response.data.keys(),
                    msg=(
                        f"Check that a POST request to '{self.url_signup}' "
                        f"with no parameters returns a message "
                        f"about the required {field} field."
                    ),
                )

    def test_signup_invalid_data(self):
        """User is not created if incorrect data is specified."""
        invalid_data = {
            "email": "invalid_email",
            "username": "*",
            "first_name": "first_name",
            "last_name": "last_name",
            "password": "password",
        }
        response = self.client.post(self.url_signup, data=invalid_data)
        self.assertEqual(
            response.status_code,
            HTTPStatus.BAD_REQUEST,
            msg=(
                f"Check that a POST request to `{self.url_signup}` with "
                f"invalid parameters returns status {HTTPStatus.BAD_REQUEST}"
            ),
        )
        invalid_fields = ["email", "username"]
        for field in invalid_fields:
            with self.subTest():
                self.assertIn(
                    field,
                    response.data.keys(),
                    msg=(
                        f"Check that a POST request to '{self.url_signup}' "
                        f"with invalid parameters returns a "
                        f"message about the invalid {field} field."
                    ),
                )

    def test_signup_valid_data(self):
        """User is created if the correct data is specified."""
        valid_data = {
            "email": "signup@valid.email",
            "username": "username",
            "first_name": "first_name",
            "last_name": "last_name",
            "password": "correct_password",
        }
        response = self.client.post(self.url_signup, data=valid_data)
        self.assertEqual(
            response.status_code,
            HTTPStatus.CREATED,
            msg=(
                f"Check that a POST request to `{self.url_signup}` with "
                f"valid parameters returns status {HTTPStatus.CREATED}"
            ),
        )
        self.assertTrue(
            User.objects.filter(email=valid_data["email"]).exists(),
            msg=(
                f"Check that a POST request to `{self.url_signup}` "
                f"with valid parameters creates new user."
            ),
        )
        expected_response_data = valid_data.copy()
        expected_response_data.pop("password")
        expected_response_data.update(
            {"id": User.objects.get(email=valid_data["email"]).id}
        )
        self.assertDictEqual(
            expected_response_data,
            response.data,
            msg=(
                f"Check that a POST request to `{self.url_signup}` with "
                f"valid parameters returns response with the correct data."
            ),
        )

    def test_signup_same_email_username_restricted(self):
        """User is not created with the same data as it already exist."""
        valid_data = {
            "email": "signup@valid.email",
            "username": "username",
            "first_name": "first_name",
            "last_name": "last_name",
            "password": "correct_password",
        }
        User.objects.create_user(**valid_data)
        response = self.client.post(self.url_signup, data=valid_data)
        repeating_fields = ["email", "username"]
        for field in repeating_fields:
            with self.subTest():
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.BAD_REQUEST,
                    msg=(
                        f"Check that a POST request to `{self.url_signup}` "
                        f"cannot create a user "
                        f"whose {field} is already registered "
                        f"and returns status {HTTPStatus.BAD_REQUEST}."
                    ),
                )
                self.assertIn(
                    field,
                    response.data.keys(),
                    msg=(
                        f"Check that a POST request to `{self.url_signup}` "
                        f"cannot create a user "
                        f"whose name is already registered and returns a "
                        f"message about a duplicate {field} field."
                    ),
                )


@unittest.skipIf(
    APIClient().options(reverse("api:login")).status_code
    == HTTPStatus.NOT_FOUND,
    "Endpoint {0} not available)".format(reverse("api:login")),
)
class UserLoginTest(APITestCase):
    """Testing user login."""

    def test_login_email_password(self):
        """User receives a token after providing email and password."""
        user_email = "user@email.fake"
        user_password = "user_password"
        User.objects.create_user(
            username="User",
            email=user_email,
            password=user_password,
        )
        url_login = reverse("api:login")
        response = self.client.post(
            url_login, data={"email": user_email, "password": user_password}
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            msg=(
                f"Check that a POST request to `{url_login}` with "
                f"email and password fields returns status {HTTPStatus.OK}"
            ),
        )
        self.assertIn(
            "auth_token",
            response.data,
            msg=(
                f"Check that a POST request to `{url_login}` "
                f"with email and password fields returns a response "
                f"with the 'auth_token' field"
            ),
        )
