import json
from unittest.mock import mock_open, patch

from CI.history_helpers import log_process


def test_log_process_positive():
    """ Contract: Checks if a log file with the given data is
    written to the given file path"""
    repo_name = "foo/bar"
    sha = "f00ba2"
    time = "2015-05-05T23:40:29Z"
    branch = 'random_branch'

    command_list = ["echo hello", "echo bye"]
    command_status = [True, True]
    command_output = ['hello\n', 'bye\n']

    # Webhook post data
    webhook_data = f"""{{
        "ref": "refs/heads/{branch}",
        "head_commit": {{
            "id": "{sha}",
            "timestamp": "{time}"
        }},
        "repository": {{
            "full_name": "{repo_name}"
        }}
    }}"""

    m = mock_open()

    with patch('CI.history_helpers.open', m):
        with patch('CI.history_helpers.os.listdir'):
            with patch('os.path.isdir'):
                log_process(command_list, command_status, command_output, webhook_data)

    m.assert_called_once_with('history/foo/bar/0.json', 'w')

    webhook_data_formated_string = json.dumps(json.loads(webhook_data))

    handle = m()
    handle.write.assert_called_once_with(
        f'{{"date": "2015-05-05T23:40:29Z", "hash": "f00ba2", "branch": "random_branch", "webhook_data": '
        f'{webhook_data_formated_string}, "results": [{{"command": "echo hello", "status": true, "output": '
        f'"hello\\n"}}, {{"command": "echo bye", "status": true, "output": "bye\\n"}}], "id": 0}}'
    )