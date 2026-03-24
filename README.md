# Copper Mountain Techonologies VNA
We now have Raspberry Pi-compatible software (early release on CMT website) for the R60 VNA. For the instructions for x86-compatible software, see the README\_DEP.md.
**Requirements**
The Pi should be running a Debian Trixie OS, RPi has a port of it. We are waiting on the beta headless version, which would allow us to use the Ubuntu Server instead of a Desktop.

You must have the instrument software downloaded from the Google Drive.


**Installation**
1. Clone the CMT-VNA repo.
2. Create a virtual environment, and install the CMT-VNA repository in that environment.
3. Run the bash script that sets the USB rules (it lives in this repo):
```
chmod +x ./scripts/install_vna_rules.sh
sudo ./scripts/install_vna_rules.sh
``` 

To check that no other libraries are needed, you can run:
```
ldd ./instrument_software/bin/cmtvna | grep "Not Found"
``` 
This will display all dependencies that are missing.  

4. Make the binary file executable:
```
chmod +x path/to/cmtvna 
```
5. The service file needed to run the GUI in the background is included in this repo at ./scripts/cmtvna.service.  and make sure that the path in the WorkingDirectory and ExecStart lines of the service file lead to the correct binary file within the repo (it's hardcoded) and copy the service file to /etc/systemd/system. Then you can run:
```
sudo systemctl daemon-reload
sudo systemctl enable cmtvna.service
sudo systemctl start cmtvna.service
```
To check the status of the service, you can run:
```systemctl status cmtvna.service```


**Some Notes**
If you are seeing all zeros when using the cmt\_vna package, it's possible that the software is connecting to the default SN0916 rather than detecting the R60 device. This could be an issue with your udev rules.
 
**Resources**

Monsalve et al., 2016 on calibration: https://ui.adsabs.harvard.edu/abs/2016ITMTT..64.2631M/abstract

Calibration kit documentation: https://coppermountaintech.com/calibration-kits/s911t-calibration-kit/ \
CMT Software on Single Board Computers: https://coppermountaintech.com/usb-vnas-with-single-board-computers/ \
CMT Automation Guide: https://coppermountaintech.com/automation-guide-for-cmt-vnas/ \
CMT Programming Examples and Guide: https://coppermountaintech.com/automation/ \
CMT Documentation: https://coppermountaintech.com/help-r/index.html \
CMT Repositories: https://github.com/orgs/Copper-Mountain-Technologies/repositories
