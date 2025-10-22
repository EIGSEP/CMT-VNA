# Copper Mountain Techonologies VNA
We now have Raspberry Pi-compatible software (beta version) for the R60 VNA. For the instructions for x86-compatible software, see the README\_DEP.md.
**Requirements**
The Pi must be running Ubuntu Desktop 64-bit 24.4 (Noble). We are waiting on the beta headless version, which would allow us to use the Ubuntu Server. The library *libxcb-cursor0* must be installed separately. You should also install python3.12-venv, openssh-server, git, and any other libraries you want. 

You must have the instrument software downloaded from the Google Drive.

To check that no other libraries are needed, you can run:
```
ldd ./instrument_software/bin/cmtvna | grep "Not Found"
``` 
This will display all dependencies that are missing. 

**Installation**
1. Clone the CMT-VNA repo.
2. Create a virtual environment, and install the CMT-VNA repository in that environment.
3. Run the bash script that sets the USB rules (it lives in this repo):
```
chmod +x ./scripts/install_vna_rules.sh
sudo ./scripts/install_vna_rules.sh
``` 
4. Make the binary file executable and run it to open the GUI:
```
chmod +x path/to/cmtvna 
path/to/cmtvna --socket-server on --socket-port 5025
```
5. Locate the green dot at the bottom left of the GUI. If it says something like "(R60) \<serial number\>" then move on to step 6. If it says "SN0916" then go to settings in the bottom left corner, and there should be a VNA in the "detected" list of devices. Click Connect, and this preference should now be saved. 

6. The service file needed to run the GUI in the background is included in this repo at ./scripts/cmtvna.service. Copy the service file to /etc/systemd/system, and make sure that the path in the WorkingDirectory and ExecStart lines of the service file lead to the correct binary file within the repo (it's hardcoded). Then you can run:
```
sudo systemctl daemon-reload
sudo systemctl enable cmtvna.service
sudo systemctl start cmtvna.service
```

7. (Optional) To check the status of the service, you can run:
```systemctl status cmtvna.service```


**Some Notes**
If you are seeing all zeros when using the cmt\_vna package, it's possible that the software is connecting to the default SN0916 rather than detecting the R60 device. This could be an issue with your udev rules, or that you skipped step 5, or that step 5 went wrong in some other way.
 
**Resources**

Monsalve et al., 2016 on calibration: https://ui.adsabs.harvard.edu/abs/2016ITMTT..64.2631M/abstract

Calibration kit documentation: https://coppermountaintech.com/calibration-kits/s911t-calibration-kit/ \
CMT Software on Single Board Computers: https://coppermountaintech.com/usb-vnas-with-single-board-computers/ \
CMT Automation Guide: https://coppermountaintech.com/automation-guide-for-cmt-vnas/ \
CMT Programming Examples and Guide: https://coppermountaintech.com/automation/ \
CMT Documentation: https://coppermountaintech.com/help-r/index.html \
CMT Repositories: https://github.com/orgs/Copper-Mountain-Technologies/repositories
