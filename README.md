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
...
```
Save and close the file.

<br>
Ansible should now be able to find the `forti_tester_mgmt` module.

# How to use it?

The following steps give an overview of how to use this module.<br>
I prefer to use roles instead of simple playbooks.<br>
However you can use a different way, like just executing a simple playbook if you want.<br><br>

NOTE: This module is tested with FortiTester OS Version 3.9.1 and above.<br><br>


1.Create a folder `ansible_fortitester_tests`.
```
mkdir /home/user/ansible_fortitester_tests
cd /home/user/ansible_fortitester_tests
```
2. Create the following subfolders.
```
mkdir roles
mkdir roles/Test_IPS
mkdir roles/Test_IPS/tasks
mkdir roles/Test_IPS/vars
```
3. Create the following files inside the subfolders.
```
touch roles/Test_IPS/tasks/main.yml
touch mkdir roles/Test_IPS/vars/main.yml
```
4. Insert the following inside the `roles/Test_IPS/vars/main.yml` file and change the variables according to your setup.
```
vi roles/Test_IPS/vars/main.yml
host_ip: <host_ip>
host_port: '<port>'
password: <password>
username: <username>
```
Make sure this user has access to FortiTesters API.

5. Paste the following example inside `roles/Test_IPS/tasks/main.yml`, which tests the IPS of a predefined DUT with FortiTester in NAT Mode.
Please replace the `<test_name>` inside the example below with your predefined test on your FortiTester appliance.<br>
The test should exist and already setup with an appropriate network.<br>
In this example the DUT is a Next Generation Firewall between the FortiTester.<br>
The NAT mode of FortiTester is used to simulate clients, which try to attack the simulated servers of the FortiTester through the Firewall.<br>
The test is already defined on the FortiTester and linked with the network.<br>
```
---
- name: Test IPS, log in to fortitester
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      login:
        user: "{{username}}"
        password: "{{password}}"
  register: result

- debug:
    msg: "{{result.session}}"

- name: Test IPS, get TestID of IPS-Test
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      request:
        method: get
        api_command_collection:
          command: /api/case/getByName
          payload:
            testName: <test_name>
          session: "{{result.session}}"
  register: response

- debug:
    msg: "{{response.response.Data._id}}"

- name: Test IPS, start IPS-Test by ID
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      request:
        method: get
        api_command_collection:
          command: /api/case/{{response.response.Data._id}}/start
          session: "{{result.session}}"
  register: response

- debug:
    msg: "{{response.response}}"


- name: Test IPS, get status of IPS-Test
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      request:
        method: get
        api_command_collection:
          command: /api/running/getStatus
          session: "{{result.session}}"
  register: response
  delay: 5
  retries: 30
  until: response.response.Data.TestStatus == 'Stopped'

- debug:
    msg: "{{response.response}}"

- name: Test IPS, get history list of IPS-Test
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      request:
        method: get
        api_command_collection:
          command: /api/history/getList
          payload:
            TestResult: all
            Category: all
            offset: 0
            size: 1
            TestName: <test_name>
            StartTime: "{{response.response.Data.StartTime}}"
            EndTime: lookup('pipe','date "+%Y-%m-%d %H:%M" $1')
          session: "{{result.session}}"
  register: response

- debug:
    msg: "{{response.response}}"

- name: Test IPS, get history profile of IPS-Test
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      request:
        method: get
        api_command_collection:
          command: /api/intrusionReport/{{response.response.payload[0]._id}}/getProfile
          session: "{{result.session}}"
  register: response

- debug:
    msg: "{{response.response.Data.Title.Summary.localhost.port1.AttackReplay}}"

- name: Test IPS, logout
  connection: local
  delegate_to: 127.0.0.1
  custom_fortitester_mgmt:
    fortitester_ip: "{{host_ip}}"
    fortitester_port: "{{host_port}}"
    fortitester_command:
      logout:
        session: "{{result.session}}"
  register: result

- debug:
    msg: "{{result.response}}"

- debug:
    msg: "The return value of Test_IPS test was: {{response.response.Data.Title.Summary.localhost.port1.AttackReplay.PeerReceived}}"
```

Feel free to modify it and use different url paths of FortiTester documentation.<br>

6. Create a file called `site.yml` inside `/home/user/ansible_fortitester_tests` and add the role.
```
- hosts: localhost
  gather_facts: false
  ignore_errors: true
  roles:
  - Test_IPS
```

<br><br>NOTE: The ansible module calls the API of FortiTester from localhost, so no remote ansible host must be setup in the inventory file of ansible.<br>
7. Start the playbook.
```
ansible-playbook site.yml
```

You must see output on the console if you have setup everything properly.
Make sure your host has connection to FortiTester and your user has proper permissions to execute FortiTester commands via API calls.