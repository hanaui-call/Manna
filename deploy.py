#!/usr/bin/env python
import argparse
import datetime
import getpass
import subprocess


# FIXME You must enter the server's information properly.
ACCOUNT = 'ubuntu'
HOSTS = 'ec2-54-180-8-69.ap-northeast-2.compute.amazonaws.com'
PROJECT_HOME = '~/Manna'


TARGETS = ['web']

DOCKER_COMPOSE = f"sudo docker-compose -f docker-compose-prod.yml"
FALSE_SENTINEL = "_____FALSE______"


def get_tag():
    tag = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    whoami = getpass.getuser()
    tag += "_{}".format(whoami.decode("utf-8").replace("\n", ""))
    return tag


def execute_remote(commands):
    command = " && ".join(commands)
    print(f"[EXEC] {command}")
    remote_command = f"ssh {ACCOUNT}@{HOSTS} '( {command} ) || ( echo \"{FALSE_SENTINEL}\" 1>&2 )'"
    p = subprocess.Popen(remote_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    lines = []
    success = True
    for line in p.stdout:
        line = line.decode('utf8').rstrip()
        if line == FALSE_SENTINEL:
            success = False
        else:
            lines.append(line)
            print(line)

        if not success:
            print(f"[EXEC] Execute fail")
            raise Exception("Execute fail")

    return "\n".join(lines)


def git_pull(branch_name="master"):
    commands = [
        f"cd {PROJECT_HOME}",
        f"git fetch --all",
        f"git reset --hard origin/{branch_name}",
    ]

    print("#### GIT Pull ######")
    out = execute_remote(commands)

    if "git_pull_error" in out:
        raise Exception('[ERROR] git files cp failed.')


def build_docker(targets):
    if 'web' in targets:
        commands = [
            f"cd {PROJECT_HOME}/web",
            f"python3 dockerfile_generator.py",
            f"cd {PROJECT_HOME}",
            f"{DOCKER_COMPOSE} build web",
        ]
        print(f"#### Build web docker images ######")
        execute_remote(commands)


def restart_targets(targets):
    if targets:
        target_str = " ".join(targets)
        commands = [
            f"cd {PROJECT_HOME}",
            f"{DOCKER_COMPOSE} kill {target_str}",
            f"{DOCKER_COMPOSE} up -d {target_str}",
        ]

        print(f"#### Restart {targets} ######")
        execute_remote(commands)
    else:
        print("No targets")


def main(args):
    git_pull(args.branch)

    if args.target == 'all':
        targets = TARGETS
    elif args.target == "none":
        targets = []
    else:
        targets = args.target.split()

    if args.build:
        build_docker(targets)
    restart_targets(targets)


if __name__ == "__main__":
    def to_bool(v):
        return v.lower() in ['y', 'yes', 'true']

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--branch',
        help='branch name',
        default='master'
    )

    parser.add_argument(
        '--target',
        help=", ".join(TARGETS),
        default='web'
    )

    parser.add_argument(
        '--build',
        help='is build',
        type=to_bool,
        default=True
    )

    main(parser.parse_args())
