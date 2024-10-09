# Copper Mountain Techonologies VNA

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

**Getting started**

After installation, the software can be opened by running the exectuable, e.g., `./CMT_RVNA_22.4.3_x86_64.AppImage`. Then enable the TCP protocol in System > Mis Settings > Network setup > Interface state: ON. Take note of the port; it's typically 5025. To do this from the command line---and optionally not opening the GUI---use `./CMT_RVNA_22.4.3_x86_64.AppImage EnableSocket:5025 InvisibleMode`.

**Resources**

Monsalve et al., 2016 on calibration: https://ui.adsabs.harvard.edu/abs/2016ITMTT..64.2631M/abstract

Calibration kit documentation: https://coppermountaintech.com/calibration-kits/s911t-calibration-kit/ \
CMT Software on Single Board Computers: https://coppermountaintech.com/usb-vnas-with-single-board-computers/ \
CMT Automation Guide: https://coppermountaintech.com/automation-guide-for-cmt-vnas/ \
CMT Programming Examples and Guide: https://coppermountaintech.com/automation/ \
CMT Documention: https://coppermountaintech.com/help-r/index.html \
CMT Repositories: https://github.com/orgs/Copper-Mountain-Technologies/repositories
