from django.core.urlresolvers import reverse
from django.test import TestCase

from meetup_integration.models import Season


class WebViewsTestCase(TestCase):
    def setUp(self):
        Season.objects.create(
            name="2014/2015",
            slug=""
        )

        Season.objects.create(
            name="2015/2016",
            slug="15/16"
        )

        Season.objects.create(
            name="All",
            slug="all",
        )

    def test_meetups_view(self):
        """
        Test meetups view.
        """
        response = self.client.get(reverse("meetups")).status_code
        self.assertEqual(response, 200)

    def test_members_view(self):
        """
        Test members view.
        """
        response = self.client.get(reverse("members")).status_code
        self.assertEqual(response, 200)

    def test_team_generator_view(self):
        """
        Test team generator view.
        """
        response = self.client.get(reverse("team_generator")).status_code
        self.assertEqual(response, 200)

    def test_payments_view(self):
        """
        Test payments view.
        """
        response = self.client.get(reverse("payments")).status_code
        self.assertEqual(response, 200)
