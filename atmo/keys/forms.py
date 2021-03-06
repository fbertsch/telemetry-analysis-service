# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_ssh_public_key

from django import forms
from django.core.exceptions import ValidationError

from .models import SSHKey
from .utils import calculate_fingerprint
from ..forms.mixins import CreatedByModelFormMixin, FormControlFormMixin


class SSHKeyForm(FormControlFormMixin, CreatedByModelFormMixin):
    prefix = 'sshkey'

    key_file = forms.FileField(
        label='Optionally select a key file (ends with .pub) from your Computer here:',
        help_text='This can usually be found in <code>~/.ssh/</code>.',
        required=False,
    )

    def clean_key(self):
        key = self.cleaned_data['key'].strip()
        if len(key) > 100000:
            raise ValidationError(
                'The submitted key was larger than 100kB, '
                'please submit a smaller one'
            )

        try:
            load_ssh_public_key(key, backend=default_backend())
        except ValueError:
            raise ValidationError(
                'The submitted key is invalid or misformatted.'
            )
        except UnsupportedAlgorithm:
            raise ValidationError(
                'The submitted key is not supported. It should start with '
                'one of the following prefixes: %s.' %
                ', '.join(SSHKey.VALID_PREFIXES)
            )
        fingerprint = calculate_fingerprint(key)
        if self.created_by.created_sshkeys.filter(fingerprint=fingerprint).exists():
            raise ValidationError(
                'There is already a SSH key with the fingerprint %s. '
                'Please try a different one or use the one already uploaded.' % fingerprint,
            )
        return key

    class Meta:
        model = SSHKey
        fields = ['title', 'key', 'key_file']
        widgets = {
            'key': forms.Textarea(
                attrs={
                    'placeholder': 'Drag and drop a key file with the ".pub" '
                                   'file extension here, paste the content '
                                   'manually or use the file selector below',
                }),
        }
