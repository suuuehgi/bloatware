#!/usr/bin/env python3
# coding: utf-8

import argparse, os, re, subprocess, sys
from urllib.error import HTTPError
import urllib.request as urllib2
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Handle apps')

sp = parser.add_subparsers(dest='command')

sp_list = sp.add_parser('list', help='List installed packages')
sp_list.add_argument('-t','--type',     help='Type of packages: 3: third party packages, a: all, d: disabled packages, e: enabled packages, s: system packages, u: uninstalled', choices=[ '3', 'a', 'd', 'e', 's', 'u' ], type=str, default='a')
sp_list.add_argument('-f','--filter',   help='Filter by string', type=str, default=None, required=False)
sp_list.add_argument('-r','--regexp',   help='Filter by regular expression', type=str, default=None, required=False)
sp_list.add_argument('--flatten',       help="Print findings as string of numbers", action='store_true')
sp_list.add_argument('--uninstall',     help="Uninstall findings", action='store_true')
sp_list.add_argument('--identify',      help="Try to identify package using PlayStore after --filter and --regexp", action='store_true')
sp_list.add_argument('--identifyfirst', help="Try to identify package using PlayStore before --filter and --regexp (might take long)", action='store_true')

sp_uninstall = sp.add_parser('uninstall', help='Uninstall packages')
sp_uninstall.add_argument('-p','--packages', help='Uninstall packages (numbers or package names)', nargs='+', default=None, required=True)

sp_reinstall = sp.add_parser('reinstall', help='Reinstall packages')
sp_reinstall.add_argument('-p','--packages', help='Reinstall previously uninstalled packages (numbers or package names)', nargs='+', default=None, required=True)

args = parser.parse_args()

filename = os.path.normpath( os.getcwd() + '/' + 'packages_initial.txt' )
filename_uninstalled = os.path.normpath( os.getcwd() + '/' + 'packages_uninstalled.txt' )

def progress(count, total, status=''):
    # https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def connection_test():
    connection = subprocess.Popen('adb shell exit', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    connection.communicate()
    if connection.returncode == 0: return True
    else: return False

def get_packages(what):
    """Read installed packages from phone or uninstalled from file"""
    if what == 'a':
        packages = subprocess.Popen('adb shell cmd package list packages', shell=True, stdout=subprocess.PIPE)
        packages = packages.stdout.readlines()
        packages = [ ( iii, i.decode().strip().split(':')[1].strip() ) for iii,i in enumerate(packages) ]
    elif what == 'u':
        packages = read_packages(filename_uninstalled)
    else:
        packages = subprocess.Popen('adb shell cmd package list packages -{}'.format(what), shell=True, stdout=subprocess.PIPE)
        packages = packages.stdout.readlines()
        packages = [ ( iii, i.decode().strip().split(':')[1].strip() ) for iii,i in enumerate(packages) ]
    return packages

def write_package(filename, package):
    """Append package to filename"""
    with open(filename, 'a') as f:
        f.write( '{},{}\n'.format( package[0], package[1] ) )

def delete_package(filename, package):
    """Remove package from filename and delete filename if empty"""
    line = '{},{}'.format( package[0], package[1] )
    subprocess.run( 'sed -i "/{}/d" {}'.format(line, filename), shell=True )
    if os.stat(filename).st_size == 0: os.remove(filename)

def init_packages(filename):
    """Fetch initial package list from phone"""
    print("{} not found, fetching initial package list.".format(filename))
    packages = get_packages('a')
    for p in packages: write_package(filename, p)

def read_packages(filename):
    """Read all packages from file"""
    with open(filename, 'r') as f:
        packages = [ tuple( p.strip().split(',') ) for p in f.readlines() ]
    return packages

def find_package(package, packages):
    """Restore entry from number/name from packages"""
    hits = [ p for p in packages if package in p ]
    if len(hits) == 1: return hits[0]
    else: raise RuntimeError("Package {} not found!".format(package))

def identify_package(package):
    try:
        req = urllib2.Request( 'https://play.google.com/store/apps/details?id={}'.format(package) )
        html = urllib2.urlopen(req).read().decode()
    except HTTPError:
        return "Not in PlayStore"
    span = re.findall('<\\s*h1[^>]*>(.*?)<\\s*/\\s*h1>', html)
    if not span == []:
        name = BeautifulSoup( span[0], "lxml" ).find('span').text
        return name
    else:
        return "Not identifiable"

def uninstall_list(packages):
    for p in packages:
        print( 'Uninstalling: {}'.format(p[1]) )
        stdout = uninstall(p[1])
        if not 'Failure' in stdout:
            # Prevent multiple entries
            delete_package(filename_uninstalled, p)
            write_package(filename_uninstalled, p)

uninstall = lambda package: subprocess.Popen( 'adb shell pm uninstall -k --user 0 {}'.format(package), shell=True, stdout=subprocess.PIPE ).stdout.readlines()
reinstall = lambda package: subprocess.Popen( 'adb shell cmd package install-existing {}'.format(package), shell=True, stdout=subprocess.PIPE ).stdout.readlines()

if connection_test() is False:
    print('Could not connect to phone. Make sure "adb shell" is working')
    sys.exit(1)

if not os.path.exists(filename): init_packages(filename)
packages = read_packages(filename)

if args.command == 'list':

    packages_new = list(zip( *get_packages(args.type) ))[1]

    # Assign original numbers
    packages = [ ( p[0], p[1], '' ) for p in packages if p[1] in packages_new ]

    # --identifyfirst
    if args.identifyfirst is True: packages = [ ( p[0], p[1], identify_package(p[1]) ) for ppp,p in enumerate(packages) if not progress(ppp, len(packages), 'Identifying packages') ]
    # --filter
    if not args.filter is None: packages = [ p for p in packages if args.filter.lower() in p[1].lower() or args.filter.lower() in p[2].lower() ]
    # --regexp
    if not args.regexp is None: packages = [ p for p in packages if bool(re.search(args.regexp, p[1])) is True or bool(re.search(args.regexp, p[2])) is True ]
    # --identify
    if args.identify is True and args.identifyfirst is False: packages = [ ( p[0], p[1], identify_package(p[1]) ) for ppp,p in enumerate(packages) if not progress(ppp, len(packages), 'Identifying packages') ]
    print()
    # --flatten
    if args.flatten is True:
        if not packages == []: print( " ".join( list(zip(*packages))[0] ) )
    else:
        for ppp, p, pname in packages:
            if pname == '': print('{:>5}: {}'.format(ppp, p, pname))
            else: print('{:>5}: {:<40} ({})'.format(ppp, p, pname))
    # --uninstall
    if args.uninstall is True: uninstall_list(packages)

elif args.command == 'uninstall':
    packages_uninstall = [ find_package( p.strip(), packages ) for p in args.packages ]
    uninstall_list(packages_uninstall)

elif args.command == 'reinstall':
    packages_install = [ find_package( p.strip(), packages ) for p in args.packages ]
    for p in packages_install:
        print( 'Reinstalling: {}'.format(p[1]) )
        reinstall(p[1])
        delete_package(filename_uninstalled, p)
