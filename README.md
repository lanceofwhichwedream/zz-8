# ZZ-8
zz-8 is a discord bot built in discord for the purposes of working more with python and discord

# Development installation
It is recommended that one use pipenv to install the required dependencies and pyenv to install
the required python version however a requirements.txt has also been provided

pyenv and pipenv method: 
												 ```
												 pyenv install 3.6.8
												 pyenv local 3.6.8
												 pipenv install --dev
												 ```

requirements.txt method: `pip install -r requirements-dev.txt`

# Deployment
This project is intended to be deployed into docker using a mixture of Jenkins packer and ansible.

First) Jenkins will detect a merge into master from a github webhook.

Second) Jenkins will start deploying the new image according to the JenkinsFile

Third) The Jenkins file will execute packer which will execute the ansible playbooks 
included in ../ansible into a docker containerand it will then commit that container

Fourth) Jenkins will start the new docker container

More to come
