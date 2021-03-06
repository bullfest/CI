import json
import os
import shutil
from datetime import datetime

from flask import request, render_template, abort

from CI import app
from CI.CI_helpers import \
    set_commit_state, clone_repo, read_configfile, \
    run_commands, is_successful_command, try_deploy
from CI.constants import CLONE_FOLDER, CONF, HISTORY_FOLDER
from CI.history_helpers import log_process, get_builds


@app.route('/')
def index():
    """The root endpoint, will not be used in the project,
    but is good for checking setups"""
    return 'Hello, World!'


@app.route('/hooks/github', methods=['POST'])
def github_webhook():
    """Defines and initiates the URL to which events will be sent to.
     The event is triggered upon a push to a branch or repository tag
     push"""

    data = request.get_json()
    print(data)

    head_sha = data['head_commit']['id']
    repo_data = data['repository']

    # noinspection PyBroadException
    try:
        set_commit_state(repo_data['full_name'], head_sha, "pending")

        os.makedirs(
            CLONE_FOLDER + repo_data['full_name'],
            exist_ok=True
        )

        print("Created directory to clone repository into...")

        branch = data['ref'].split('/')[-1]
        clone_repo(
            repo_data['ssh_url'],
            branch,
            f"{CLONE_FOLDER}{repo_data['full_name']}/{head_sha}"
        )

        print("Successfully cloned repository from", repo_data['ssh_url'])

        config = read_configfile(
            f"{CLONE_FOLDER}{repo_data['full_name']}/{head_sha}/{CONF}"
        )

        # Change to repo folder
        main_dir = os.getcwd()
        os.chdir(f"{CLONE_FOLDER}{repo_data['full_name']}/{head_sha}")

        command_results = run_commands(config['commands'])

        print("Successfully ran commands...")
        print("Output:", command_results)

        successful_commands = [
            is_successful_command(*pair)
            for pair in zip(command_results, config['success_strings'])
        ]

        print("Successful tests:", successful_commands)

        if all(successful_commands):
            deploy_msg = try_deploy(config)
        else:
            deploy_msg = ""

        print(deploy_msg)

        # Return to root folder
        os.chdir(main_dir)
        shutil.rmtree(
            path=f"{CLONE_FOLDER}{repo_data['full_name']}/{head_sha}",
            ignore_errors=True
        )

        set_commit_state(
            repo_data['full_name'],
            head_sha,
            "success" if all(successful_commands) else "failure"
        )

        log_process(
            command_list=config['commands'],
            command_status=successful_commands,
            command_output=command_results,
            webhook_data=data
        )

        print("Successfully saved long entry...")

    except Exception as e:
        set_commit_state(
            repo_data['full_name'],
            head_sha,
            "failure"
        )
        print(e)
    return ""  # We have to return something


@app.route('/history/<owner>/<repo>', endpoint="list_builds")
def list_builds(owner, repo):
    """This route collects and displays all
    of the builds for the specified repo"""

    return render_template(
        "listbuilds.html",
        owner=owner,
        repo=repo,
        build_list=get_builds(owner, repo)
    )


@app.route('/history/<owner>/<repo>/<build_id>', endpoint="build_info")
def build_info(owner, repo, build_id):
    """This route collects and displays the specified build file"""
    try:
        build_file_path = f"{HISTORY_FOLDER}{owner}/{repo}/{build_id}.json"
        build_data = json.load(open(build_file_path))
    except FileNotFoundError:
        abort(404)
    return render_template(
        "buildinfo.html",
        status=all([build_data['results'][i]['status']
                    for i in range(len(build_data['results']))]),
        owner=owner,
        repo=repo,
        build_id=build_id,
        date=datetime.strptime(
            build_data["date"].replace(":", ""),
            "%Y-%m-%dT%H%M%S%z"),
        hash=build_data["hash"],
        results=build_data["results"]
    )
