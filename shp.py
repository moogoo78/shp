#!/usr/bin/env python
# -.- coding: utf-8 -.-
import os
import argparse
import configparser
from pathlib import Path
import re


def find_file(root, file_path, pattern, flags):
    full_path = Path(root, file_path)
    # check full_path.match(pattern)
    # check is_binary
    output = []
    with open(full_path) as f:
        for index, row in enumerate(f):
            matches = []
            for m in re.finditer(pattern, str(row), flags):
                matches.append(m.group(0))
            if len(matches) > 0:
                for m in matches:
                    row = replace_by_color(row, m, 95) # purple
                # if len(row) < 500: else print (too long)
                output.append('{}: {}'.format(set_color(index+1, 93), row[:-1])) # strip ending linebreak

        #print (set_color(full_path, 91)) # red
    return output

def replace_by_color(string, keyword, color_code):
#    if os.name == "nt":
#        windll.Kernel32.SetConsoleTextAttribute(std_out_handle, 14)
#        print (str(keyword))
#        windll.Kernel32.SetConsoleTextAttribute(std_out_handle, 7)
#    else:
        return string.replace(str(keyword), set_color(str(keyword),95) )

def set_color(keyword, color_code):
    if os.getenv('TERM',None) in ['rxvt','xterm', 'xterm-256color']:
        return str(keyword).replace(str(keyword), '\033[0;'+str(color_code)+'m'+str(keyword)+'\033[m')
        #return '\033[0;' + str(color_code) + 'm' + str(keyword) + '\033[m'
#    elif os.name == "nt":
#        windll.Kernel32.SetConsoleTextAttribute(std_out_handle, 10)
#        print str(keyword)
#        windll.Kernel32.SetConsoleTextAttribute(std_out_handle, 7) # 7 is light grey, 15 is white
    else:
        return str(keyword)

def main(args, config):
    print(args)
    results = {
        'num_file_scan': 0,
        'num_file_match': 0,
        'num_text_match': 0,
    }

    ignore_directories = []
    for kv in config.items(section='IgnoreDirectory'):
        ignore_directories += kv[1].split('|')
    re_flags = 0
    if args.ignorecase:
        re_flags = re.IGNORECASE

    # search
    for root, dirs, files in os.walk(args.path, topdown=True):
        # via docs: https://docs.python.org/3/library/os.html#os.walk
        # > When topdown is True, the caller can modify the dirnames list in-place (perhaps using del or slice assignment), and walk() will only recurse into the subdirectories whose names remain in dirnames; this can be used to prune the search, impose a specific order of visiting, or even to inform walk() about directories the caller creates or renames before it resumes walk() again.
        dirs[:] = [d for d in dirs if d not in ignore_directories]
        # print(root, dirs, files)
        for f in files:
            found = 0
            ignore = False
            #print (root, dirs, f)
            found = find_file(root, f, args.pattern, re_flags)
            if num := len(found):
                print (set_color('{} ({})'.format(Path(root, f), num), 100))
                for text in found:
                    print(text)
                results['num_file_match'] += 1
                results['num_text_match'] += num

    print('=== results ===')
    print(results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', help='pattern')
    parser.add_argument('--path', help='search path',
                        type=Path, default=Path.cwd())
    parser.add_argument('-i', '--ignorecase', help='ignore regex case',
                        action="store_true")

    config = configparser.ConfigParser()
    config.read('config.ini')
    main(parser.parse_args(), config)
