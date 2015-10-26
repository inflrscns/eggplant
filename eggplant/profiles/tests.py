import datetime

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

# Create your tests here.
from eggplant.factories import UserFactory, DepartmentFactory, \
    AccountFactory


class TestProfile(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('pass')
        self.user.save()
        email_address = EmailAddress.objects\
            .add_email(None, self.user, 'test@food.net', confirm=False,
                       signup=False)
        email_address.verified = True
        email_address.primary = True
        email_address.save()

    def test_profile(self):
        response = self.client.get(reverse('eggplant:membership:profile'))
        url = reverse('account_login') + '?next=' + \
            reverse('eggplant:membership:profile')
        self.assertRedirects(response, url, status_code=302,
                             target_status_code=200, msg_prefix='')

        self.client.login(username='test@food.net', password='pass')
        response = self.client.get(reverse('eggplant:membership:profile'))
        expected = '<form action="%s"' % reverse('eggplant:membership:profile')
        self.assertContains(response, expected, 1, 200)

        data = {
            'first_name': 'Joe',
            'middle_name': 'Frank',
            'last_name': 'Doe',
            'address': '123 Sunset av. NY, USA',
            'postcode': '123321ABCD',
            'city': 'New York',
            'tel': '79231232',
            'sex': 'f',
            'date_of_birth': '11/12/13',
            'privacy': 'checked',
        }
        response = self.client.post(reverse('eggplant:membership:profile'),
                                    data=data)
        self.assertRedirects(response, reverse('eggplant:dashboard:home'),
                             status_code=302,
                             target_status_code=200, msg_prefix='')

        expected = {
            'middle_name': 'Frank',
            'address': '123 Sunset av. NY, USA',
            'postcode': '123321ABCD',
            'sex': 'f',
            'city': 'New York',
            'tel': '79231232',
            'date_of_birth': datetime.date(2013, 11, 12),
            'privacy': True,
        }
        profile = UserProfile.objects.get(user_id=self.user.id)
        self.assertDictContainsSubset(expected, profile.__dict__)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.first_name, 'Joe')
        self.assertEqual(user.last_name, 'Doe')

    def test_user_profile(self):
        self.assertIsNotNone(self.user.userprofile)

    def test_user_profile_privacy(self):
        self.assertFalse(self.user.userprofile.privacy)

    def test_user_member_department_models(self):
        # Although this may look like testing ORM API I thought it
        # would be good to just write a test to show how we expect
        # membership to work
        department = DepartmentFactory()
        account = AccountFactory(department=department)
        user2 = UserFactory()
        # Member is a set of users (user profiles)
        # - eg. a house with one address
        account.accountmembership_set\
            .create(user_profile=self.user.userprofile)
        account.accountmembership_set.create(user_profile=user2.userprofile)
        self.assertEqual(2, account.profiles.all().count())

        # we don't have to have a fresh copy of dept
        self.assertEqual(1, department.accounts.count())
        department.accounts.all().delete()
        self.assertEqual(0, department.accounts.count())