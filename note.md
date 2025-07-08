### New features
#### v1.1
-   Upgrade UI for ListOption, better looking (the old one is really shit)
-   Polling thread when waiting for button event, reduce CPU consumption. (In v1.0, waiting for button consump about 6% of total CPU)
### Development note
-   Functions for responding with button press (in all interface class) is vulnerable due to not handling race condition (pressing multiple key)