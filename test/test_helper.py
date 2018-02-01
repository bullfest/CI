from CI.CI_helpers import *


def test_run_commands_positive():
    commands = ["echo hello", "echo bye"]
    command_output = run_commands(commands)
    assert command_output == [b'hello\n', b'bye\n']


def test_run_commands_negative():
    """ First command is invalid, will throw an exception and 'Error' is appended
    to list """
    commands = ["ech hello", "echo hello"]
    command_output = run_commands(commands)
    assert command_output == ["Error", b'hello\n']


def test_clone_repo():
    """ Will return false since we are trying to clone a non-existing repo"""
    assert clone_repo("fsdwe", "~/Desktop/test1") is False


def test_is_successful_command_positive():
    # contract : A successful command returns a string which contains "TEST PASSED"
    # as such the method should return True
    output = "Lorem Ipsum dolori yada TEST PASSED nadie pongo"
    success_regex = "TEST PASSED"
    assert (is_successful_command(output, success_regex)) is True


def test_is_successful_command_negative():
    # contract: A unsuccessful command returns a string which does not contain "TEST PASSED"
    # and therefore should return False
    output = "Lorem Ipsum dolori yada nadie pongo"
    success_regex = "TEST PASSED"
    assert (is_successful_command(output, success_regex)) is False


def test_is_successful_command_regex_positive():
    # contract : A successful command returns a string which contains "TEST PASSED"
    # as such the method should return True
    output = "Lorem Ipsum dolori yada nadie pongo"
    success_regex = "Ipsum.+yada"
    assert (is_successful_command(output, success_regex)) is True


def test_is_successful_command_regex_negative():
    # contract : A successful command returns a string which contains "TEST PASSED"
    # as such the method should return True
    output = "Lorem Ipsum dolori yada TEST PASSED nadie pongo"
    success_regex = "[^L]orem"
    assert is_successful_command(output, success_regex) is False
