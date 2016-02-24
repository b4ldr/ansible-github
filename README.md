# Vagrent project to install gitlab via ansible

To get this up and running you will need to 

 1. Install vagrant(https://www.vagrantup.com/downloads.html)
 2. Install Virtualbox(https://www.virtualbox.org/wiki/Downloads)
 3. Install ansible(http://docs.ansible.com/ansible/intro_installation.html)

Then run the following commands

```bash
git clone https://github.com/b4ldr/ansible-gitlab
cd ansible-gitlab
sudo ansible-galaxy install -r requirements.yml
vagrant up
```

Once vagrant has finished you should have a gitlab server that you can reach via https://127.0.0.1:8443(https://127.0.0.1:8443) with the following details

```
Username: root
Password: 5iveL!fe
```

