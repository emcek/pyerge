## 0.8.0
* Refactor tools be more effective
* Supported Python version are: 3.10 - 3.14
* Internal:
  * add Dockerfile to test `pyerge` and tools in real environment
  * move to `src` layout and to `pyproject.toml`
  * update unit test to be more real life
  * Update CI process
  * Add `dependabot`

## 0.7.2
* run regular emerge command via pye

## 0.7.1.
* Show command output when do `smart-live-rebuild` (cli parameter `-e`)

## 0.7.0
* New CLI parameters:
  * *-i*, *--device* - Linux device to use as tmp, default tmpfs
  * *-e*, *--live_ebuild* - run smart-live-rebuild after world update
* internal code clean-up and refactoring

## 0.6.0
Add new tool:
* e_live - Get names and/or number of live packages to build (**new**)
  *  `all` - print all data - `openmw,freeorion (2 of 4)`
  * `name` print only names of packages - `openmw,freeorion`
  * `number` print only number of packages to build - `2 of 4`

## 0.5.5
* Brake lines in logs to be more readable
* Change `errors` to `sterr` in logs no to confiuse user

## 0.5.4.
* chnage date format od `e_sync`
* make implementation of `e_dl` simpler

## 0.5.4.
* chnage date format od `e_sync`
* make implementation of `e_dl` simpler

## 0.5.3
* fix detecting `--pretend` mode of emerge command

## 0.5.2
* remove passing *-p*, *--pretend* option
* remove passing *-q*, **--quiet* parameters to **emerge** action
* add *--with-bdeps=y* and *--keep-going=y* to **pye -w emerge** (emerge @world)
* add *--with-bdeps=y* to **check** action and **pye -w emerge** (emerge -pv @world)

## 0.5.1
* Only minor internal changes and repo clean-up.

## 0.5.0
* New CLI parameters:
  * _-d_, _--clean-print_ - Run deep clean with pretend after emerge and print info
  * _-c_, _--clean-run_ - Run deep clean after emerge and do the clean
* New states for `e_sta` command
* _-v_, _--verbose_ and _-q_, -_-quite_ work better now
* internal code clean-up

## 0.4.2
Two new commands:
* `e_sta` - Get current stage of emerging package
* `e_prog` - Get current progress of emerging packages

## 0.4.1
* Fix `e_upd` command for **in new slots**

## 0.4.0
All tools generated script using entry_points:
* pye - use to sync (**check**) portage and update (**emerge**)
* e_sync - Get date of last sync of portage
* e_dl - Get size of archives to be download for next system update
* e_curr - Get name of the current/last compiled package
* e_eut - Get estimated update time
* e_eta - Get estimated time of compilation of current package
* e_log - Get details of packages for next update (**new**)
* e_upd - Get list of update types (**new**)
* e_raid - Get status of RAID Array (**new**)
* glsa - use to **list** latest GLSA or **test** system

## 0.3.7
* add `pretend` and `quiet` options to starting script

## 0.3.6
* do not mount tmp file system when action is check
* add tools for:
  * Get name of the current/last compiled package (e_curr)
  * Get estimated update time (e_eut)
  * Get estimated time of compilation of current package (e_eta)

## 0.3.5
* when system affected, GLSAs are printer with commas in one line
* change verbose handling
* add log entry with version

## 0.3.3
* Fix condition for return code in internal commands

## 0.3.2
* Do not mount tmpfs when check is local

## 0.3.1
* Fix running GLSA actions

## 0.3.0
* First release, API is subject to change.
