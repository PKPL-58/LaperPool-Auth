from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from my_auth.models import Customer
from laperpool_auth import settings
from unittest.mock import patch

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

    @patch('my_auth.views.logger.info')  # Mock logger.info
    @patch('my_auth.views.logger.warning')  # Mock logger.warning
    def test_logging_for_failed_login(self, mock_logger_warning, mock_logger_info):
        """Test untuk memastikan aktivitas login gagal dicatat."""
        # Simulasikan login dengan kredensial yang salah
        response = self.client.post(self.login_url, {'username': 'testuser@example.com', 'password': 'WrongPass123'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username atau password salah.')
        mock_logger_warning.assert_called_with("Login gagal. Username atau password salah.")

    @patch('my_auth.views.logger.info')  # Mock logger.info
    def test_logging_for_successful_login(self, mock_logger_info):
        """Test untuk memastikan aktivitas login berhasil dicatat."""
        # Simulasikan login dengan kredensial yang benar
        response = self.client.post(self.login_url, {'username': 'testuser@example.com', 'password': 'SecurePass123'})

        self.assertEqual(response.status_code, 302)  # Redirect ke HOME_URL

        mock_logger_info.assert_any_call("Login berhasil untuk pengguna: testuser@example.com")

    @patch('requests.get')  # Mock requests.get untuk mencegah request sebenarnya
    def test_ssrf_protection(self, mock_requests_get):
        """Test untuk memastikan aplikasi tidak rentan terhadap SSRF."""
        # Mock respons dari requests.get
        mock_requests_get.return_value.status_code = 400

        malicious_url = "http://127.0.0.1:8000/internal-api"
        response = self.client.post(self.login_url, {'username': malicious_url, 'password': 'SecurePass123'}, follow=True)

        # Pastikan aplikasi tidak memproses URL berbahaya
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username hanya boleh mengandung huruf, angka, underscore, @, dan titik.')
        mock_requests_get.assert_not_called()

class RegisterTestCase(TestCase):
    def setUp(self):
        """Setup for registration tests."""
        self.register_url = reverse('auth:register')
        self.valid_data = {
            'username': 'newuser@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123',
            'phone_number': '08123456789',
            'pin': '123456',
            'alamat': 'Jl. Test No. 123'
        }

    def test_valid_registration(self):
        """Test registrasi dengan data yang valid."""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 302)  # Redirect setelah sukses
        user = Customer.objects.get(username=self.valid_data['username'])
        self.assertTrue(user.check_password(self.valid_data['password1']))
        self.assertEqual(user.phone_number, self.valid_data['phone_number'])
        self.assertEqual(user.alamat, self.valid_data['alamat'])

    def test_invalid_email(self):
        """Test registrasi dengan email tidak valid."""
        data = self.valid_data.copy()
        data['username'] = 'invalid-email'
        response = self.client.post(self.register_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Masukkan email yang valid.')

    def test_invalid_pin(self):
        """Test registrasi dengan PIN tidak valid."""
        test_cases = [
            ('12345', 'PIN harus berupa 6 digit angka.'),  # Terlalu pendek
            ('1234567', 'PIN harus berupa 6 digit angka.'),  # Terlalu panjang
            ('abcdef', 'PIN harus berupa 6 digit angka.'),  # Bukan angka
        ]
        
        for pin, error_message in test_cases:
            data = self.valid_data.copy()
            data['pin'] = pin
            response = self.client.post(self.register_url, data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, error_message)

    def test_invalid_phone(self):
        """Test registrasi dengan nomor telepon tidak valid."""
        data = self.valid_data.copy()
        data['phone_number'] = 'abc12345'
        response = self.client.post(self.register_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nomor telepon hanya boleh mengandung angka.')

    def test_xss_in_alamat(self):
        """Test pencegahan XSS dalam alamat."""
        data = self.valid_data.copy()
        data['alamat'] = '<script>alert("XSS")</script>'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect setelah sukses
        user = Customer.objects.get(username=self.valid_data['username'])
        self.assertNotIn('<script>', user.alamat)  # Memastikan script tag di-escape

    def test_missing_required_fields(self):
        """Test registrasi dengan field yang required kosong."""
        required_fields = ['username', 'password1', 'password2', 'phone_number', 'pin']
        
        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            response = self.client.post(self.register_url, data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'This field is required.')

    def test_password_validation(self):
        """Test validasi password."""
        test_cases = [
            {'password1': 'short', 'password2': 'short', 'error': 'This password is too short.'},
            {'password1': 'admin', 'password2': 'admin', 'error': 'This password is too common.'},
            {'password1': 'SecurePass123', 'password2': 'DifferentPass123', 'error': 'The two password fields didn’t match'},
        ]
        
        for test_case in test_cases:
            data = self.valid_data.copy()
            data['password1'] = test_case['password1']
            data['password2'] = test_case['password2']
            response = self.client.post(self.register_url, data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, test_case['error'])

    @patch('my_auth.views.logger.info')
    def test_successful_registration_logging(self, mock_logger_info):
        """Test logging untuk registrasi berhasil."""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        mock_logger_info.assert_called_with(
            f"Registrasi berhasil untuk pengguna: {self.valid_data['username']}"
        )
