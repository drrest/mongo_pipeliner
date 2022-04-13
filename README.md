MongoDB utility to make migrations and data processing.
Allow to create flexible configurable files to  processing mongo databases on everal environments.

MongoPipeLiner remember all completed steps of each configurable file (*.mrg) and skip completed steps to avoid repeat executing of them.
So .mgr files can be used as a migration pipeline and will stay on folder migrations/mongo_versions for apply it on next enviromnent.

All actions are eligible for MacOS

1) Install Homebrew

Open Terminal or your favorite OS X terminal emulator and run

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```
The script will explain what changes it will make and prompt you before the installation begins. 
Once you’ve installed Homebrew, insert the Homebrew directory at the top of your PATH environment 
variable. You can do this by adding the following line at the bottom of your ~/.profile file

```
export PATH="/usr/local/opt/python/libexec/bin:$PATH"
```
if MacOS 10.12 or older:
```
export PATH=/usr/local/bin:/usr/local/sbin:$PATH
```

2) Install Python3 (on MACOS)
```
brew install python
```

3) Install VirtualEnv
```
pip3 install virtualenv
```

4) Create VirtualEnv
```
virtualenv venv
```

5) Switch to newly created VirtualEnv

```
source venv/bin/active
```

6) Install requirements
```
pip3 install -r requirements.txt
```

7) Setup environment variables
```
set -a
. ./prepare_environment/work.env
set +a
```

8) RUN
```
python3 main.py
```

