# sendgmail

Send gmail from the commandline

Basic options: to/sender/cc/bcc/subject. The following sends an basic message:
```
sendgmail.py --sender "..." --to "..."  --cc "..." --bcc "..." --subject "..." --message "message:
```
In the above `sender` is a single email address, while `to`, `cc` and `bcc` are comma-separated lists of email addresses.

Message options:
```
sendgmail.py --message "..." 
sendgmail.py --mfile message.txt
cat message.txt | sendgmail.py --mfile -
cat message.txt | sendgmail.py [without --mfile or --message specfied]
```
If the first option is used with the others, they are processed in the above order. Note that you can send an empty message using `--message ""`.

You can add another file as a signature:
```
sendgmail.py --sfile signature.txt
```
This is helpful if you are using the configuration below, and you want `sendgmail.py` to handle the signature. However, it has the same effect as adding extra text via `--mfile`.

Attachments:
```
sendgmail.py --attach file.pdf [file.pdf] 
```

# Configuration

Saved configuration: Can be included (1) on the command line
```
sendgmail.py --configuration config.json
```
or (2) be in a file config.json in the current directory.

If those are not the case, but `--sender ABC@DEF` is specified then (3)
```
$HOME/.config/sendgmail/ABC@DEF/config.json
```
is checked. Finally, (4)
```
$HOME/.config/sendgmail/config.json
```
is checked.

The config file looks like
```
{
"to": "...",
"from": "...",
"cc": "...",
"bcc": "...",
"subject": "...",
"attach": [ "...pdf", "...jpg", ...],
"message": "some text",
"mfile": "message.txt",
"sfile": "signature.txt",
"credentials": "credentials.json",
"token": "token.pickle"
}
```
Note that all credentials and token files are relative to the config file, unless you use `./` or '/', i.e.,
```
{
"credentials": "./credentials.json",
"token": "./token.pickle"
}
```
or
```
{
"credentials": "/home/user/somewhere/credentials.json",
"token": "/home/user/somewhere/token.pickle"
}
```

# Credentials / token

Most (1) either be included on the command line:
```
python3 sendgmail.py --credentials credentials.json --token token.pickle
```
or (2) must be in files credentials.json/token.pickle in the current directory or (3) must be specified in the config file (see above).

If none of these, then if `--sender ABC@DEF`, then (4)
```
$HOME/.config/sendgmail/ABC@DEF/credentials.json
$HOME/.config/sendgmail/ABC@DEF/token.pickle
```
is checked and finally (5)
```
$HOME/.config/sendgmail/credentials.json
$HOME/.config/sendgmail/token.pickle
```
is checked. I.e., command line takes highest precedence, `$HOME/.config/sendgmail` takes lowest precedence.

# Requirements
```
pip install google-api-python-client
pip install google-auth-oauthlib
```
