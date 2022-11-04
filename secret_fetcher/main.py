import json
import base64
import subprocess
import pathlib

import yaml
import click


def retrieve_files_pathlib(path: str) -> list:
    return [file for file in pathlib.Path(path).rglob('*.yml')]


def decode_secrets(secret: list, variables: list) -> None:
    for variable in variables:
        # Secret key
        key = variable.get('valueFrom', {}).get('secretKeyRef', {}).get('key')
        if not key:
            continue

        # In any given iteration, there's not guarantee the current secret contains all the keys needed.
        value = base64.b64decode(secret.get(key, '')).decode('utf-8')
        if value:
            variable['value'] = f'"{value}"'


def _write_from_example(variables: list, env_reference: str, env_output='.env') -> None:
    env_output = open(env_output, 'w')
    env_reference = open(env_reference, 'r')

    for line in env_reference.readlines():
        pair = line.split('=')
        if len(pair) != 2:
            env_output.write(line)
            continue
        value = list(filter(lambda item: item.get(
            'name') == pair[0], variables))
        if value:
            env_output.write(f'{pair[0]}={value[0]["value"]}' + '\n')
        else:
            env_output.write(line)

    env_reference.close()
    env_output.close()


def _write_pod_env(variables: list, env_output='.env') -> None:
    with open(env_output, 'w') as f:
        for variable in variables:
            f.write(f'{variable.get("name")}={variable.get("value")}' + '\n')


def resolve_variables(variables: list) -> list:
    for variable in variables:
        # Secret name in kubernetes
        secret_name = variable.get('valueFrom', {}).get(
            'secretKeyRef', {}).get('name')
        # Checks for either hardcoded values or for already decoded values
        has_value = variable.get('value')
        if not secret_name or has_value:
            continue
        value = subprocess.run(
            ['kubectl', 'get', 'secret', secret_name, '-o', 'json'], capture_output=True)
        value = json.loads(value.stdout)
        secret_values = value['data']
        decode_secrets(secret_values, variables)
    return variables


@click.group()
def cli():
    pass


@click.command()
@click.option('--env-example', default='.env-example', help='Path to template file for environment variables. Default: ".env-example".')
@click.option('--env-output', default='.env', help="Path to output environment file. Default: '.env'")
@click.option('--deployment', default='.travis', help='Path to Deployment "*.yml" folder, not the file! Default: "./.travis"')
def write_from_example(env_example: str, env_output: str, deployment: str) -> None:
    deployment_path = retrieve_files_pathlib(deployment)
    if not deployment_path:
        raise FileNotFoundError('Deployment file *.yml not found.')
    with open(deployment_path[0]) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    # This is the list of variables that the .env possibly needs
    variables = data['spec']['template']['spec']['containers'][0]['env']
    # Expands each object with decoded values
    variables = resolve_variables(variables)
    _write_from_example(variables, env_example, env_output)


@click.command()
@click.option('--env-output', default='.env', help="Path to output environment file. Default: '.env'")
@click.option('--deployment', default='.travis', help='Path to Deployment "*.yml" folder, not the file! Default: "./.travis"')
def write_pod_env(env_output: str, deployment: str) -> None:
    deployment_path = retrieve_files_pathlib(deployment)
    if not deployment_path:
        raise FileNotFoundError('Deployment file *.yml not found.')
    with open(deployment_path[0]) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    # This is the list of variables that the .env possibly needs
    variables = data['spec']['template']['spec']['containers'][0]['env']
    # Expands each object with decoded values
    variables = resolve_variables(variables)
    _write_pod_env(variables, env_output)


cli.add_command(write_from_example)
cli.add_command(write_pod_env)

if __name__ == '__main__':
    cli()
