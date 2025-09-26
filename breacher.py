#!/usr/bin/env python3
import requests
import threading
import argparse
import os
import sys
import time

# -----------------------
# Arguments (unchanged)
# -----------------------
parser = argparse.ArgumentParser()
parser.add_argument("-u", help="target url", dest="target")
parser.add_argument("--path", help="custom path prefix", dest="prefix")
parser.add_argument("--type", help="set the type i.e. html, asp, php", dest="type")
parser.add_argument("--fast", help="uses multithreading", dest="fast", action="store_true")
args = parser.parse_args()

# -----------------------
# Helpers
# -----------------------
def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def short_banner():
    print('''\033[1;34m______   ______ _______ _______ _______ _     _ _______  ______
|_____] |_____/ |______ |_____| |       |_____| |______ |_____/
|_____] |    \_ |______ |     | |_____  |     | |______ |    \_
                   CYBER ALPHA

                          \033[37mMade with \033[91m<3\033[37m By D3V\033[1;m''')
    print()
    print("  I am not responsible for your actions. If something errors out, the target may not be responding.")
    print('\033[1;31m--------------------------------------------------------------------------\033[1;m\n')

# -----------------------
# Prepare target URL (keeps your original logic)
# -----------------------
target = args.target
try:
    target = target.replace("https://", "")
except:
    print('\033[1;31m[-]\033[1;m -u argument is not supplied. Enter python breacher -h for help')
    sys.exit(1)

target = target.replace("http://", "")
target = target.replace("/", "")
target = "http://" + target
if args.prefix is not None:
    target = target + args.prefix

# -----------------------
# robots.txt quick check
# -----------------------
def show_robots():
    try:
        r = requests.get(target + "/robots.txt", timeout=6)
        if "<html>" in r.text:
            print("  \033[1;31m[-]\033[1;m Robots.txt not found\n")
        else:
            print("  \033[1;32m[+]\033[0m Robots.txt found. Check for any interesting entry\n")
            print(r.text)
    except Exception:
        print("  \033[1;31m[-]\033[1;m Robots.txt not found\n")

# -----------------------
# Core scanner (preserved logic)
# -----------------------
def scan(links):
    """
    For each path in links, request the combined URL and print a message
    according to the HTTP status code. This is the original logic you had.
    """
    total = len(links)
    for idx, link in enumerate(links, start=1):
        url = target + link
        try:
            r = requests.get(url, timeout=6)
            http = r.status_code
        except Exception:
            # Network error — print a consistent message but continue.
            print(f"  \033[1;31m[-]\033[1;m {url} (request error)")
            continue

        if http == 200:
            print(f"  \033[1;32m[+]\033[0m Admin panel found: {url}")
        elif http == 404:
            print(f"  \033[1;31m[-]\033[1;m {url}")
        elif http == 302:
            print(f"  \033[1;32m[+]\033[0m Potential EAR vulnerability found : {url}")
        else:
            print(f"  \033[1;31m[-]\033[1;m {url}")

        # simple progress hint
        print(f"    ({idx}/{total}) checked\n")

# -----------------------
# Path loader (keeps your filtering logic)
# -----------------------
paths = []

def get_paths(type_arg):
    """
    Read 'paths.txt' and append lines to the global `paths` list according
    to the same type filtering rules you originally wrote.
    """
    global paths
    try:
        with open("paths.txt", "r") as wordlist:
            for path in wordlist:
                path = str(path.replace("\n", ""))
                try:
                    if "asp" in type_arg:
                        if "html" in path or "php" in path:
                            pass
                        else:
                            paths.append(path)
                    if "php" in type_arg:
                        if "asp" in path or "html" in path:
                            pass
                        else:
                            paths.append(path)
                    if "html" in type_arg:
                        if "asp" in path or "php" in path:
                            pass
                        else:
                            paths.append(path)
                except:
                    paths.append(path)
    except IOError:
        print("\033[1;31m[-]\033[1;m Wordlist not found!")
        sys.exit(1)

# -----------------------
# Small preview of 'tools' (first few lines of paths.txt) for the menu
# -----------------------
def preview_tools(n=8):
    """Return up to n sample paths from paths.txt to show in the menu."""
    samples = []
    try:
        with open("paths.txt", "r") as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                samples.append(line.strip())
    except IOError:
        samples = ["(paths.txt missing)"]
    return samples

# -----------------------
# Interactive menu (human-friendly)
# -----------------------
def menu():
    clear_screen()
    short_banner()
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

    choice = input("Choose an option (1-3) [default 1]: ").strip()
    if choice == "" or choice == "1":
        return "normal"
    if choice == "2":
        return "fast"
    return "exit"

# -----------------------
# Runner: keeps threading behavior but fixes Python3 slice division
# -----------------------
def run_scan(mode):
    # Ensure type_arg is a string to avoid None issues
    type_arg = args.type or ""
    get_paths(type_arg)

    if not paths:
        print("\nNo paths loaded from paths.txt. Nothing to scan.")
        return

    if mode == "fast" or args.fast:
        # split list using integer division so it works on Python 3
        mid = len(paths) // 2
        paths1 = paths[:mid]
        paths2 = paths[mid:]

        def part1():
            scan(paths1)

        def part2():
            scan(paths2)

        t1 = threading.Thread(target=part1)
        t2 = threading.Thread(target=part2)
        t1.start()
        t2.start()
        # show a small spinner while threads run (user-friendly)
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
        scan(paths)

# -----------------------
# Main entry
# -----------------------
if __name__ == "__main__":
    clear_screen()
    short_banner()

    # If user already passed --fast on CLI, run immediately (keeps behavior)
    if args.fast:
        run_scan("fast")
        sys.exit(0)

    # Otherwise show interactive menu
    mode = menu()
    if mode == "exit":
        print("Goodbye.")
        sys.exit(0)

    clear_screen()
    short_banner()
    print("Starting scan (mode: {})...\n".format(mode))
    run_scan(mode)
