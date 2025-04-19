#!/bin/zsh

# basic setup
touch ~/.zshrc
xcode-select --install

nvm_install_status=$(which nvm)
if [[ $nvm_install_status =~ ".*not found" ]]; then
    echo "nvm not found, installing"
    # install nvm
    # source: https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
    source ~/.zshrc
fi

node_install_status=$(which node)
if [[ $node_install_status =~ ".*not found" ]]; then
    # install latest node lts
    nvm install --lts
    source ~/.zshrc
fi


aws_cli_install_status=$(which aws)
if [[ $aws_cli_install_status =~ ".*not found" ]]; then
    echo "AWS CLI not found, installing"
    # install the aws cli
    # source: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
    sudo installer -pkg AWSCLIV2.pkg -target /
    source ~/.zshrc
    rm AWSCLIV2.pkg
fi


homebrew_install_status=$(which brew)
if [[ $homebrew_install_status =~ ".*not found" ]]; then
    echo "homebrew not found, installing"
    # install homebrew
    # source: https://github.com/Homebrew/install
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    source ~/.zshrc
fi

terraform_install_status=$(which terraform)
if [[ $homebrew_install_status =~ ".*not found" ]]; then
    echo "terraform not found, installing"
    # install terraform 
    # source: https://developer.hashicorp.com/terraform/install
    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform
fi

source ~/.zshrc



