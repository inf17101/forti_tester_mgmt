# Custom Ansible Module for Fortinet FortiTester

This self-programmed Ansible module provides users with an easy-to-use interface to automate test runs on the FortiTester. <br>
The script can address all FortiTester API endpoints that expect HTTP POST or HTTP GET requests from the client.<br>
For example, it is possible to start or stop tests, wait for results and then store the test result in an Ansible variable.<br>
All that is needed are basics about Ansible.

# Installation

This section describes how to install the custom module properly.<br>
There are several ways to get it work, I just show you one.<br><br>
Note: This module requires python3.<br>

1. Install Ansible latest version.
`sudo apt install ansible`
2. Create a custom folder anywhere.
`mkdir /home/user/custom_ansible_modules`
2. Clone the repo inside the created folder.
```
cd /home/user/custom_ansible_modules
git clone ...
```
3. Change the variable `library` inside `/etc/ansible.cfg` to point to your custom ansible modules folder. 
```
vi /etc/ansible.cfg
...
library     = /home/user/custom_ansible_modules
```
Save and close the file.

<br>
Ansible should now be able to find the `forti_tester_mgmt` module.

# How to use it?


The following steps give an overview of how to use this module.