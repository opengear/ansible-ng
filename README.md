# Opengear Ansible Collections

The Opengear Ansible Collections includes a variety of Ansible content to help
automate the management of Opengear network appliances.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/opengear/opengear.om/.github%2Fworkflows%2Fmain.yml?branch=develop%2Fproject-cleanup)

## Collections

| Name        | Description                                                        |
| ----------- | ------------------------------------------------------------------ |
| opengear.ng | Manage Opengear console servers and out-of-band management devices |

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

### Local Repository

To install any collection from this repository:
```
git clone https://github.com/opengear/ansible-collections.git opengear-ansible-collections
cd opengear-ansible-collections
ansible-galaxy collection install opengear/<collection> --force
```

### Development
To install collections locally for active development, symlink the local source
to Ansible collections:
```
git clone https://github.com/opengear/ansible-collections.git opengear-ansible-collections
cd opengear-ansible-collections

mkdir -p ~/.ansible/collections/ansible_collections/
ln -s /path/to/opengear-ansible-collections/opengear \
      ~/.ansible/collections/ansible_collections/opengear
```
Development changes will be picked up automatically.

## Usage

For usage instructions, see the README of the desired collection:

- [opengear.ng](opengear/ng/README.md)

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
- [Opengear OM REST API](https://ftp.opengear.com/download/opengear_appliances/OM/OM2200/current/documentation/og-rest-api-specification-v2-ngcs.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
