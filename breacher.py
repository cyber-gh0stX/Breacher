#!/usr/bin/env python3

import requests
import threading
import argparse
import os
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("-u", help="target url", dest='target')
parser.add_argument("--path", help="custom path prefix", dest='prefix')
parser.add_argument("--type", help="set the type i.e. html, asp, php", dest='type')
parser.add_argument("--fast", help="uses multithreading", dest='fast', action="store_true")
args = parser.parse_args()

# If -u wasn't supplied, prompt so the interactive menu will show
if not args.target:
    try:
        provided = input("Enter target (example.com) or press Enter to exit: ").strip()
        if not provided:
            print("No target provided. Exiting.")
            sys.exit(0)
        args.target = provided
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)

# cross-platform clear
def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# banner (raw string to avoid escape warnings)
def banner():
    b = r'''
\033[1;34m______   ______ _______ _______ _______ _     _ _______  ______
|_____] |_____/ |______ |_____| |       |_____| |______ |_____/
|_____] |    \_ |______ |     | |_____  |     | |______ |    \_
                   CYBER ALPHA

                          \033[37mMade with \033[91m<3\033[37m By D3V\033[1;m'''
    print(b)
    print()
    print("  I am not responsible for your actions. If something errors out, the target may not be responding.")
    print('\033[1;31m--------------------------------------------------------------------------\033[1;m\n')

# Prepare target exactly like original logic
target = args.target
try:
    target = target.replace('https://', '')
except:
    print ('\033[1;31m[-]\033[1;m -u argument is not supplied. Enter python breacher -h for help')
    quit()

target = target.replace('http://', '')
target = target.replace('/', '')
target = 'http://' + target
if args.prefix != None:
    target = target + args.prefix

# quick robots.txt check (UI-only)
def show_robots():
    try:
        r = requests.get(target + '/robots.txt', timeout=6)
        if '<html>' in r.text:
            print ('  \033[1;31m[-]\033[1;m Robots.txt not found\n')
        else:
            print ('  \033[1;32m[+]\033[0m Robots.txt found. Check for any interesting entry\n')
            print (r.text)
    except:
        print ('  \033[1;31m[-]\033[1;m Robots.txt not found\n')

print_menu_sample_count = 8
def preview_tools(n=print_menu_sample_count):
    samples = []
    try:
        with open('paths.txt', 'r') as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                samples.append(line.strip())
    except IOError:
        samples = ["(paths.txt missing)"]
    return samples

# ========== ORIGINAL scanning logic (kept intact) ==========
def scan(links):
    for link in links: #fetches one link from the links list
        link = target + link # Does this--> example.com/admin/
        try:
            r = requests.get(link, timeout=6) #Requests to the combined url
            http = r.status_code #Fetches the http response code
        except Exception:
            # network errors shouldn't stop whole run — report and continue
            print('  \033[1;31m[-]\033[1;m %s (request error)' % link)
            continue

        if http == 200: #if its 200 the url points to valid resource i.e. admin panel
            print ('  \033[1;32m[+]\033[0m Admin panel found: %s'% link)
        elif http == 404: #404 means not found
            print ('  \033[1;31m[-]\033[1;m %s'% link)
        elif http == 302: #302 means redirection
            print ('  \033[1;32m[+]\033[0m Potential EAR vulnerability found : ' + link)
        else:
            print ('  \033[1;31m[-]\033[1;m %s'% link)

paths = [] #list of paths
def get_paths(type):
    try:
        with open('paths.txt','r') as wordlist: #opens paths.txt and grabs links according to the type arguemnt
            for path in wordlist: #too boring to describe
                path = str(path.replace("\n",""))
                try:
                    if 'asp' in type:
                        if 'html' in path or 'php' in path:
                            pass
                        else:
                            paths.append(path)
                    if 'php' in type:
                        if 'asp' in path or 'html' in path:
                            pass
                        else:
                            paths.append(path)
                    if 'html' in type:
                        if 'asp' in path or 'php' in path:
                            pass
                        else:
                            paths.append(path)
                except:
                    paths.append(path)
    except IOError:
        print ('\033[1;31m[-]\033[1;m Wordlist not found!')
        quit()
# ========== end original logic ==========

# Interactive menu (auto clears, shows tools preview, then runs original flow)
def menu_run():
    while True:
        clear_screen()
        banner()
        show_robots()
        print('\033[1;31m--------------------------------------------------------------------------\033[1;m\n')
        print("Detected tools (sample from paths.txt):")
        for s in preview_tools():
            print("   -", s)
        print()
        print("Menu:")
        print("  1) Start scan (normal)")
        print("  2) Start scan (fast / multithread)")
        print("  3) Exit")
        print()
        try:
            choice = input("Choose an option (1-3) [default 1]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if choice == "" or choice == "1":
            mode = "normal"
        elif choice == "2":
            mode = "fast"
        else:
            print("Goodbye.")
            sys.exit(0)

        # Prepare and run with EXACT original behavior (but fix slicing to work in py3)
        type_arg = args.type or ""
        get_paths(type_arg)
        if not paths:
            print("\nNo paths loaded from paths.txt. Nothing to scan.")
            input("Press Enter to return to menu...")
            continue

        clear_screen()
        banner()
        print("Starting scan (mode: {})...\n".format(mode))

        if mode == "fast" or args.fast:
            # original code split used len(paths)/2 which breaks in py3; use integer division
            mid = len(paths) // 2
            paths1 = paths[:mid]
            paths2 = paths[mid:]
            def part1():
                links = paths1
                scan(links)
            def part2():
                links = paths2
                scan(links)
            t1 = threading.Thread(target=part1)
            t2 = threading.Thread(target=part2)
            t1.start()
            t2.start()
            # small spinner while threads run
            spinner = "|/-\\"
            idx = 0
            while t1.is_alive() or t2.is_alive():
                sys.stdout.write("\rScanning... " + spinner[idx % len(spinner)])
                sys.stdout.flush()
                idx += 1
                time.sleep(0.15)
            t1.join()
            t2.join()
            print("\nScan complete.")
        else:
            links = paths
            scan(links)

        input("\nScan finished. Press Enter to return to menu...")

# If user passed --fast on CLI directly, preserve behavior and run without showing the menu
if args.fast:
    # Prepare paths and run exactly like original script would
    type_arg = args.type or ""
    get_paths(type_arg)
    # If user expects no interactive menu, jump straight to scanning
    mid = len(paths) // 2
    paths1 = paths[:mid]
    paths2 = paths[mid:]
    def part1_cli():
        scan(paths1)
    def part2_cli():
        scan(paths2)
    t1 = threading.Thread(target=part1_cli)
    t2 = threading.Thread(target=part2_cli)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
else:
    # show interactive menu
    menu_run()
