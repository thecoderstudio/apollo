import os

from apollo.lib.agent import (AgentBinary, SupportedArch, SupportedOS,
                              create_agent_binary)


def test_create_agent_binary():
    path: str

    for binary in create_agent_binary(SupportedOS.LINUX, SupportedArch.AMD_64):
        assert binary.target_os == SupportedOS.LINUX
        assert binary.target_arch == SupportedArch.AMD_64
        path = binary.path
        assert os.path.isfile(path)

    # Assert binary gets deleted
    binary = None
    assert not os.path.isfile(path)


def test_delete_agent_binary():
    binary = AgentBinary(SupportedOS.LINUX, SupportedArch.AMD_64)
    binary.delete()
    assert not os.path.isfile(binary.path)
