# Remove Android Bloatware

Wrapper script around `adb shell cmd package`.
Packages are being disabled for the current user from userspace (without root) and can easily be enabled again.
The script therefore creates two plain text files to keep track of the changes.

## Dependency

* `adb` (`adb shell` has to work)
* `sed`, `python3`

## Example

```
./packman.py list -f microsoft --uninstall
./packman.py uninstall com.whatsapp
./packman.py uninstall -p 68 84 167 176
./packman.py reinstall -p 68 84 167 176
./packman.py list --regexp 'samsung(?!\.)'
```
