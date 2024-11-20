Miss extension methods from other languages? Python can have those too.

## Installation

```shell
pip install extensified==0.3.0
```

## Usage

```python
from dataclasses import dataclass
from datetime import datetime

from extensified import extension_on


@dataclass
class Customer:

    name: str
    email: str
    created_at: datetime = datetime.now()


@extension_on(Customer)
class CustomerStringReprExtension:

    @property
    def rfc5322_email(self) -> str:
        return f'{self.name} <{self.email}>'

    @property
    def ldap_dn(self) -> str:
        email_domain = self.email.split('@')[1]
        return f'cn={self.name},ou=Users,dc={email_domain.replace(".", ",dc=")}'

    @property
    def vcard_name(self) -> str:
        surname = self.name.split()[-1]
        given_names = ' '.join(self.name.split()[:-1])
        return f'FN:{self.name}\nN:{surname};{given_names};;;'


customer = Customer("John Doe", "john@example.com")
print(customer.rfc5322_email)
print(customer.ldap_dn)
print(customer.vcard_name)
```

## Limitations

- Make sure that extension class is imported before its methods are used (i.e. import it in your init code).
- `super()` can't be used in an extension class for now.
- Type checkers won't understand what's going on and will complain about attributes missing.
