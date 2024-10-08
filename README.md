# CMT-VNA

**Installation**

Install the software from https://coppermountaintech.com/download-free-vna-software/, using the R VNA software compatible with 1-port VNAs. On Linux: unzip the files, make the AppImage exectuable, and run it. See the provided documentation or the [FAQ](https://coppermountaintech.com/frequently-asked-questions/) in case of issues with the installation.

> [!NOTE]
> For newer version of Ubuntu (20+), there's a known issue where the package is incompatible with the fonts of the OS. The fix (from the FAQ) is:
> 
> Download the v12 font package (fontconfig-config_2.12.6-0ubuntu2_all.deb) from http://security.ubuntu.com/ubuntu/pool/main//f/fontconfig/
> Then install it by running:
> ```
> sudo dpkg –install ~/Downloads/fontconfig-config_2.12.6-0ubuntu2_all.deb
> cp -L -r /etc/fonts/conf.d /tmp/etc-fonts-conf.d
> sudo apt install –fix-broken
> sudo cp -L -r /tmp/etc-fonts-conf.d/* /etc/fonts/conf.d/
> ```
> Go to /etc/fonts/fonts.conf and delete the lines at the top of the file that start with tags "\<its:\>" or "\<description\>".
> 
> Add this line to your .bashrc:
> ```
> export TERM=xterm
> ```
