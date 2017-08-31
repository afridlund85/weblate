# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Test for legal stuff."""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings, modify_settings

from weblate.accounts.tests.test_registration import REGISTRATION_DATA
from weblate.legal.models import Agreement
from weblate.trans.tests.test_views import RegistrationTestMixin


class LegalTest(TestCase, RegistrationTestMixin):
    def test_index(self):
        response = self.client.get(reverse('legal:index'))
        self.assertContains(response, 'Legal Terms Overview')

    def test_terms(self):
        response = self.client.get(reverse('legal:terms'))
        self.assertContains(response, 'Terms of Service')

    def test_cookies(self):
        response = self.client.get(reverse('legal:cookies'))
        self.assertContains(response, 'Cookies Policy')

    def test_security(self):
        response = self.client.get(reverse('legal:security'))
        self.assertContains(response, 'Security Policy')

    @modify_settings(SOCIAL_AUTH_PIPELINE={
        'append': 'weblate.legal.pipeline.tos_confirm',
    })
    @override_settings(REGISTRATION_OPEN=True, REGISTRATION_CAPTCHA=False)
    def test_confirm(self):
        """TOS confirmation on social auth."""
        response = self.client.post(
            reverse('register'),
            REGISTRATION_DATA,
            follow=True
        )
        # Check we did succeed
        self.assertContains(response, 'Thank you for registering.')

        # Follow link
        url = self.assert_registration_mailbox()
        response = self.client.get(url, follow=True)
        self.assertTrue(
            response.redirect_chain[-1][0].startswith(
                reverse('legal:confirm')
            )
        )

        # Extract next URL
        url = response.context['form'].initial['next']

        # Try invalid form (not checked)
        response = self.client.post(
            reverse('legal:confirm'),
            {
                'next': url,
            }
        )
        self.assertContains(response, 'This field is required')

        # Actually confirm the TOS
        response = self.client.post(
            reverse('legal:confirm'),
            {
                'next': url,
                'confirm': 1
            },
            follow=True
        )
        self.assertContains(response, 'Your profile')

    @modify_settings(MIDDLEWARE_CLASSES={
        'append': 'weblate.legal.middleware.RequireTOSMiddleware',
    })
    def test_middleware(self):
        user = User.objects.create_user(
            'testuser',
            'noreply@weblate.org',
            'testpassword',
            first_name='Weblate Test',
        )
        # Unauthenticated
        response = self.client.get(reverse('home'), follow=True)
        self.assertContains(response, 'Suggested translations')
        # Login
        self.client.login(username='testuser', password='testpassword')
        # Chck that homepage redirects
        response = self.client.get(reverse('home'), follow=True)
        self.assertTrue(
            response.redirect_chain[-1][0].startswith(
                reverse('legal:confirm')
            )
        )
        # Check that contact works even without TOS
        response = self.client.get(reverse('contact'), follow=True)
        self.assertContains(response, 'You can contact maintainers')
        # Confirm current TOS
        user.agreement.make_current()
        # Homepage now should work
        response = self.client.get(reverse('home'), follow=True)
        self.assertContains(response, 'Suggested translations')
