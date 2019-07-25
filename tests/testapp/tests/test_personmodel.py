from django.test import TestCase

from tests.testapp.models import ModelWhenAnyPerson


class ModelCustomPKTestCase(TestCase):
	def setUp(self):
		person = ModelWhenAnyPerson.objects.create(first_name="Max", middle_name="Joe", last_name="Blocks")
		self.person = person

	def test_when_any(self):
		person = self.person
		person.middle_name = "Marie"
		person.save()
		person.refresh_from_db()

		self.assertEqual("Max Marie Blocks", person.full_name)

		person.first_name = "Anton"
		person.save()
		person.refresh_from_db()
		self.assertEqual("Anton Marie Blocks", person.full_name)

		person.last_name = "Korver"
		person.save()
		person.refresh_from_db()
		self.assertEqual("Anton Marie Korver", person.full_name)
