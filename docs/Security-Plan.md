This is mostly clobbered together from a few emails I(Ethan) sent to the MSD team, so the formatting may not be perfect, but it should still be an in depth overview of the security procedure. 

This ensures that both the server and the device have an impossible-to-fake method of verifying the existance of eachother. The device has a cert from the server that it can use to verify the server's identity, and the server has the device name/serial values. Serial is never translated over the internet except through a secure https connection on the normal website, while logged in as a trail manager(or admin, but we dont know that one yet)

Locking creating the devices behind trail manager or above allows us to take advantage of thinking "what's the worst that can happen if someone is capible of hacking to spoof a device?". Someone spoofing a device to fool the server is obviously a problem. What's the worst that can happen if a trail manager gets hacked normally? They'd be able to destroy or steal all of our trail data. Now if a trail manager is the lowest level that can create a device as well, what's the worst that can happen? Still what I said before, spoofing is pretty useless at this access level. As such, it's a reasonable security measure by that logic. 

Devices wont be able to properly communicate with the server until they pass this verification and can then set up a mutual tls connection to securely transmit data. The server will reject it. Devices will have to obtain, and maintain(renew in case of experiaton) their own certificates from our own self hosted certificate authority. AWS can do this for us but it's $400+ monthly MINIMUM to even use it, not accounting for usage limits. We don't need to pad bezos' pocket that much. 

This is the primary link that details the main mTLS process that we are following:
https://docs.aws.amazon.com/apigateway/latest/developerguide/rest-api-mutual-tls.html
What's relevant for you is the curl commands for actually sending the certificate. If you want to test with a dummy certificate, .pem files are standardized and you can easily create your own. It'll be a bit(multiple weeks) before we can get you the real certificates to test with though as there are quite a lot of parts we need to build first.  

For implementing everything, I recommend looking into mbedTLS: https://github.com/Mbed-TLS/mbedtls. I believe this is purpose built for our use case, and should have everything we need. Additionally it covers generating the private/public keys, generating the CSR, and the HMAC hashing. There's examples in the readme on how to generate a CSR that you can use.

We're specifically going to use the x519 format for the CSR as well, the only important thing for the CSR is it should have the standard options + device id put into the

Here's a general overview of how hmac works for our api security here: https://www.authgear.com/post/hmac-api-security I believe mbedTLS can do this, just make sure it lines up with the python hmac output result: https://docs.python.org/3/library/hmac.html

I believe mbedTLS should do everything in regards to encryption, certificate verification and the TLS/mTLS handshakes. With that said I am not an embedded dev, I'm familiar with reading and writing c but understanding how to use the library and all the specifics in regards to making it work are most likely up to you all. 

The process for the actual registration with verifying both the device and the server is laid out like this in order. I'm assuming mbedTLS for devices.

**Initial Device Boot and Registration**
- device has baked into it a unique serial number(private, stored securely), a unique device name(public), and a copy of the root certificate as a .pem file
- device turns on
- device uses timestamp server(pick something you can shoot a request to and get a response) to set its internal clock accurately
- mbedTLS generates a public/private key pair for the device. Store the private key securely. 
- mbedTLS uses the key pair to generate a CSR. 
    - Populate the common name field with the public device id(rather than the subject alternative name field, I looked into it further). Most specs online say put a domain name here but for a device like this that doesn't really have such, we can just populate it - with a unique identifier. 
    - Other fields like organization name, country name, etc are optional. Fill these out if you want but we're handling all of this ourselves on the server end so they're mostly useless. 
- Object of {public device id, unix timestamp, CSR} is created, not sure how you want to do this in c really, pick whatever data structure you're comfortable with that can be serialized and set with ease. 
- use mbedTLS to hash the object against the device serial number via HMAC-SHA-512(not 100% sure it has 512, otherwise 256 is fine, look into and lmk)
- Create final object of {{public device id, unix timestamp, CSR}, hmac hash}
- Perform TLS handshake via mbedTLS with new registration API endpoint different than the one you've been using(we'll be working on this soon, more specifics to come)
    - Root certificate used to verify connection
- Send get request to endpoint containing the data object 
- Request returns a certificate unique to the device as a .pem file, store this securely
    - Save yourself the time later, parse the cert, fetch the expiration date, and store it separately as well


**Device mTLS Operation**
- Use main API that you've been using
    - Do note we're currently adjusting this to use a custom domain name, the actual url might change but the core functionality is the same
- mbedTLS should be able to present the cert where needed to perform the mTLS handshake for AWS
- Append your curl requests with --key <path-to-key> where this is the private key for the device, and --cert <path-to-cert> where this is the certificate you stored at the end of registration
- Results returned work as normal
- If a device's certificate is revoked or expired, we'll probably return some sort of error code. Most likely 403 forbidden. 


**Device Certificate Renewal**
- When sending the daily count for a trail, check the current system time against the cert's stored expiration date
- If cert is within 10 days of expiration, request a certificate renewal
- If cert is expired, re-generate a CSR and go through the full process of device id/timestamp/csr/hash again to the main registration point
    - This should never happen unless a device goes offline or out of internet range for over 10 days straight prior to expiration and reconnects after the cert expires
- If cert is not expired but within the 10 days of expiration threshold 
    - mTLS handshake with your expired/near expired certificate to a different point in the registration API
    - Server will return a new certificate, save it along with the new expiration date