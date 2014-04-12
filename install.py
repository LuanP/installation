import apt
import sys
import urllib

from apt import debfile
from subprocess import Popen


class Install(object):
    cache = apt.cache.Cache()

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __call__(self):

        # update and upgrade the system
        self.cache.update()
        self.cache.open()
        self.cache.upgrade(dist_upgrade=True)
        self.cache.commit()

        self.install_essentials()

        # if sys.argv > 1:
        #     install_others()

    @classmethod
    def run(cls, cmd):
        process = Popen(cmd, shell=True, executable='/bin/bash')
        process.wait()

    @classmethod
    def pip(cls, pkg):
        run('sudo pip -U {}'.format(pkg))

    def get_package(self, pkg):
        if pkg in self.cache:
            return self.cache[pkg]
        return None

    def install_essentials(self):
        # install working tools
        # python-pip (remember of updating it with pip, and install distribute)
        # (remember of installing fabric too)
        # git, vim and export editor variable to use vim as default
        # chrome, terminator, firefox nightly, virtualbox and vagrant

        # get packages to be installed
        python_pip = self.get_package('python-pip')
        git = self.get_package('git')
        vim = self.get_package('vim')
        sublime = self.get_package('sublime')
        chrome = self.get_package('google-chrome-stable')
        terminator = self.get_package('terminator')

        # mark each package for installation
        python_pip.mark_install()
        git.mark_install()
        vim.mark_install()
        sublime.mark_install()
        chrome.mark_install()
        terminator.mark_install()

        # install packages
        self.cache.commit()

        # install pip packages, firstly update pip
        pip('pip')
        pip('distribute')
        pip('fabric')

        # install deb files
        self.install_debfiles()

        # install firefox nightly
        install_firefox_nightly()

        # configure git, vim and sublime
        self.config_git()
        self.config_vim()
        self.config_sublime()


    def install_debfiles(self):
        vbox_url = 'http://download.virtualbox.org/virtualbox/4.3.10/virtualbox-4.3_4.3.10-93012~Ubuntu~raring_amd64.deb'
        vagrant_url = 'https://dl.bintray.com/mitchellh/vagrant/vagrant_1.5.2_x86_64.deb'

        debfiles = {
            'vbox': vbox_url,
            'vagrant': vagrant_url,
        }

        # download and install deb packages
        for filename, url in debfiles.items():
            filename_ = '/tmp/{}.deb'.format(filename)
            try:
                urllib.urlretrieve(url, filename_)
            except IOError:
                print "Download of {} failed".format(filename)
                print "url used: {}".format(url)
                raise

            deb = debfile.DebPackage(filename_)
            if deb.check():
                deb.install()

        self.cache.update()
        self.cache.open()
        self.cache.commit()

    def install_firefox_nightly(self):
        url = 'http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/firefox-31.0a1.en-US.linux-x86_64.tar.bz2'
        # download firefox nightly
        try:
            urllib.urlretrieve(url, '/tmp/firefox.tar.bz2')
        except IOError:
                print "Download of firefox failed"
                print "url used: {}".format(url)
                raise

        # install firefox nightly
        run('tar xfj /tmp/firefox.tar.bz2')

        # move firefox to your home folder
        run('mv /tmp/firefox ~')

    def config_git(self):
        ps1 = """PS1='\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w $(__git_ps1 "\[\033[31m\](%s)")\[\033[00m\]\$ '"""

        run('git config --global user.name {}'.format(self.name))
        run('git config --global user.email {}'.format(self.email))
        run('git config --global color.ui true')
        run('git config --global push.default simple')
        run('git config --global core.editor vi')
        run('GIT_PS1_SHOWDIRTYSTATE=true >> ~/.bashrc')
        run('{} >> ~/.bashrc'.format(ps1))

    def config_vim(self):
        # the idea is to clone the repository below and run install.sh

        # run('cd ~/Downloads')
        # repo_name = 'vim-config'
        # vim_config_url = 'git@github.com:seocam/{}.git.format(repo_name)'
        # run('git clone {}'.format(vim_config_url))
        # run('cd {}'.format(repo_name))
        # run('./install.sh')
        # go back home
        # run('cd ~')

        run('export EDITOR="vim" >> /etc/profile')

    def config_sublime():
        run('export VISUAL="sublime" >> /etc/profile')


if __name__ == "__main__":
    # get arguments, excluding the file
    args = sys.argv[1:]

    # verify if args passed were just name and email
    if len(args) == 2:
        name = args[0]
        email = args[1]
    elif len(args) == 4:
        kwargs = dict(args[0]=args[1], args[2]=args[3])
        name = kwargs.get('--name')
        email = kwargs.get('--email')

    Install(name, email)
