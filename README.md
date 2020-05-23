# sendgmail
Send gmail form the commandline

Basic options: to/from/cc/bcc/subject:
```
python3 sendgmail.py --to "..." --from "..." --cc "..." --bcc "..." --subject "..." 
```

Message:
```
python3 sendgmail.py --message "..." 
python3 sendgmail.py --file message.txt
cat message.txt | python3 sendgmail.py
```
If all three options are present, they are processed in the way shown above.

Attachments:
```
python3 sendgmail.py --attach file.pdf [file.pdf] 
```

Credentials: Most either be included on the command line:
```
python3 sendgmail.py --credentials credentials.json --token token.pickle
```
or must be in files credentials.json/token.pickle in the current directory or must be be in 
```
$HOME/.config/sendgmail/credentials.json
$HOME/.config/sendgmail/token.pickle
```
# Configuration
Saved configuration: Can be included on the command line
```
python3 sendgmail.py --configuration config.json
```
or be in a file config.json in the current directory or be in 
```
$HOME/.config/sendgmail/config.json
```
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
"file": "textfile.txt",
"credentials": "credentials.json",
"token": "token.pickle"
}
```
Note that all files (...pdf, textfile.txt, credentials, token) are relative to the config file, unless you use `./`
```
{
...
"attach": [ "./...pdf", "./...jpg", ...],
"file": "./textfile.txt",
"credentials": "./credentials.json",
"token": "./token.pickle"
}
```
