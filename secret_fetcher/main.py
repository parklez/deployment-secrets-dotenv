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


def _write_deployment_env(variables: list, env_output='.env') -> None:
    with open(env_output, 'w') as f:
        for variable in variables:
            f.write(f'{variable.get("name")}={variable.get("value")}' + '\n')


def resolve_variables(variables: list, deploy_env: str) -> list:
    for variable in variables:
        # Secret name in kubernetes
        secret_name = variable.get('valueFrom', {}).get(
            'secretKeyRef', {}).get('name')
        # Replaces key names in case specified
        if secret_name and deploy_env: 
            secret_name = secret_name.replace('$DEPLOY_ENV', deploy_env)
        # Checks for either hardcoded values or for already decoded values
        has_value = variable.get('value')
        if not secret_name or has_value:
            continue
        value = subprocess.run(
            ['kubectl', 'get', 'secret', secret_name, '-o', 'json'], capture_output=True)
        try:
            value = json.loads(value.stdout)
        except json.decoder.JSONDecodeError:
            raise Exception(f'Failed to load JSON from "{secret_name}" - Please check your access!')
        secret_values = value['data']
        decode_secrets(secret_values, variables)
    return variables


def get_variables_from_file(deployment: str) -> list:
    deployment_path = retrieve_files_pathlib(deployment)
    if not deployment_path:
        raise FileNotFoundError(f'No *.yml files found at: "{deployment}"')
    with open(deployment_path[0]) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    # This is the list of variables that the .env possibly needs
    # For OpenShift
    envs = data.get('spec', {}).get('containers', [{}])[0].get('env')
    if envs:
        return envs
    # For ???
    envs = data.get('spec', {}).get('env')
    if envs:
        return envs
    # For Kubernetes
    return data['spec']['template']['spec']['containers'][0]['env']


@click.group()
def cli():
    pass


@click.command()
@click.option('--env-example', default='.env-example', help='Path to template file for environment variables. Default: ".env-example".')
@click.option('--env-output', default='.env', help="Path to output environment file. Default: '.env'")
@click.option('--deployment', default='.travis', help='Path to Deployment "*.yml" folder, not the file! Default: "./.travis"')
@click.option('--deploy-env', default='dev', help='Replaces "$DEPLOY_ENV" in "name" key from secret. Default: "dev".')
def write_from_example(env_example: str, env_output: str, deployment: str, deploy_env: str) -> None:
    variables = get_variables_from_file(deployment)
    # Expands each object with decoded values
    decoded_variables = resolve_variables(variables, deploy_env)
    _write_from_example(decoded_variables, env_example, env_output)


@click.command()
@click.option('--env-output', default='.env', help="Path to output environment file. Default: '.env'")
@click.option('--deployment', default='.travis', help='Path to Deployment "*.yml" folder, not the file! Default: "./.travis"')
@click.option('--deploy-env', default='dev', help='Replaces "$DEPLOY_ENV" in "name" key from secret. Default: "dev".')
def write_deployment_env(env_output: str, deployment: str, deploy_env: str) -> None:
    variables = get_variables_from_file(deployment)
    # Expands each object with decoded values
    decoded_variables = resolve_variables(variables, deploy_env)
    _write_deployment_env(decoded_variables, env_output)


cli.add_command(write_from_example)
cli.add_command(write_deployment_env)

if __name__ == '__main__':
    cli()
