from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from planetarium.models import AstronomyShow, ShowTheme
from planetarium.serializers import AstronomyShowRetrieveSerializer

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")

def detail_url(show_id):
    return reverse("planetarium:astronomyshow-detail", args=[show_id])

def sample_astronomy_show(**params) -> AstronomyShow:
    defaults = {
        "title": "Test Astronomy Show",
        "description": "Test Astronomy Show description",
    }
    defaults.update(params)
    return AstronomyShow.objects.create(**defaults)


class UnauthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_astronomy_show_api(self):
        response = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

    def test_astronomy_show_list(self):
        sample_astronomy_show()

        astronomy_show_with_show_themes = sample_astronomy_show(title="Test")
        show_theme_1 = ShowTheme.objects.create(name="First Show Theme")
        show_theme_2 = ShowTheme.objects.create(name="Second Show Theme")
        astronomy_show_with_show_themes.show_theme.add(
            show_theme_1, show_theme_2
        )

        response = self.client.get(ASTRONOMY_SHOW_URL)
        astronomy_shows = AstronomyShow.objects.all()
        serializer = AstronomyShowRetrieveSerializer(astronomy_shows, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_show_list_by_theme(self):
        show_without_theme = sample_astronomy_show(title="Without")
        serializer_without_theme = AstronomyShowRetrieveSerializer(
            show_without_theme
        )

        show_with_theme_1 = sample_astronomy_show(title="With Theme-1")
        show_theme_1 = ShowTheme.objects.create(name="First Show Theme")
        show_with_theme_1.show_theme.add(show_theme_1)
        serializer_with_theme_1 = AstronomyShowRetrieveSerializer(
            show_with_theme_1
        )

        show_with_theme_2 = sample_astronomy_show(title="With Theme-2")
        show_theme_2 = ShowTheme.objects.create(name="Second Show Theme")
        show_with_theme_2.show_theme.add(show_theme_2)
        serializer_with_theme_2 = AstronomyShowRetrieveSerializer(
            show_with_theme_2
        )

        response = self.client.get(
            ASTRONOMY_SHOW_URL,
            {"show_theme": f"{show_theme_1.id},{show_theme_2.id}"}
        )

        self.assertIn(serializer_with_theme_1.data, response.data)
        self.assertIn(serializer_with_theme_2.data, response.data)
        self.assertNotIn(serializer_without_theme.data, response.data)

    def test_filter_show_list_by_its_title(self):
        astronomy_show_1 = sample_astronomy_show(title="First")
        serializer_1 = AstronomyShowRetrieveSerializer(astronomy_show_1)

        astronomy_show_2 = sample_astronomy_show(title="Not First")
        serializer_2 = AstronomyShowRetrieveSerializer(astronomy_show_2)

        astronomy_show_3 = sample_astronomy_show(title="Third")
        serializer_3 = AstronomyShowRetrieveSerializer(astronomy_show_3)

        response = self.client.get(ASTRONOMY_SHOW_URL, {"title": "firs"})

        self.assertIn(serializer_1.data, response.data)
        self.assertIn(serializer_2.data, response.data)
        self.assertNotIn(serializer_3.data, response.data)

    def test_retrieve_astronomy_show_details(self):
        astronomy_show = sample_astronomy_show()
        show_theme = ShowTheme.objects.create(name="Test Theme")
        astronomy_show.show_theme.add(show_theme)
        serializer = AstronomyShowRetrieveSerializer(astronomy_show)

        url = detail_url(astronomy_show.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "AstronomyShow created by user",
            "description": "This AstronomyShow cannot be created",
        }
        response = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.test", password="admin_test_password"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_astronomy_show(self):
        payload = {
            "title": "AstronomyShow created by user",
            "description": "This AstronomyShow cannot be created",
        }
        response = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        astronomy_show = AstronomyShow.objects.get(id=response.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(astronomy_show, key))

    def test_create_astronomy_show_with_show_themes(self):
        show_theme_1 = ShowTheme.objects.create(name="First Show Theme")
        show_theme_2 = ShowTheme.objects.create(name="Second Show Theme")
        show_theme_3 = ShowTheme.objects.create(name="Third Show Theme")

        payload = {
            "title": "AstronomyShow created by user",
            "description": "This AstronomyShow cannot be created",
            "show_theme": [show_theme_1.id, show_theme_2.id]
        }
        response = self.client.post(ASTRONOMY_SHOW_URL, payload)
        astronomy_show = AstronomyShow.objects.get(id=response.data["id"])
        show_themes = astronomy_show.show_theme.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(show_theme_1, show_themes)
        self.assertIn(show_theme_2, show_themes)
        self.assertNotIn(show_theme_3, show_themes)
