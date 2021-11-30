[![image](https://img.shields.io/badge/pypi-v0.5.1-blue.svg)](https://pypi.org/project/pyerge/)
[![Python CI](https://github.com/emcek/pyerge/actions/workflows/python-ci.yml/badge.svg?branch=master)](https://github.com/emcek/pyerge/actions/workflows/python-ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/emcek/pyerge/badge.svg?branch=master)](https://coveralls.io/github/emcek/pyerge?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a695786f861e4001b3fc3974f628e09f)](https://www.codacy.com/gh/emcek/pyerge/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emcek/pyerge&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/badge/Licence-MIT-blue.svg)](./LICENSE.md)
[![Downloads](https://img.shields.io/github/downloads/emcek/pyerge/total?label=Downloads)](https://github.com/emcek/pyerge/releases)  
[![image](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue.svg)](https://github.com/emcek/pyerge)
[![BCH compliance](https://bettercodehub.com/edge/badge/emcek/pyerge?branch=master)](https://bettercodehub.com/)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=emcek_pyerge&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=emcek_pyerge)

## pyerge
It is small python wrapper tool for emerge (Gentoo package manager - Portage). It can mount RAM disk of defined size and compile packages inside it. 
Pyerge provide various tools to check and show emerge/portage status for conky.

## Table of Contents
* [Name](#name)
* [Requirements](#requirements)
* [Installation](#installation)
* [Main usage](#main-usage)
* [Tools for Conky](#tools-for-conky)

## Name
It should be called **PYMERGE** for **PY**thon and e**MERGE**, but when I create repository I missspelled the name and I keep it like that.

## Requirements
* Python-3.6+
* app-portage/eix

## Installation
Copy ebuild form GitHub Reliease into your local repository (i.e. /usr/local/portage) and run:
```shell
sudo emerge dev-python/portage
```

## Main usage
Pyerge API/CLI parameter are not stable yes and are subject to change.
Main pyerge script is called `pye` and has two main actions: `check` and `emerge`

### pye check
```shell
sudo pye check
```
It basicly run:
* sync portage `eix-sync`
* `sudo emerge -pvNDu --color n @world` (and save output to log_file_1)
* Estypete time for runing ememrge @world `genlop -pn` (and save to log_file_2)

Some useful switches:
* -l, --local - run everthing without `eix-sync`
* -q, --quiet - no output from pyerge itself only form other tools like `eix`, or `emerge`
* -v, --verbose - be more verbose

### pye emerge
```shell
sudo pye -w emerge
```
It basicly run:
* check if emerge isn't runnig
* set envirinment variable PORTAGE_TMPDIR to /var/tmp/portage
* mount 4G RAM disk to /var/tmp/portage
* run `emerge -pvNDu @world`
* unmount RAM disk

Some useful switches:
* -d, --clean-print - after running `emerge -pvNDu @world` it will show output from deep clean - `emegre -pc`
* -c, --clean-run - after running `emerge -pvNDu @world` it will run deep clean - `emerge -c` (imply -d)

After `emerge` action you can pass any ememrge parameter, it will be passed directly into emerge. So, you can build:
```shell
sudo pye -s 1G emerge -a app-admin/conky
```
It will mount only 1G RAM disk and ask while comipling app-admin/conky package.
* -s, --size - size of RAM disk with postfix i.e. 1024K, 512M, 2G

## Tools for Conky
Those tools are crated especialy for Conky monitoring. i.e. part of my .conkyrc:
```
color0 5b6dad
color1 7f8ed3
TEXT
${color0}Sensors:
 ${color0}CPU1: ${color1}${hwmon 0 temp 2}°C ${color0}CPU2: ${color1}${hwmon 0 temp 3}°C
 ${color0}md126 (root): ${color1}${execi 60 e_raid -n md126}   ${color0}md127 (swap): ${color1}${execi 60 e_raid -n md127}
${color1}$hr
${color0}File Systems:
 ${color0}root ${color1}${fs_used /}/${fs_size /} ${color1}${fs_bar /}
 ${color0}boot ${color1}${fs_used /boot}/${fs_size /boot} ${color1}${fs_bar /boot}
 ${color0}portage ${color1}${fs_used /var/tmp/portage}/${fs_size /var/tmp/portage} ${color1}${fs_bar 6 /var/tmp/portage}
${color1}$hr
${color0}Portage:
 ${color0}Last Sync: ${color1}${execi 120 e_sync}
 ${color0}Progress:  ${color1}${execibar 30 e_prog}
 ${color0}Package:   ${color1}${execi 30 e_curr}
 ${color0}ETA:       ${color1}${execi 30 e_eta}
 ${color0}Status:    ${color1}${execi 30 e_sta}
 ${color0}Update:    ${color1}${execi 30 e_upd}
 ${color0}Download:  ${color1}${execi 30 e_dl}
 ${color0}EUT:       ${color1}${execi 30 e_eut}
${color1}$hr
${color0}Gentoo Linux Security Advisories:
${color1}${execi 5400 glsa list -e 25}
${color0}Affected GLSA:
${color1}${execi 5400 glsa test -e 40}
```

### e_sync
```shell
e_sync
```
Print date of last emerge syc `eix-sync`

### e_dl
```shell
e_dl
```
Run after `pye check` print size of downloads of @world
i.e output - 3,239,589 KiB

### e_curr
```shell
e_curr
```
Run during `sudo pye emereg` or `sudo emerge` - print current building (lastly builded) package

### e_eut
```shell
e_eut
```
Run after `pye check` - print estimated update time from `genlop -pn`
i.e. output - 2 days 10h 36min

### e_eta
```shell
e_eta
```
Run during `sudo pye emereg` or `sudo emerge` - print estimetet left time to end of compilation, based on `genlop`

### e_log
```shell
e_log
```
Run after `pye check` - print content of next @world update

### e_sta
```shell
e_sta
```
Status of emerge/portage. Possible values: Compiling, Cleaning, Autoclean, Completed, Finished, Synced, Syncing, Unmerging, Merging, Unmerge

### e_prog
```shell
e_prog
```
Run during `sudo pye emereg` or `sudo emerge` - print current progress of emerge as float
i.e. output - if emerge is buildeing (5 of 6) package it will return 83.3333
You can use it in conky as: ${execibar 30 e_prog}

### e_upd
```shell
e_upd
```
Run after `pye check` - print types of next @world update. Possible values: U, N, NS, R, Un, D, B
i.e. output - 19 U, 2 R, 1 Un, 2 D - it means 19 upgrades, 2 reinstals, 1 uninstall, 2 downgrades

### e_raid
```shell
e_raid <raid dev>
```
Print RAID status form /proc/mdstat
i.e. output for e_raid md126 - [UUU]

### glsa
```shell
glsa -e 5 list 
```
List laste 5 GLSA enrties
output:
202107-55: SDL 2: Multiple vulnerabilities
202107-54: libyang: Multiple vulnerabilities
202107-53: Leptonica: Multiple vulnerabilities
202107-52: Apache Velocity: Multiple vulnerabilities
202107-51: IcedTeaWeb: Multiple vulnerabilities

```shell
glsa -e 40 test 
```
Check system against lats 40 GLSA.
output:
System is not affected by any of listed GLSAs
or list of IDs:
202107-53,202107-52
