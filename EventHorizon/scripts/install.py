import commands
import os
from string import find
from optparse import OptionParser
import shutil
import sys
import urllib2
import datetime

###################
#Install functions#
###################

#Install Python
def install_python():
    print "Checking your python version..."
    version = commands.getoutput('python --version')
    if version.find('Python 2.6') == 0:
    	print "Your python version is OK"
    else:
	print "Your python version is %s and required version is 2.6.X" % version
	print "Updating python..."
        try:
	    os.system("sudo apt-get install python2.6 > /dev/null")
        except:
	    sys.exit("Failed to install Python. Try to install it manually and rerun the script.")
	print "Python 2.6 was installed"

#Install Postgres
def install_postgres():
    print "Checking your postgres version..."
    if commands.getoutput('sudo apt-show-versions | grep postgresql-8.3'):
        print "Your postgres version is OK"
    else:
        print "Your postgres version is not 8.3"
        print "Installing postgres... (This can take some time)"
        try:
       	    print "Installing postgresql(1/4)..."
    	    os.system("sudo apt-get -y install postgresql-8.3 > /dev/null") 
	    print "Installing postgresql-client(2/4)..."
	    os.system("sudo apt-get -y install postgresql-client-8.3 > /dev/null")
	    print "Installing postgresql-contrib(3/4)..."
	    os.system("sudo apt-get -y install postgresql-contrib-8.3 > /dev/null")
     	    print "Installing pgadmin3(4/4)..."
	    os.system("sudo apt-get -y install pgadmin3 > /dev/null")
	except:
            sys.exit("Failed to install Postgres. Try to install it manually and rerun the script.")
	print "Postgres was installed"
        print "Creating postgres user..."
	try:
	    os.system("echo \"ALTER USER postgres WITH PASSWORD 'qwerty123';\\q\" | sudo su postgres -c psql template1 > /dev/null")
            os.system("sudo passwd -d postgres > /dev/null")
            os.system("sudo echo \"qwerty123\nqwerty123\" | sudo su postgres -c passwd 2>1& /dev/null")
        except:
            sys.exit("Failed to create postgres user. Try to create it manually and rerun the script.")
	print "Postgres user created"

#Install Psycopg2
def install_psycopg2():
    print "Checking if you have psycopg2..."	
    if commands.getoutput("sudo apt-show-versions | grep psycopg2"):
        print "Psycopg2 is installed"
    else:
        print "Installing psycopg2..."
        try:
       	    os.system("sudo apt-get -y install python2.6-psycopg2 > /dev/null")
	except:
	    sys.exit("Failed to install psycopg2. Try to install it manually and rerun the script.")
	print "Psycopg2 was installed"

#Install Django
def install_django(dvd, output):
    print "Checking your django version..."
    if commands.getoutput('django-admin.py --version').startswith("1.1"):
        print "Your django version is OK"
    else:
	print "Installing django..."
    try:
        os.chdir("%s/linux" % dvd)
        shutil.copy("Django-1.1-beta-1.tar.gz", "%s/Django-1.1-beta-1.tar.gz" % output)
        os.chdir(output)
        if not os.path.exists("%s/Django-1.1-beta-1" % output):
            os.system("sudo tar -zxvf Django-1.1-beta-1.tar.gz > /dev/null")
        os.chdir("%s/Django-1.1-beta-1" % output)
        os.system("sudo python setup.py install > /dev/null")
        os.unlink("%s/Django-1.1-beta-1.tar.gz" % output)
    except:
        sys.exit("Failed to install django. Try to install it manually and rerun the script.")
	print "Django was installed"
	
#Install Apache2
def install_apache2():
    print "Checking if you have apache2..."
    if commands.getoutput("sudo apt-show-versions | grep apache2"):
	print "Apache2 is installed"
    else:
	print "Installing apache2..."
	try:
	    os.system("sudo apt-get -y install apache2 > /dev/null")
	except:
	    sys.exit("Failed to install apache2. Try to install it manually and rerun the script.")
	print "Apache2 was installed"

#Install mod_python
def install_mod_python():
    print "Checking if you have mod_python..."
    if commands.getoutput("sudo apt-show-versions | grep mod-python"):
        print "Mod_python is installed"
    else:
        print "Installing mod_python..."
        try:
            os.system("sudo apt-get -y install libapache2-mod-python > /dev/null")
        except:
            sys.exit("Failed to install mod_python. Try to install it manually and rerun the script.")
        print "Mod_python was installed"

