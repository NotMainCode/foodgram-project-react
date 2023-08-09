"""Testing the user page and user list page."""

from http import HTTPStatus

from rest_framework.test import APITestCase

from users.models import User


class UsersTest(APITestCase):
    """Testing the user page and user list page."""

    url_users = "/api/users/"

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username="user_one", email="user_one@email.fake"
        )
        User.objects.create_user(
            username="user_two", email="user_two@email.fake"
        )
        User.objects.create_user(
            username="user_three", email="user_three@email.fake"
        )

    def test_user_list(self):
        """Get the correct paginated response to user list request."""
        response = self.client.get(self.url_users)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            msg=(
                f"Page '{self.url_users}' is unavailable to anonymous user."
            ),
        )
        pagination_parameters = ("count", "next", "previous", "results")
        for pagination_parameter in pagination_parameters:
            self.subTest(
                self.assertIn(
                    pagination_parameter,
                    response.data,
                    msg=(
                        f"Check that a GET request to `{self.url_users}` "
                        f"returns data with pagination. "
                        f"`{pagination_parameter}` parameter not found."
                    ),
                )
            )
        self.assertEqual(
            response.data["count"],
            User.objects.count(),
            msg=(
                f"Check that a GET request to `{self.url_users}` "
                f"returns data with pagination. "
                f"The value of the 'count` parameter is incorrect."
            ),
        )
        self.assertEqual(
            type(response.json()["results"]),
            list,
            msg=(
                f"Check that a GET request to `{self.url_users}` "
                f"returns data with pagination. "
                f"The type of the `results` parameter should be a list."
            ),
        )
        expected_count_page_items = {
            1: User.objects.count() - 1,
            2: 1,
        }
        for page_number, expected_count in expected_count_page_items.items():
            with self.subTest():
                response = self.client.get(
                    self.url_users,
                    data={
                        "limit": expected_count_page_items[1],
                        "page": page_number,
                    },
                )
                self.assertEqual(
                    expected_count,
                    len(response.data["results"]),
                    msg=(
                        f"Check that the GET request to `{self.url_users}` "
                        f"with the 'page' and 'limit' parameters "
                        f"returns paginated data. Objects count "
                        f"in the 'results' parameter is incorrect."
                    ),
                )
        print(response.data["results"])
