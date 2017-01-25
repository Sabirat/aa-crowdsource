# aa-crowdsource
Crowdsourcing platform for global self-updating AA meeting list


## Set up
##### Python stuff
1. In order to run the server locally you will need to have [pip](https://pip.pypa.io/en/stable/installing/) installed.
2. Then you can run the `install.sh` script by typing `./install.sh`
  * you may need to use sudo or change the permissions of the script file
3.  You will also need PhantomJS to be installed and its executable will need to be in your `PATH`

##### MySQL (this will be changed soon)
You will also need MySQL installed and a server running. Soon we will just have the DB on a server and
update the calls to use that so that you do not need a local version running. But for now:
1. [Install MySQL](https://dev.mysql.com/downloads/installer/)
2. You may need to type `export PATH=$PATH:/usr/local/mysql/bin` in the shell so that you have the command `mysql` in your `PATH`
3. Enter the SQL shell `mysql` and create database `CREATE DATABASE aameetings;`
4. Change password for root to nothing `SET PASSWORD FOR root@'localhost' = PASSWORD('');`
5. type `quit` to go back to normal shell
6. From the repo's root directory, import the `.sql` file `mysql -u root -p database_name < file.sql`
7. Start the server locally [Mac/Linux](https://coolestguidesontheplanet.com/start-stop-mysql-from-the-command-line-terminal-osx-linux/) [Windows](https://dev.mysql.com/doc/refman/5.7/en/windows-start-command-line.html)

##### Running
* Just type `python run.py` in root directory of the repo
