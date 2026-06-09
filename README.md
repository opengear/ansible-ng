# Opengear Ansible Collections

The Opengear Ansible Collections includes a variety of Ansible content to help
automate the management of Opengear network appliances.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/opengear/opengear.om/.github%2Fworkflows%2Fmain.yml?branch=develop%2Fproject-cleanup)

## Collections

| Name        | Description                                                        |
| ----------- | ------------------------------------------------------------------ |
| opengear.ng | Manage Opengear console servers and out-of-band management devices |

### Supported connections
The Ansible collections support ``httpapi``  connections.

### HTTPAPI plugins
| Name           | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| opengear.ng.http_api | Use Opengear REST API to run request on Opengear devices. |

### Modules
| Name                      | Description                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| opengear.ng.auth          | Configure remote authentication, authorization, accounting (AAA) servers.                     |
| opengear.ng.conns         | Read and manipulate the network connections on the Operations Manager appliance.              |
| opengear.ng.facts         | Collect facts from OM devices.                                                                |
| opengear.ng.failover      | Failover endpoint is to check failover status and retrieve / change failover settings.        |
| opengear.ng.groups        | Retrieve or update group information.                                                         |
| opengear.ng.pdu           | Configure, monitor and control PDUs connected to the device.                                  |
| opengear.ng.physifs       | Read and manipulate the network physical interfaces on the Operations Manager appliance.      |
| opengear.ng.ports         | Configuring and viewing ports information.                                                    |
| opengear.ng.services      | Used for working with the properties of the various services running on the system.           |
| opengear.ng.static_routes | Configuring and viewing static routes.                                                        |
| opengear.ng.system        | Used for configuring and accessing information about the Operations Manager appliance itself. |
| opengear.ng.users         | Retrieve and update user information.                                                         |

## Installing The Collections

### Release 

You can install the latest release of an Opengear Ansible Collection with the
Ansible Galaxy CLI:
```
ansible-galaxy collection install opengear.ng
```
You can also include it in a `requirements.yml` file and install it with
`ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: opengear.ng
```

### GitHub
To install directly from GitHub:
```
ansible-galaxy collection install git+https://github.com/opengear/ansible-collections.git
```

### Local Repository

To install all collections from this repository:
```
git clone https://github.com/opengear/ansible-collections.git opengear-ansible-collections
cd opengear-ansible-collections
ansible-galaxy collection install opengear/ng --force
```

### Development
To install colletions locally for active development, symlink the local source
to Ansible collections:
```
git clone https://github.com/opengear/ansible-collections.git opengear-ansible-collections
cd opengear-ansible-collections

mkdir -p ~/.ansible/collections/ansible_collections/
ln -s /path/to/opengear-ansible-collections/opengear \
      ~/.ansible/collections/ansible_collections/opengear
```
Development changes will be picked up automatically.

## Using Opengear Ansible Collections

These collections include [network resource modules](https://docs.ansible.com/ansible/latest/network/user_guide/network_resource_modules.html).

### Using modules from the Opengear Ansible Collections in your playbooks

You can call modules by their Fully Qualified Collection Namespace (FQCN) such
as `opengear.ng.users`.

The following example task replaces configuration changes in the existing
configuration on a Opengear network device, using the FQCN:

```yaml
---
  - name: Replace device configuration of users.
    openear.ng.users:
      config:
        - name: user1
          enabled: true
          no_password: true
          groups:
          - group2
      state: replaced

```

### See Also:

* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md)
before submitting a pull request.

### Code of Conduct
This collection follows the Ansible project's [Code of Conduct][].
Please read and familiarize yourself with this document.

[Code of Conduct]: https://docs.ansible.com/ansible/devel/community/code_of_conduct.html

## More information

- [Ansible network resources](https://docs.ansible.com/ansible/latest/network/getting_started/network_resources.html)
- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
- [Opengear OM REST API](https://ftp.opengear.com/download/api/operations_manager/og-rest-api-specification-v2-ngcs.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