#Install python_imaging
def install_python_imaging():
    print "Checking if you have python_imaging..."
    if commands.getoutput("sudo apt-show-versions | grep python-imaging"):
        print "Python_imaging is installed"
    else:
        print "Installing python_imaging..."
        try:
            os.system("sudo apt-get -y install python-imaging > /dev/null")
        except:
            sys.exit("Failed to install python_imaging. Try to install it manually and rerun the script.")
        print "Python_imaging was installed"

#Install python_twitter
def install_python_twitter():
    print "Checking if you have python_twitter..."
    if commands.getoutput("sudo apt-show-versions | grep python-twitter"):
        print "Python_twitter is installed"
    else:
        print "Installing python_twitter..."
        try:
            os.system("sudo apt-get -y install python-twitter > /dev/null")
        except:
            sys.exit("Failed to install python_twitter. Try to install it manually and rerun the script.")
        print "Python_twitter was installed"

#Edit settings.py
def edit_settings(output):
    try:
        file = open("%s/EventHorizon/settings.py" % output, "r")
        text = file.read()
   	file.close()
        text = text.replace("DEBUG = True", "DEBUG = False")
        text = text.replace("os.path.join(os.path.dirname(__file__), 'media')", "'/var/www/site_media'")
        text = text.replace("DATABASE_ENGINE = 'sqlite3'", "DATABASE_ENGINE = 'postgresql_psycopg2'")
        text = text.replace("'%s/db/EventHorizon.db' % base_dir", "'EventHorizon'")
        text = text.replace("DATABASE_USER = ''", "DATABASE_USER = 'postgres'")
        text = text.replace("DATABASE_PASSWORD = ''", "DATABASE_PASSWORD = 'qwerty123'")
        text = text.replace("DATABASE_HOST = ''", "DATABASE_HOST = 'localhost'")
        file = open("settings.py", "w")
        file.write(text)
        file.close()
    except:
        sys.exit("Failed to edit settings")
    print "settings.py is OK"
	
#Copying EventHorizon directory, media, admin media and configure settings
def copy_and_configure(options, dvd, output):
    print "Copying EventHorizon directory..."
    os.chdir(dvd)
    try:
        if not os.path.exists("%s/EventHorizon" % output):
            shutil.copytree("EventHorizon", "%s/EventHorizon" % output)
            os.chdir("%s/EventHorizon" % output)
            os.system("chmod -R 777 *")
            print "EventHorizon directory was copied"
        else:
	    print "You have EventHorizon directory in %s already" % output
    except:
        sys.exit("Failed to copy EventHorizon directory")
    edit_settings(output)
    try:
        if not os.path.exists("/var/www/media"):
    	    shutil.move("%s/EventHorizon/media" % output, "/var/www/media")
            os.rename("/var/www/media", "/var/www/site_media")
        else:
            print "You have media directory already" 
    except:
	sys.exit("Failed to move media directory")
    try:
        if not os.path.exists("/var/www/media"):
            shutil.copytree("%s/Django-1.1-beta-1/django/contrib/admin/media" % output, "/var/www/media")
        else:
            print "You have admin media directory already"
    except:
        sys.exit("Failed to copy admin media directory")
    print "Media directories are OK"

#Create database and load the data
def create_db(output):
    try:
        os.system("sudo su postgres -c \"createdb EventHorizon\" > /dev/null")
    	os.system("sudo python %s/EventHorizon/manage.py syncdb --noinput > /dev/null" % output) 
    except:	
        sys.exit("Failed to create the database and load the data.")
    print "DB was created and data was loaded"

#Configure ip and prefix
def configure_ip_and_prefix(options, output):
    try:
        if options.ip:
	    os.system("sudo python %s/mx30/scripts/mx_config.pyc -i %s --prefix=/peergw" % (output, options.ip.split(":")[0]))
        else:
	    os.system("sudo python %s/mx30/scripts/mx_config.pyc -i localhost --prefix=/peergw" % output)
    except:
	sys.exit("Failed to configure ip and prefix")
    print "IP and prefix were configured"

