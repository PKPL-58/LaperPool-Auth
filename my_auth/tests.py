from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from my_auth.models import Customer
from laperpool_auth import settings

User = get_user_model()

class LoginTestCase(TestCase):
    def setUp(self):
        # Buat user untuk pengujian
        self.user = Customer.objects.create_user(username='testuser@example.com', password='SecurePass123', phone_number='08123456789')
        self.login_url = reverse('auth:login')

    def test_valid_login(self):
        """Test login dengan kredensial yang valid."""
        response = self.client.post(self.login_url, {'username': 'testuser@example.com', 'password': 'SecurePass123'})
        self.assertEqual(response.status_code, 302)  # Redirect ke HOME_URL
        self.assertIn(settings.SIMPLE_JWT['AUTH_COOKIE'], response.cookies)  # Pastikan session cookie disetel

    def test_invalid_username(self):
        """Test login dengan username yang tidak valid."""
        response = self.client.post(self.login_url, {'username': 'invalid@example.com', 'password': 'SecurePass123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username atau password salah.')

    def test_invalid_password(self):
        """Test login dengan password yang salah."""
        response = self.client.post(self.login_url, {'username': 'testuser@example.com', 'password': 'WrongPass123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username atau password salah.')

    def test_sql_injection(self):
        """Test login dengan payload SQL Injection."""
        response = self.client.post(self.login_url, {'username': "' OR 1=1; --", 'password': 'SecurePass123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username hanya boleh mengandung huruf, angka, underscore, @, dan titik.')

    def test_xss_attack(self):
        """Test login dengan payload XSS."""
        response = self.client.post(self.login_url, {'username': '<script>alert(1)</script>', 'password': 'SecurePass123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username hanya boleh mengandung huruf, angka, underscore, @, dan titik.')

    def test_brute_force_protection(self):
        """Test rate limiting untuk mencegah brute force."""
        for _ in range(6):  # Melebihi batas rate limit (5/m)
            response = self.client.post(self.login_url, {'username': 'testuser@example.com', 'password': 'WrongPass123'}, follow=True)
        self.assertEqual(response.status_code, 200)  # Too Many Requests
        self.assertContains(response, 'Anda telah melampaui batas percobaan login.')

    def test_empty_username_password(self):
        """Test login dengan username dan password kosong."""
        response = self.client.post(self.login_url, {'username': '', 'password': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username dan password tidak boleh kosong.')

    def test_jwt_cookie_set(self):
        """Test apakah JWT disetel di cookie setelah login berhasil."""
        response = self.client.post(self.login_url, {'username': 'testuser@example.com', 'password': 'SecurePass123'})
        self.assertEqual(response.status_code, 302)  # Redirect ke HOME_URL
        self.assertIn(settings.SIMPLE_JWT['AUTH_COOKIE'], response.cookies)  # Pastikan JWT disetel di cookie

    def test_access_control(self):
        """Test apakah hanya pengguna yang valid dapat login."""
        "Pengecekan akses kontrol terletak di service laperpool_app dengan decorator @allowed_groups"
        pass
