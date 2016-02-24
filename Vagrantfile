
Vagrant.configure(2) do |config|
  config.vm.box = 'centos/7'
  config.vm.host_name = 'gitlab.example.com'
  config.vm.network "forwarded_port", guest: 443, host: 8443

  config.vm.define :gitlab do |v|
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
    ansible.sudo = true
  end

end
