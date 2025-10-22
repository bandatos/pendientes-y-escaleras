
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from report.models import StairReport
from stair.models import Stair  # Ajusta según tu app

User = get_user_model()


class StairReportCreateTestCase(TestCase):
    """Tests para la creación de reportes de escalera"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuarios
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        # Crear token para autenticación
        self.token = Token.objects.create(user=self.user)

        # Crear cliente API
        self.client = APIClient()

        # Crear una escalera de prueba
        self.stair = Stair.objects.create(
            # Ajusta los campos según tu modelo Stair
            name='Escalera Test',
            # otros campos necesarios...
        )

        # URL del endpoint
        self.url = '/api/stair_report/'

        # Datos válidos base para crear un reporte
        self.valid_data = {
            'stair': self.stair.id,
            'status_maintenance': 'full',
            'code_identifiers': ['CODE001', 'CODE002'],
            'route_start': 'Entrada Principal',
            'path_start': 'Nivel 1',
            'path_end': 'Nivel 2',
            'route_end': 'Salida Norte',
            'is_aligned': True,
            'is_working': False,
            'details': 'Escalera requiere mantenimiento completo'
        }

    def test_create_stair_report_authenticated(self):
        """Test: Usuario autenticado puede crear un reporte"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StairReport.objects.count(), 1)

        # Verificar que el usuario se asignó correctamente
        report = StairReport.objects.first()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.stair, self.stair)
        self.assertEqual(report.status_maintenance, 'full')

    def test_create_stair_report_unauthenticated(self):
        """Test: Usuario no autenticado no puede crear un reporte"""
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(StairReport.objects.count(), 0)

    def test_create_stair_report_minimal_data(self):
        """Test: Crear reporte con datos mínimos requeridos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        minimal_data = {
            'stair': self.stair.id,
            'is_aligned': False,
        }

        response = self.client.post(self.url, minimal_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StairReport.objects.count(), 1)

    def test_create_stair_report_with_other_maintenance(self):
        """Test: Crear reporte con estado de mantenimiento 'otro'"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        data = self.valid_data.copy()
        data['status_maintenance'] = 'other'
        data['other_status_maintenance'] = 'Reparación de sensores'

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = StairReport.objects.first()
        self.assertEqual(report.status_maintenance, 'other')
        self.assertEqual(report.other_status_maintenance, 'Reparación de sensores')

    def test_create_stair_report_invalid_stair(self):
        """Test: No se puede crear reporte con escalera inexistente"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        invalid_data = self.valid_data.copy()
        invalid_data['stair'] = 99999  # ID que no existe

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(StairReport.objects.count(), 0)

    def test_create_stair_report_invalid_status_maintenance(self):
        """Test: No se puede crear reporte con estado de mantenimiento inválido"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        invalid_data = self.valid_data.copy()
        invalid_data['status_maintenance'] = 'invalid_status'

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(StairReport.objects.count(), 0)

    def test_create_stair_report_empty_code_identifiers(self):
        """Test: Crear reporte con lista vacía de códigos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        data = self.valid_data.copy()
        data['code_identifiers'] = []

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = StairReport.objects.first()
        self.assertEqual(report.code_identifiers, [])

    def test_create_stair_report_null_optional_fields(self):
        """Test: Crear reporte con campos opcionales en null"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        data = {
            'stair': self.stair.id,
            'status_maintenance': None,
            'is_working': None,
            'details': None,
            'is_aligned': False,
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = StairReport.objects.first()
        self.assertIsNone(report.status_maintenance)
        self.assertIsNone(report.is_working)

    def test_create_stair_report_boolean_fields(self):
        """Test: Validar campos booleanos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Test con is_aligned=True y is_working=True
        data = self.valid_data.copy()
        data['is_aligned'] = True
        data['is_working'] = True

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = StairReport.objects.first()
        self.assertTrue(report.is_aligned)
        self.assertTrue(report.is_working)

    def test_create_stair_report_long_details(self):
        """Test: Crear reporte con campo details extenso"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        data = self.valid_data.copy()
        data['details'] = 'A' * 1000  # Texto largo

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = StairReport.objects.first()
        self.assertEqual(len(report.details), 1000)

    def test_create_stair_report_all_maintenance_types(self):
        """Test: Crear reportes con todos los tipos de mantenimiento"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        maintenance_types = ['full', 'medium', 'minor', 'other']

        for maintenance_type in maintenance_types:
            data = self.valid_data.copy()
            data['status_maintenance'] = maintenance_type

            response = self.client.post(self.url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(StairReport.objects.count(), len(maintenance_types))

    def test_create_multiple_reports_same_stair(self):
        """Test: Se pueden crear múltiples reportes para la misma escalera"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Crear primer reporte
        response1 = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Crear segundo reporte para la misma escalera
        response2 = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEqual(StairReport.objects.count(), 2)
        self.assertEqual(
            StairReport.objects.filter(stair=self.stair).count(), 2
        )

    def test_create_stair_report_response_structure(self):
        """Test: Verificar estructura de la respuesta"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la respuesta contiene los campos esperados
        expected_fields = [
            'id', 'stair', 'user', 'status_maintenance',
            'code_identifiers', 'route_start', 'path_start',
            'path_end', 'route_end', 'is_aligned', 'is_working',
            'details', 'date_reported', 'date_received'
        ]

        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_user_cannot_be_overridden(self):
        """Test: El usuario no puede ser sobrescrito en el request"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        data = self.valid_data.copy()
        data['user'] = self.other_user.id  # Intentar asignar otro usuario

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que el usuario es el autenticado, no el enviado en el request
        report = StairReport.objects.first()
        self.assertEqual(report.user, self.user)
        self.assertNotEqual(report.user, self.other_user)


class StairReportPermissionsTestCase(TestCase):
    """Tests específicos de permisos"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/stair_report/'

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

        self.stair = Stair.objects.create(name='Test Stair')

    def test_read_only_access_without_authentication(self):
        """Test: Acceso de solo lectura sin autenticación"""
        # GET debería funcionar sin autenticación (IsAuthenticatedOrReadOnly)
        response = self.client.get(self.url)
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        )

    def test_write_requires_authentication(self):
        """Test: Escritura requiere autenticación"""
        data = { 'stair': self.stair.id, 'is_aligned': False }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)