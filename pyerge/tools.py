from argparse import ArgumentParser
from datetime import datetime
from re import search, sub, match

from pyerge import EMERGE_LOGFILE, TMERGE_LOGFILE, TMPLOGFILE
from pyerge.utils import run_cmd


def e_sync() -> str:
    """Fetch date of last sync form logs."""
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            reqex = search(r'(\d+)(:\s===\sSync completed)', line)
            if reqex is not None:
                sync_time = reqex.group(1)
                break
        else:
            return 'Unknown'
    sync_date = datetime.fromtimestamp(int(sync_time)).strftime('%a, %d-%m %H:%M')
    print(sync_date)
    return sync_date


def e_dl() -> str:
    """Fetch size of archives to be downloaded for next system update."""
    size = 'Calculating...'
    with open(file=TMERGE_LOGFILE, mode='r', encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            reqex = search(r'(Size of downloads:.)([0-9,]*\s[KMG]iB)', line)
            if reqex is not None:
                size = reqex.group(2)
                break
    print(size)
    return size


def e_curr() -> str:
    """Get name of the current or last compiled package."""
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            reqex = search(r'Compiling.*\((.*)::', line)
            if reqex is not None:
                pack = reqex.group(1)
                break
        else:
            pack = ''
    print(pack)
    return pack


def e_eut() -> str:
    """Get estimated update time."""
    with open(file=TMPLOGFILE, encoding='utf-8') as log_file:
        for line in list(log_file)[::-1]:
            reqex = search(r'Estimated update time:\s+(.*)\.', line)
            if reqex is not None:
                eut = reqex.group(1).replace(',', '')
                eut = sub(' minutes| minute', 'min', eut)
                eut = sub(' hours| hour', 'h', eut)
                break
        else:
            eut = 'Unknown'
    print(eut)
    return eut


def e_eta() -> str:
    """Get estimated time of compilation of current package."""
    output, _ = run_cmd('genlop -cn')
    out = output.decode('utf-8')
    eta = ''
    if search(r'Error.*no working merge found', out):
        eta = 'Unknown'

    reqex = search(r'ETA:\s(.*)\.', out)
    if reqex is not None:
        eta = reqex.group(1)
    print(eta)
    return eta


def e_sta() -> str:
    """Get current stage of emerging package."""
    result = 'Unknown'
    map_dict = {'Compiling': 'Compiling', 'Cleaning': 'Cleaning', 'AUTOCLEAN': 'Autoclean', 'completed emerge': 'Completed', 'Finished': 'Finished',
                'Sync completed': 'Synced', 'Starting rsync': 'Syncing', 'Unmerging': 'Unmerging', 'Merging': 'Merging', 'unmerge': 'Unmerge'}
    with open(file=EMERGE_LOGFILE, encoding='utf-8') as log_file:
        emerge_log = ''.join(list(log_file)[::-1][:16])
    regex = search(r'(Compiling|Cleaning|AUTOCLEAN|completed\semerge|Finished|Starting\srsync|Sync\scompleted|Unmerging|Merging|unmerge)', emerge_log)
    if regex is not None:
        result = map_dict[regex.group(1)]
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
    """Check next update content."""
    with open(file=TMERGE_LOGFILE, encoding='utf-8') as log_file:
        content = log_file.read()
    return content


def e_upd() -> str:
    """Check types and number of packages to update."""
    result = 'Calculating...'
    map_dict = {'upgrades': 'U', 'upgrade': 'U', 'new': 'N', 'in new slot': 'NS', 'in new slots': 'NS', 'reinstalls': 'R',
                'reinstall': 'R', 'uninstalls': 'Un', 'uninstall': 'Un', 'downgrades': 'D', 'downgrade': 'D', 'blocks': 'B', 'block': 'B'}
    with open(file=TMERGE_LOGFILE, encoding='utf-8') as log_file:
        content = log_file.read()

    if search(r'Total: 0 packages, Size of downloads: 0 KiB', content):
        result = "None"
    regex_total = search(r'Total:\s\d*\spackages?\s\((.*)\),.*', content)
    regex_conflict = search(r'Conflict:\s(\d*\sblocks?)', content)
    total_list = regex_total.group(1).split(',') if regex_total else []
    conflict_list = regex_conflict.group(1).split(',') if regex_conflict else []
    if total_list:
        list_str = [element.strip() for element in [*total_list, *conflict_list]]
        upd_dict = {match(r'\d*\s([A-Za-z ]*)', element).group(1): match(r'(\d*)\s\w*', element).group(1) for element in list_str}  # type: ignore
        result = ', '.join([f'{v} {map_dict[k]}' for k, v in upd_dict.items() if k in map_dict])
    print(result)
    return result


def e_raid(raid_id: str) -> str:
    """
    Check of Raid array.

    :param raid_id: name i.e. md126 or md127
    :return: status of RAID
    """
    raid = 'Unknown'
    out, _ = run_cmd('cat /proc/mdstat')
    out = out.decode('utf-8')  # type: ignore
    reqex = search(rf'{raid_id}.*\n.*(\[[U_]*\])', out)  # type: ignore
    if reqex is not None:
        raid = reqex.group(1)  # type: ignore
    return raid


def run_e_raid():
    """Run e_raid from cli."""
    parser = ArgumentParser()
    parser.add_argument('-n', '--name', action='store', help='Provides name of MD RAID Array')
    args = parser.parse_args()
    print(e_raid(args.name))
