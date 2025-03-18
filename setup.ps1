<#
[ ] Set execution policy to RemoteSigned (must be done manually)
[ ] Check for winget installation https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget
[x] Check for nvm, AWS CLI, and terraform installation
[x] install node lts and set as default
[ ] walk through the setup of aws account and linking to aws cli
[ ] profit?
#>


Function getInstallStatus
{
    param (
        $appName
    )

    $status = Get-Command $appName -ErrorAction SilentlyContinue

    if ($?){
        return $true
    }
    return $false
}

Function installApp
{
    param (
        $appName
    )

    winget install $appName

    
    
}

Function awsSetupInstructions
{
    Write-Output "The following instructions will walk through the process of setting up an AWS account and linking it to the AWS CLI"
    Read-Host -Prompt "Press Enter to Continue"

    Write-Output "Navigate to http://aws.amazon.com, sign in to an existing account, or create a new account."
    Read-Host -Prompt "Press Enter to Continue"

    Write-Output "Once logged in, navigate to the top right and click your username. Select 'Security credentials' from the dropdown menu."
    Read-Host -Prompt "Press Enter to Continue"

    Write-Output "Scroll down to the section labeled 'Access keys' and follow the prompts to create an access key."
    Write-Output "There will be warning against creating an access key for the root account, it is okay to ignore these warnings."
    Write-Output "Make sure to keep the page that displays the new access key open for the following steps."
    Read-Host -Prompt "Press Enter to Continue"

    Write-Output "The AWS CLI will now be invoked to link your account to the CLI."
    Write-Output "When prompted, enter your access key and press Enter."
    Write-Output "Do the same for your secret access key."
    Write-Output "'Default region name' and 'Default output format' can be left blank"
    Read-Host -Prompt "Press Enter to Continue"

    aws configure

    #test that the linking worked
    aws sts get-caller-identity
    if(!$?){
        Write-Output "AWS Account linking failed, exiting."
        exit 1
    }    

    
    
    
}

Function installNode
{
    $current = nvm current
}



$winget = getInstallStatus("winget")

if ($winget){
    Write-Output "Winget found"
}
else{
    Write-Output "Winget not found"
    exit
    # install winget here
}

Write-Output "Checking for NVM"
$nvm = getInstallStatus("nvm")

if($nvm){
    Write-Output "NVM found."
}
else{
    Write-Output "NVM not found, installing."
    installApp("CoreyButler.NVMforWindows")
}

Write-Output "Checking for AWS CLI"
$aws_cli = getInstallStatus("aws")

if ($aws_cli){
    Write-Output "AWS CLI found."
}
else{
    Write-Output "AWS CLI not found, installing."
    installApp("Amazon.AWSCLI")
}

Write-Output "Checking for Terraform"
$terraform = getInstallStatus("terraform")

if($terraform){
    Write-Output "Terraform found."
}
else{
    Write-Output "Terraform not found, installing."
    installApp("Hashicorp.Terraform")
}

#manually update the nvm env variables so we dont have to restart the powershell session
$env:NVM_HOME = $env:LOCALAPPDATA + '\nvm'
$env:NVM_SYMLINK = 'C:\nvm4w\nodejs'


# reload env variables to access the programs we just installed
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") 

Write-Output "Installing Node LTS"
nvm install lts
nvm use lts

Read-Host -Prompt "Press Enter to Exit"
exit 0
