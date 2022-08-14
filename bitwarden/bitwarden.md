# bitwarden

Notes related to the [bitwarden password manager](https://bitwarden.com/).

## bitwarden CLI

<https://bitwarden.com/help/cli/>

Essentials:
```bash
bw --help
bw <command> --help
bw login
bw sync
bw lock
bw logout
```

## Programmatically work with attachments

**WARNING**: *Do not do use `bw` if you have certain types of `PowerShell` logging enabled, for example transcript logging. Similar to enabling clipboard monitoring in Sysmon, you can potentially write your entire vault to disk in clear text.*

- [About Logging in PowerShell](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging?view=powershell-5.1)
- [Script Tracing and Logging](https://docs.microsoft.com/en-us/powershell/scripting/windows-powershell/wmf/whats-new/script-logging?view=powershell-7.2)
- [Transcript Logging](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.host/start-transcript?view=powershell-7.2)
- [About Script Blocks](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_script_blocks?view=powershell-7.2)
- [About PowerShell Profiles](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.2)

*Script tracing* and *script block logging* records the content of scripts themselves for auditing purposes. If a malicious script runs or if a script breaks something, what was executed exactly at the time of running that script is written to a file on disk.

To avoid issues here, use variables for `bw` queries as demonstrated below. The most that can be retrieved in some cases is the name or title of an entry, or it's `itemid` which is acceptable. By doing this the variable runs the query each time the script is invoked rather than hardcoding the variable iteself. You'd need to have a valid login session to return any information.

*Transcript logging* logs all of the text that appears in a terminal session window. This is what can potentially be dangerous if you're searching your vault from PowerShell while this setting is enabled. It can be enabled manually via the `Start-Transcript` cmdlet. This cmdlet can also be enabled in a profile to run every time you open PowerShell. Similar to bash profiles, this means it will invoke `Start-Transcript` anytime you run PowerShell.

To check your PowerShell profile settings to see if this is enabled, review the locations mentioned [here](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.2). Also [check your registry](https://github.com/carlospolop/hacktricks/tree/master/windows-hardening/windows-local-privilege-escalation#powershell-transcript-files) to see if it's enabled there as well.

Retrieve an `itemid`
```bash
# Get an itemid
# This should be only one line, so double quoting "$()" is fine
bw list items --search <query> --pretty | grep -P "^\s+\"id\":\s\".*\",$" | cut -d '"' -f 4

# Get the itemid of your entry named 'GitHub'
bw list items --search GitHub --pretty | grep -P "^\s+\"id\":\s\".*\",$" | cut -d '"' -f 4
# If mutiple results are found, remove the regex to see what's returned and refine your query

# Put the query for the itemid into a variable
ITEM_ID="$(bw list items --search <query> --pretty | grep -P "^\s+\"id\":\s\".*\",$" | cut -d '"' -f 4)"
```

Upload files
```bash
# You'll receive continuous responses to the console window for each attachment uploaded
for file in ../path/*.test; do bw create attachment --file "$file" --itemid "$ITEM_ID"; done

# Confirm the files are listed under "$ITEM_ID" attachments
bw get item "$ITEM_ID" --pretty
```

Delete attachments
```bash
# 80 is arbitrary, just a guess to an upper limit on how many attachments you may have - update this if you really have more
# We grep for any matches *after* (-A) the list of attachments, as other entries above the attachments line (which we don't want) could also match this regex
# DO NOT double quote the command substitution $(), this way each result is it's own line vs the list of results being a single string
ATTACHMENT_IDS=$(bw get item "$ITEM_ID" --pretty | grep -A 80 -Px "^\s+\"attachments\": \[$" | grep -Px "^\s+\"id\": \"\w+\",$" | grep -Fv '-' | cut -d '"' -f 4)

# DO double quote the variable of each "$file", or each line from the output above
for file in $ATTACHMENT_IDS; do bw delete attachment "$file" --itemid "$ITEM_ID"; done
```
