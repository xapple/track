############
Installation
############

To install you the track package, you don't need any administrator privileges or special permissions, you can simply download it somewhere in your home (for instance in a directory for repositories) and tell python where it is::

    $ cd ~
    $ mkdir repos
    $ cd repos
    $ git clone https://github.com/xapple/track.git
    $ export PYTHONPATH="$HOME/repos/track/":$PYTHONPATH

That last line should go into to your `.bash_profile` file so that python always knows where to find the track package.