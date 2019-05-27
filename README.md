# Remove Samsung bloatware

Wrapper script around `adb shell cmd package`.
Packages are being disabled for the current user from userspace (without root) and can easily be enabled again.
The script therefore creates two plain text files to keep track of the changes.

## Dependency

* `adb` (`adb shell` has to work)
* `sed`

## Example

```
./samsung.py list -f microsoft --uninstall
./samsung.py uninstall -p 68 84 167 176
./samsung.py reinstall -p 68 84 167 176
./samsung.py list --regexp 'samsung(?!\.)'
```
