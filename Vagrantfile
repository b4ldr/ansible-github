Vagrant.configure(2) do |config|
  config.vm.box = 'centos/7'
  config.vm.host_name = 'github.example.com'
  config.vm.network "forwarded_port", guest: 443, host: 8443
  config.vm.provision "shell", inline: "yum -y update"
  config.vm.provision "shell", inline: "yum -y install epel-release"
  config.vm.provision "shell", inline: "yum -y install ansible"
  config.vm.provision "shell", inline: "curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | bash"
  config.vm.provision "shell", inline: "yum -y install gitlab-ce"


  #
  # Run Ansible from the Vagrant Host
  #
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbook.yml"
  end

end
