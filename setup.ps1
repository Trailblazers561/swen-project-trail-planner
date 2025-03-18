<#
[ ] Set execution policy to RemoteSigned (must be done manually)
[ ] Check for winget installation https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget
[x] Check for nvm, AWS CLI, and terraform installation
[ ] install node lts and set as default
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

$winget = getInstallStatus("winget")

if ($winget){
    Write-Output "Winget found"
}
else{
    Write-Output "Winget not found, installing."
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

