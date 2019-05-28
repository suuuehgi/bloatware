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
./packman.py list --regexp 'samsung(?!\.)' --identify
```

## Usage

```
> ./packman.py list -h
usage: packman.py list [-h] [-t {3,a,d,e,s,u}] [-f FILTER] [-r REGEXP]
                       [--flatten] [--uninstall] [--identify]
                       [--identifyfirst]

optional arguments:
  -h, --help            show this help message and exit
  -t {3,a,d,e,s,u}, --type {3,a,d,e,s,u}
                        Type of packages: 3: third party packages, a: all, d:
                        disabled packages, e: enabled packages, s: system
                        packages, u: uninstalled
  -f FILTER, --filter FILTER
                        Filter by string
  -r REGEXP, --regexp REGEXP
                        Filter by regular expression
  --flatten             Print findings as string of numbers
  --uninstall           Uninstall findings
  --identify            Try to identify package using PlayStore after --filter
                        and --regexp
  --identifyfirst       Try to identify package using PlayStore before
                        --filter and --regexp (might take long)
```

```
> ./packman.py -h
usage: packman.py [-h] {list,uninstall,reinstall} ...

Handle apps

positional arguments:
  {list,uninstall,reinstall}
    list                List installed packages
    uninstall           Uninstall packages
    reinstall           Reinstall packages

optional arguments:
  -h, --help            show this help message and exit
```