#Configure and restart apache
def configure_and_restart_apache(output):
    django_in_apache = commands.getoutput('sudo cat /etc/apache2/httpd.conf | grep "DJANGO_SETTINGS_MODULE"')
    if django_in_apache:
        print "Your apache is configured already"
    else:
        try:
	    shutil.copy("/etc/apache2/httpd.conf", "/etc/apache2/httpd_orig.conf")    
            file = open("%s/EventHorizon/scripts/apache_conf.txt" % output, 'r')
            text = file.read()
	    file.close()
            file = open("/etc/apache2/httpd.conf", 'w')
	    file.write(text.replace("<home dir>", "%s', '%s/EventHorizon" % (output, output)))
	    file.close()
	except:
	    sys.exit("Failed to configue apache")      
	try:
	    os.system('sudo /etc/init.d/apache2 restart')
	except:
	    sys.exit("Failed to restart apache")
 	print "Apache was configured and restarted"	   

#getting version number from mx30 directory
def get_version(dir, v):
    try:
        sys.path.append("%s/.." % dir)
        sys.path.append("%s/" % dir)
	sys.path.reverse()
	if v == "old":
	    os.environ['DJANGO_SETTINGS_MODULE'] = 'mx30_backup.settings'
            from mx30_backup.pmx.pmx import get_version
	else:
	    os.environ['DJANGO_SETTINGS_MODULE'] = 'mx30.settings'
            from mx30.pmx.pmx import get_version
    except:
        sys.exit("Could not get the mx30 version")
    return get_version()

#Run upgrades scripts
def run_upgrades_scripts(dir, old_version, new_version):
    scripts = os.listdir('%s/mx30/scripts/upgrade/db_upgrades' % dir)
    for script in os.listdir('%s/mx30/scripts/upgrade/backups_upgrades' % dir):
        scripts.append(script)
    for script in scripts:
        if not script.endswith("py") and not script.endswith("pyc"):
            for i in range(scripts.count(script)):
                scripts.remove(script)
    temp = []
    for script in scripts:
        temp.append(script)
    for script in temp:
        if (script.split("_")[0] < old_version) or (script.split("_")[2] > new_version):
            scripts.remove(script)
    #now the scripts list include only the scripts that should be run
    scripts.sort()
    for script in scripts:
        #if scripts.find('Python 2.5') == 0:
        print "Running script %s" % script
        if script.find("sql") != -1:
            os.system("python %s/mx30/scripts/upgrade/db_upgrades/%s" % (dir, script))
        else:
            for file in os.listdir('%s/mx30/backups' % dir):
                os.system("python %s/mx30/scripts/upgrade/backups_upgrades/%s %s/mx30/backups/%s" % (dir, script, dir, file))

#Copy the media
def copy_media(dir, media_dir):
    try:
	shutil.rmtree("%s/login" % media_dir)
	shutil.rmtree("%s/skins" % media_dir)
	shutil.rmtree("%s/stub" % media_dir)
	shutil.rmtree("%s/system" % media_dir)
        shutil.copytree("%s/mx30/media/login" % dir, "%s/login" % media_dir)
        shutil.copytree("%s/mx30/media/skins" % dir, "%s/skins" % media_dir)
        shutil.copytree("%s/mx30/media/stub" % dir, "%s/stub" % media_dir)
        shutil.copytree("%s/mx30/media/system" % dir, "%s/system" % media_dir)
        os.system("chmod -R 777 %s" % media_dir)
    except:
        sys.exit()

