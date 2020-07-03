import logging
import os
import subprocess
import uuid
from enum import Enum

PACKAGE = 'github.com/thecoderstudio/apollo-agent'


class SupportedOS(Enum):
    DARWIN = 'darwin'
    LINUX = 'linux'
    FREEBSD = 'freebsd'
    OPENBSD = 'openbsd'


class SupportedArch(Enum):
    AMD_64 = 'amd64'
    ARM_64 = 'arm64'
    ARM = 'arm'


class AgentBinary:
    def __init__(self, target_os: SupportedOS, target_arch: SupportedArch):
        self.path = f"/tmp/{uuid.uuid4()}"
        self.target_os = target_os
        self.target_arch = target_arch

        # Always make sure to get the latest version
        self._download_source()

        self._compile()

    @staticmethod
    def _download_source():
        subprocess.run(['go', 'get', '-d', '-u', PACKAGE])

    def _compile(self):
        env = os.environ.copy()
        env['GOOS'] = self.target_os.value
        env['GOARCH'] = self.target_arch.value
        subprocess.run(['go', 'build', '-o', self.path, PACKAGE], env=env)

    def delete(self):
        try:
            os.remove(self.path)
        except FileNotFoundError as e:
            logging.debug(str(e))


def create_agent_binary(target_os: SupportedOS, target_arch: SupportedArch):
    binary = AgentBinary(target_os, target_arch)
    try:
        yield binary
    finally:
        binary.delete()
