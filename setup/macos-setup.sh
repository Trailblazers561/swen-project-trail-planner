#!/bin/zsh

# basic setup
touch ~/.zshrc
xcode-select --install
source ~/.zshrc

aws_setup_instructions() {
    echo "The following instructions will walk through the process of setting up an AWS account and linking it to the AWS CLI"
    vared -p "Press Enter to Continue" -c tmp

    echo "Navigate to http://aws.amazon.com, sign in to an existing account, or create a new account."
    vared -p "Press Enter to Continue" -c tmp

    echo "Once logged in, navigate to the top right and click your username. Select 'Security credentials' from the dropdown menu."
    vared -p "Press Enter to Continue" -c tmp

    echo "Scroll down to the section labeled 'Access keys' and follow the prompts to create an access key."
    echo "There will be warning against creating an access key for the root account, it is okay to ignore these warnings."
    echo "Make sure to keep the page that displays the new access key open for the following steps."
    vared -p "Press Enter to Continue" -c tmp

    echo "The AWS CLI will now be invoked to link your account to the CLI."
    echo "When prompted, enter your access key and press Enter."
    echo "Do the same for your secret access key."
    echo "'Default region name' and 'Default output format' can be left blank"
    vared -p "Press Enter to Continue" -c tmp

    aws configure

    aws_test=$(aws sts get-caller-identity)
    if [ $? -ne 0 ] ; then
        echo "AWS Account linking failed, exiting."
    fi
}

nvm_install_status=$(nvm --version)
if [[ $? -ne 0 ]]; then
    echo "nvm not found, installing"
    # install nvm
    # source: https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
    source ~/.zshrc
fi

node_install_status=$(which node)
if [[ $? -ne 0 ]]; then
    # install latest node lts
    nvm install --lts
    source ~/.zshrc
fi


aws_cli_install_status=$(which aws)
if [[ $? -ne 0 ]]; then
    echo "AWS CLI not found, installing"
    # install the aws cli
    # source: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
    sudo installer -pkg AWSCLIV2.pkg -target /
    source ~/.zshrc
    rm AWSCLIV2.pkg
fi


homebrew_install_status=$(which brew)
if [[ $? -ne 0 ]]; then
    echo "homebrew not found, installing"
    # install homebrew
    # source: https://github.com/Homebrew/install
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    source ~/.zshrc
fi

terraform_install_status=$(which terraform)
if [[ $? -ne 0 ]]; then
    echo "terraform not found, installing"
    # install terraform 
    # source: https://developer.hashicorp.com/terraform/install
    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform
    source ~/.zshrc
fi

aws_setup_instructions

echo "Setup complete, exiting.


