<#
[ ] Set execution policy to RemoteSigned (must be done manually)
[ ] Check for winget installation https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget
[ ] Check for nvm, AWS CLI, and terraform installation
[ ] install node lts and set as default
[ ] walk through the setup of aws account and linking to aws cli
[ ] profit?
#>


Function getInstallStatus{
    param (
        $appName
    )

    $status = Get-Command $appName -ErrorAction SilentlyContinue

    if ($?){
        return True
    }
    else{
        return False
    }
}




$winget = Get-Command "winget" -ErrorAction SilentlyContinue

if ($winget){
    Write-Output "Winget found"
}
else{
    Write-Output "Winget not found"
    Write-Output "Installing Winget"
    # install winget here
}


