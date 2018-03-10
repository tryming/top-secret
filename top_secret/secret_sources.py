import abc
import os

from .exceptions import SecretMissingError


class BaseSecretSource(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get(self, name):
        pass


class EnvironmentVariableSecretSource(BaseSecretSource):

    def get(self, name):
        value = os.environ.get(name)
        if value is None:
            raise SecretMissingError(
                f'Cannot get secret {name!r}. '
                f'Environment variable {name!r} is not set.'
            )
        return value


class FileSecretSource(BaseSecretSource):

    def __init__(self, base_path, postfix=None, stripe_whitespaces=True):
        self.base_path = base_path
        self.postfix = postfix
        self.stripe_whitespaces = stripe_whitespaces

    def get(self, name, stripe_whitespaces=None):
        path = self.build_path(name)
        self.raise_on_no_file(path, name)
        secret = self.read_secret(path, stripe_whitespaces)
        return secret

    def build_path(self, name):
        if self.postfix:
            name = '{}.{}'.format(name, self.postfix.lstrip('.'))

        if os.path.isabs(name):
            return name
        return os.path.join(self.base_path, name)

    def raise_on_no_file(self, path, name):
        if not os.path.exists(path):
            raise SecretMissingError(
                f'Cannot get secret {name!r}. '
                f'File {path} doesn\'t exist.'
            )

    def read_secret(self, path, stripe_whitespaces):
        with open(path) as fd:
            secret = fd.read()

        if stripe_whitespaces is None:
            stripe_whitespaces = self.stripe_whitespaces

        if stripe_whitespaces:
            secret = secret.strip()

        return secret
