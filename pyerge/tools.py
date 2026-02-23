from argparse import ArgumentParser
from collections import deque
from datetime import datetime
from itertools import chain
from re import findall, match, search, sub

from pyerge import EMERGE_LOGFILE, TMERGE_LOGFILE, TMPLOGFILE
from pyerge.utils import run_cmd

UPDATES_MAPPING = {'upgrades': 'U', 'upgrade': 'U', 'new': 'N', 'in new slot': 'NS', 'in new slots': 'NS',
                   'reinstalls': 'R', 'reinstall': 'R', 'uninstalls': 'Un', 'uninstall': 'Un',
                   'downgrades': 'D', 'downgrade': 'D', 'blocks': 'B', 'block': 'B'}
STAGE_MAPPING = {'Compiling': 'Compiling', 'Cleaning': 'Cleaning', 'AUTOCLEAN': 'Autoclean',
                 'completed emerge': 'Completed', 'Finished': 'Finished', 'Sync completed': 'Synced',
                 'Starting rsync': 'Syncing', 'Unmerging': 'Unmerging', 'Merging': 'Merging', 'unmerge': 'Unmerge'}

def e_sync() -> str:
    """Fetch a date of last sync from logs."""
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            regex = search(r'(\d+)(:\s===\sSync completed)', line)
            if regex is not None:
                sync_time = regex.group(1)
                break
        else:
            return 'Unknown'
    sync_date = datetime.fromtimestamp(int(sync_time)).strftime('%a, %d-%m %H:%M')
    print(sync_date)
    return sync_date


def e_dl() -> str:
    """Fetch a size of archives to be downloaded for the next system update."""
    size = 'Calculating...'
    with open(file=TMERGE_LOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            regex = search(r'(Size of downloads:.)([0-9,]*\s[KMG]iB)', line)
            if regex is not None:
                size = regex.group(2)
                break
    print(size)
    return size


def e_curr() -> str:
    """Get a name of the current or last compiled package."""
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            regex = search(r'Compiling.*\((.*)::', line)
            if regex is not None:
                pack = regex.group(1)
                break
        else:
            pack = ''
    print(pack)
    return pack


def e_eut() -> str:
    """Get estimated update time."""
    with open(file=TMPLOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            regex = search(r'Estimated update time:\s+(.*)\.', line)
            if regex is not None:
                eut = regex.group(1).replace(',', '')
                eut = sub(' minutes| minute', 'min', eut)
                eut = sub(' hours| hour', 'h', eut)
                break
        else:
            eut = 'Unknown'
    print(eut)
    return eut


def e_eta() -> str:
    """Get an estimated time of compilation of a current package."""
    output, _ = run_cmd('genlop -cn')
    out = output.decode('utf-8')
    eta = ''
    if search(r'Error.*no working merge found', out):
        eta = 'Unknown'

    regex = search(r'ETA:\s(.*)\.', out)
    if regex is not None:
        eta = regex.group(1)
    print(eta)
    return eta


def e_sta() -> str:
    """Get a current stage of emerging package."""
    result = 'Unknown'
    stage_pattern = r'(Compiling|Cleaning|AUTOCLEAN|completed\semerge|Finished|Starting\srsync|Sync\scompleted|Unmerging|Merging|unmerge)'
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        recent_lines = deque(log_file, maxlen=16)
        emerge_log = ''.join(reversed(recent_lines))
    regex = search(stage_pattern, emerge_log)
    if regex is not None:
        result = STAGE_MAPPING[regex.group(1)]
    print(result)
    return result


def e_prog() -> float:
    """Get current progress of emerging packages."""
    result = 100.0
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        emerge_log = ''.join(list(log_file)[::-1][:51])
    regex = search(r'\(([0-9]*)\sof\s([0-9]*)\)', emerge_log)
    if regex is not None:
        result = round(100.0 * int(regex.group(1)) / int(regex.group(2)), 4)
        print(result)
    return result


def e_log() -> str:
    """Check the next update content."""
    with open(file=TMERGE_LOGFILE, encoding='utf-8') as log_file:
        content = log_file.read()
    return content


def e_upd() -> str:
    """Check the types and number of packages to update."""
    with open(file=TMERGE_LOGFILE, encoding='utf-8') as log_file:
        content = log_file.read()
    if search(r'Total: 0 packages, Size of downloads: 0 KiB', content):
        return 'None'

    result = 'Calculating...'
    regex_total = search(r'Total:\s\d*\spackages?\s\((.*)\),.*', content)
    if not regex_total:
        return result
    total_list = regex_total.group(1).split(',') if regex_total else []
    if total_list:
        regex_conflict = search(r'Conflict:\s(\d*\sblocks?)', content)
        conflict_list = regex_conflict.group(1).split(',') if regex_conflict else []
        list_str = [element.strip() for element in chain(total_list, conflict_list)]
        upd_dict = {}
        for element in list_str:
            key_match = match(r'\d*\s([A-Za-z ]*)', element)
            value_match = match(r'(\d*)\s\w*', element)
            if key_match and value_match:
                upd_dict[key_match.group(1)] = value_match.group(1)

        result = ', '.join([f'{v} {UPDATES_MAPPING[k]}' for k, v in upd_dict.items() if k in UPDATES_MAPPING])
    print(result)
    return result


def e_raid(raid_id: str) -> str:
    """
    Check of the Raid array.

    :param raid_id: Name i.e., md126 or md127
    :return: Status of RAID
    """
    raid = 'Unknown'
    out, _ = run_cmd('cat /proc/mdstat')
    regex = search(rf'{raid_id}.*\n.*(\[[U_]*])' , out.decode('utf-8'))
    if regex is not None:
        raid = regex.group(1)
    return raid


def run_e_raid():
    """Run e_raid from cli."""
    parser = ArgumentParser()
    parser.add_argument('-n', '--name', action='store', help='Provides name of MD RAID Array')
    print(e_raid(parser.parse_args().name))


def e_live(action: str) -> str:
    """Get the number and names of live ebuilds to build."""
    out, err = run_cmd('smart-live-rebuild --no-color --jobs=6 --pretend --quiet --unprivileged-user')
    live_no, live_tot = 0, 0
    live_names = 'None'
    regex = search(r'\*{3}\sFound\s(\d+).*out\sof\s(\d+)', err.decode('utf-8'))
    if regex is not None:
        live_no, live_tot = int(regex.group(1)), int(regex.group(2))
    if live_no:
        live_names = ','.join(findall(r'/(.*):0', out.decode('utf-8')))

    if action == 'all':
        result = f'{live_names} ({live_no} of {live_tot})'
    elif action == 'name':
        result = live_names
    else:
        result = f'{live_no} of {live_tot}'

    return result


def run_e_live():
    """Run e_live from cli."""
    parser = ArgumentParser()
    parser.add_argument('action', help='action: "all", "name" or "number" of live ebuilds')
    print(e_live(parser.parse_args().action))