#update
def update(old, new, options):
    print "Starting update..."
    print "Backing up the data..."
    try:
        os.chdir('%s/mx30' % old)
        dt = datetime.datetime.now()
        exec_string = "python manage.pyc dumpdata --indent=4 --format=xml > backups/update_%s_%s_%s.aupaace.xml" % (dt.month, dt.day, dt.year)
        os.system(exec_string)
    except:
        sys.exit("Failed to backup the data.")
    print "Your data was backed up."
    print "Updating your version..."
    try:
        print "Copying the new version..."
        shutil.rmtree("%s/mx30_backup" % old)
        os.renames("%s/mx30" % old, "%s/mx30_backup" % old)
        shutil.copytree("%s/mx30" % new, "%s/mx30" % old)
        print "Configuring settings..."
        os.chdir("%s/mx30" % old)
        edit_settings(options, old)
        file = open ("%s/mx30_backup/settings.py" % old, "r")
        line = file.readline()
        while line and line.find('DATABASE_NAME') == -1:
            line = file.readline()
        db = line.split("'")[1]
        file.close()
        file = open ("%s/mx30_backup/settings.py" % old, "r")
        line = file.readline()
        while line and line.find('MEDIA_ROOT') == -1:
            line = file.readline()
        media_dir = line.split("'")[1]
        file.close()
        file = open ("%s/mx30/settings.py" % old, "r")
	text = file.read()
	file.close()
	file = open ("%s/mx30/settings.py" % old, "w")
        file.write(text.replace("DATABASE_NAME = 'peer_center'", "DATABASE_NAME = '%s'" % db))
        file.close()
	shutil.rmtree("%s/mx30/backups" % old)
        shutil.copytree("%s/mx30_backup/backups" % old, "%s/mx30/backups" % old)
        print "Copying media..."
        copy_media(old, media_dir)
    except:
        sys.exit("Failed to copy and configure mx30 directory")
    try:
        os.system("python %s/mx30/manage.pyc syncdb --noinput >> /dev/null" % old)
	old_version = get_version("%s/mx30_backup" % old, "old")
	new_version = get_version("%s/mx30" % old, "new")
        run_upgrades_scripts(old, old_version, new_version)
        os.system("sudo python %s/mx30/manage.pyc syncdb --noinput >> /dev/null" % old)
    except:
        sys.exit("Failed to upgrade your version")
    print "New version was copied and configured"
    print "Restoring your data..."
    backups = os.listdir('%s/mx30/backups' % old)
    temp = [b for b in os.listdir('%s/mx30/backups' % old) if b.startswith('update')]
    temp.sort()
    data = temp[-1]
    try:
        os.system("python %s/mx30/manage.pyc loaddata %s/mx30/backups/%s" % (old, old, data))
    except:
        sys.exit("Failed to restore your data your version. In any case, it's saved in %s/mx30/backups/%s" % (old, data))
    configure_ip_and_prefix(options, old)
    print "Restarting apache..."
    try:
        os.system('/etc/init.d/apache2 restart')
    except:
        sys.exit("Failed to restart apache")
    print "Apache was restarted"
    sys.exit("Your version was successfully updated.")

###############
#Main function#
###############
  
def main():
    
    ########################
    #Parsing script options#
    ########################

    parser = OptionParser()
    parser.usage = "install.py [options] -i <install dvd location> -o <desired install location>"
    parser.add_option("-i", "--input", dest="input", help="dvd location for the installation")
    parser.add_option("-o", "--output", dest="output", help="desired install directory location")
    #parser.add_option("-u", action="store_true", dest="update", help="update version")
    #parser.add_option("-l", action="store_true", dest="local", help="Local installation")
    #parser.add_option("-I", "--ip", dest="ip", help="your ip")
    (options, args) = parser.parse_args()

    if not os.getuid()==0:
        sys.exit("You must be root to run this script")
    if not options.input:
        sys.exit("You should provide install EventHorizon directory location. Use '-i' option.")
    if not options.output:
        sys.exit("You should provide the desired install location. Use '-o' option.")

    dvd = os.path.abspath(options.input.split("EventHorizon")[0])
    output = os.path.abspath(options.output.split("EventHorizon")[0]) 

    ##################
    #Update procedure#
    ##################

    #if options.update:
    #    update(output, dvd, options)

    ###################
    #Install procedure#
    ###################
    try:
        req = urllib2.Request('http://www.google.com')
        urllib2.urlopen(req)
    except:
        sys.exit("You must be connected to the internet to run this script")
    print "Updating apt-get... (This can take some time)"
    try:
        os.system("sudo apt-get update > /dev/null")
        os.system("sudo apt-get -y install apt-show-versions > /dev/null")
    except:
        sys.exit("You don't have apt-get")
    print "Finished updating apt-get"
    print "Copying files..."
    shutil.copytree(dvd, "%s/dvd" % output)
    dvd = os.path.abspath("%s/dvd" % output)
    os.system("chmod 777 -R %s" % dvd)
    print "Finished copying files"
    os.chdir(dvd)
    install_python() 
    install_postgres()
    install_psycopg2()
    install_django(dvd, output)
    install_apache2()
    install_mod_python()	
    install_python_imaging()
    install_python_twitter()
    copy_and_configure(options, dvd, output)
    create_db(output)
    #configure_ip_and_prefix(options, output)
    configure_and_restart_apache(output)
    print "Deleting temporary files..."
    shutil.rmtree(dvd)
    print "The installation was finished successfully."
	
if __name__ == "__main__":
    main()
