from django.test import TestCase


class WebViewsTestCase(TestCase):

    def test_meetups_view(self):
        """
        Test meetups view.
        """
        response = self.client.get("/meetups/").status_code
        self.assertEqual(response, 200)

    def test_members_view(self):
        """
        Test members view.
        """
        response = self.client.get("/members/").status_code
        self.assertEqual(response, 200)

    def test_team_generator_view(self):
        """
        Test team generator view.
        """
        response = self.client.get("/team-generator/").status_code
        self.assertEqual(response, 200)

    def test_payments_view(self):
        """
        Test payments view.
        """
        response = self.client.get("/payments/").status_code
        self.assertEqual(response, 200)
