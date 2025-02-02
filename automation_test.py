import requests
import unittest

API_URL = "http://localhost:5000"  # Cambia si tu API corre en otro puerto o dominio
TEST_USER = {"username": "testuser", "password": "password123"}

class TestAPIFunctionality(unittest.TestCase):
    token = None

    @classmethod
    def setUpClass(cls):
        """Obtiene el token de autenticación antes de ejecutar las pruebas"""
        response = requests.post(f"{API_URL}/login", json=TEST_USER)
        assert response.status_code == 200, "No se pudo obtener el token"
        json_response = response.json()
        cls.token = json_response.get("access_token")
        assert cls.token, "No se recibió un token válido"

    def get_headers(self, token=None):
        """Devuelve los headers con el token JWT si es proporcionado, de lo contrario usa el válido"""
        return {"Authorization": f"Bearer {token or self.token}"}

    def test_api_running(self):
        """Verifica que la API esté corriendo y responda correctamente"""
        response = requests.get(f"{API_URL}/items", headers=self.get_headers())
        self.assertEqual(response.status_code, 200, "La API no responde correctamente")

    def test_get_user_info(self):
        """Verifica que se pueda obtener la info del usuario autenticado"""
        response = requests.get(f"{API_URL}/user", headers=self.get_headers())
        self.assertEqual(response.status_code, 200, "No se pudo obtener información del usuario")
        self.assertIn("user", response.json(), "La respuesta no contiene la clave 'user'")

    def test_invalid_token(self):
        """Verifica que la API rechace un token malformado o inválido"""
        # Caso 1: Token malformado
        malformed_token = "INVALID_TOKEN"
        headers = self.get_headers(malformed_token)
        response = requests.get(f"{API_URL}/user", headers=headers)
        self.assertIn(response.status_code, [401, 422], "La API no rechazó un token malformado como se esperaba")
        self.assertIn("msg", response.json(), "La respuesta no contiene un mensaje de error esperado")

        # Caso 2: Token bien formado pero inválido
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.error"
        headers = self.get_headers(invalid_token)
        response = requests.get(f"{API_URL}/user", headers=headers)
        self.assertEqual(response.status_code, 422, "La API no devolvió 422 para un token bien formado pero inválido")
        self.assertIn("msg", response.json(), "La respuesta no contiene un mensaje de error esperado")


    def test_create_item(self):
        """Verifica que se pueda crear un nuevo ítem correctamente"""
        new_item = {"name": "Test Item", "description": "Created by test script"}
        response = requests.post(f"{API_URL}/items", json=new_item, headers=self.get_headers())
        self.assertEqual(response.status_code, 201, "No se pudo crear el ítem")
        json_response = response.json()
        self.assertIn("item", json_response, "La respuesta no contiene el ítem creado")
        self.item_id = json_response["item"].get("id")
        self.assertIsNotNone(self.item_id, "No se obtuvo el ID del ítem creado")

    def test_update_item(self):
        """Verifica que se pueda actualizar un ítem existente"""
        # Crear un ítem para garantizar su existencia
        new_item = {"name": "Item to Update", "description": "Created for update test"}
        create_response = requests.post(f"{API_URL}/items", json=new_item, headers=self.get_headers())
        self.assertEqual(create_response.status_code, 201, "No se pudo crear el ítem para la prueba de actualización")
        item_id = create_response.json()["item"]["id"]

        # Intentar actualizar el ítem creado
        update_data = {"name": "Updated Item", "description": "Updated by test script"}
        response = requests.put(f"{API_URL}/items/{item_id}", json=update_data, headers=self.get_headers())
        self.assertEqual(response.status_code, 200, "No se pudo actualizar el ítem")
        self.assertIn("item", response.json(), "La respuesta no contiene la clave 'item'")


    def test_delete_item(self):
        """Verifica que se pueda eliminar un ítem correctamente"""
        response = requests.delete(f"{API_URL}/items/1", headers=self.get_headers())
        self.assertEqual(response.status_code, 200, "No se pudo eliminar el ítem")
        self.assertIn("msg", response.json(), "La respuesta no contiene la clave 'msg'")

    def test_access_protected_route_without_token(self):
        """Verifica que el acceso a una ruta protegida sin token devuelva 401"""
        response = requests.get(f"{API_URL}/user")
        self.assertEqual(response.status_code, 401, "La API permitió acceso sin token")

if __name__ == "__main__":
    unittest.main()
