# deployment-secrets-dotenv
An automated way to get your projects up and running by fetching all the secrets necessary from Kubernetes, writing them into an .env file.

<p align="center">
  <img src="front.png">
</p>

- Kubernetes has a feature called Secrets <> where system administrators can store environment variables for their applications. These secrets are stored in base64 and can be accessed one by one using CLI commands OR by using an UI interface.
- It's a time consuming and painstaking process to setup multiple applications to run **locally** by what Kubernetes offers alone (manually CTRL+C -> CTRL+V from UI or CLI).
- This small CLI tool I made reads a given deployment.yml file and fetches each necessary secret, decodes them, and writes into a dotenv file which many developers use to run applications locally.

## Requirements  🛠
 - Python 3.7 - 3.10
 - Kubernetes CLI (kubectl)

## Installing  ⚙️
Clone this repository and using a terminal window, write the following:
```sh
pip3 install .
```
This way the tool is globally available in your machine via terminal.

## How to use?  📖

This script was made with this structure in mind (you might have something similar)

```sh
my-app-example/
|-- .travis/
|   |-- deployment"*.yml"
|-- .env-example
```
#### A. Fetch (deployment secrets) and write into .env file
```
$ secrets write-deployment-env --help                                                                         
Usage: secrets write-deployment-env [OPTIONS]

Options:
  --env-output TEXT  Path to output environment file. Default: '.env'
  --deployment TEXT  Path to Deployment "*.yml" folder, not the file! Default:
                     "./.travis"
  --deploy-env TEXT   Replaces "$DEPLOY_ENV" in "name" key from secret.
                      Default: "dev".
  --help             Show this message and exit.
```
```sh
$ secrets write-deployment-env --deployment <path to deployment.yml folder> --env-output <path to .env output>
```

#### B. Fetch (deployment secrets) and fullfil .env-example template into .env file
```
$ secrets write-from-example --help
Usage: secrets write-from-example [OPTIONS]

Options:
  --env-example TEXT  Path to template file for environment variables.
                      Default: ".env-example".
  --env-output TEXT   Path to output environment file. Default: '.env'
  --deployment TEXT   Path to Deployment "*.yml" folder, not the file!
                      Default: "./.travis"
  --deploy-env TEXT   Replaces "$DEPLOY_ENV" in "name" key from secret.
                      Default: "dev".
  --help              Show this message and exit.
```
```sh
$ secrets write-from-example --deployment <path to deployment.yml folder> --env-example <path to .env-example template> --env-output <path to .env output>
```

#### C. Fetch "env" from running pod and save into .env file
```
$ secrets write-pod-env --help                                                                 
Usage: secrets write-pod-env [OPTIONS]

Options:
  --pod TEXT         Pod name. Example: "my-cool-app-1234".
  --env-output TEXT  Path to output environment file. Default: '.env-<pod>'
  --help             Show this message and exit.
```
```sh
$ secrets write-pod-env --pod <my-cool-app-1234> --env-output <path to .env output>
```

#### Further reading 📝

https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html

https://medium.com/nerd-for-tech/how-to-build-and-distribute-a-cli-tool-with-python-537ae41d9d78

https://github.com/pypa/sampleproject

https://packaging.python.org/en/latest/tutorials/packaging-projects/