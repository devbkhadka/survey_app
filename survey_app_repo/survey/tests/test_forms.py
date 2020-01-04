from django.test import TestCase
from ..forms import FormRegistar

class TestFormRegistar(TestCase):

    def test_get_instance(self):
        registar = FormRegistar.get_instance()
        self.assertIsInstance(registar, FormRegistar)
        registar2 = FormRegistar.get_instance()
        self.assertTrue(registar is registar2)
        
    def test_constructor_raises_error_when_called_directly(self):
        FormRegistar.get_instance()
        with self.assertRaises(Exception):
            FormRegistar()
    
    def test_register_and_get_form(self):
        registar = FormRegistar.get_instance()

        registar.register_form('key1', TestCase)
        registar.register_form('key2', Exception)
        
        registar = FormRegistar.get_instance()
        self.assertIsInstance(registar.get_form_for('key2'), Exception)
        self.assertIsInstance(registar.get_form_for('key1'), TestCase)
