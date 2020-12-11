# Application Installation in Ubuntu 18.04

## Step 1: Create a virtual env

`sudo apt-get update`

`sudo apt-get install python3-venv`

`python3 -m venv encoded-venv`

`source encoded-venv/bin/activate`

## Step 2: install dependencies:

Some tools may not be preinstalled in Unbuntu.

`sudo apt install awscli  unattended-upgrades apache2 apache2-dev apache2-utils ssl-cert   libapache2-mod-wsgi-py3 libjpeg8-dev zlib1g-dev libpq-dev apt-transport-https daemontools  build-essential libbz2-dev libdb-dev libffi-dev libgdbm-dev liblzma-dev libncurses5-dev libnss3-dev  libreadline-dev libssl-dev libsqlite3-dev python3-dev zlib1g-dev redis-server lzop nginx libarchive-tools bsdtar python3-setuptools -y`


## Step 3: clone git

`sudo apt-get install git`.

`git clone https://github.com/utsw-bicf/pandiseased`.

Go to your project folder and checkout the branch you want if not master branch.

## Step 4: run shell script

Find user name using `whoami`

Find home directory using `echo "$HOME"`

Change the user name and home directory to yours in the shell script install-devservers.sh

`sh install-devservers.sh`

`source ~/.bashrc`

## Step 5: build application

`make clean && buildout bootstrap && bin/buildout`

## Step 6: run application
- **Terminal window 1**:  
  In one terminal window startup the database servers and nginx proxy with:

  - `bin/dev-servers development.ini --app-name app --clear --init --load`

  This will first clear any existing data in `/tmp/encoded`.
  Then postgres and elasticsearch servers will be initiated within `/tmp/encoded`.
  An nginx proxy running on port 8000 will be started.
  The servers are started, and finally the test set will be loaded.

- **Terminal window 2**:  
  In a second terminal, make sure you are in the encoded-venv, run the app with:

  - `bin/pserve development.ini`

## Step 7: Browse to the interface at http://localhost:6543










