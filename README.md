# Opengear Ansible Collections

The Opengear Ansible Collections includes a variety of Ansible content to help
automate the management of Opengear network appliances.

## Collections
At this time there is one collection available for use.

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| opengear.om | Manage the Opengear OM and CM8xxx family of devices.        |

### Supported connections
The Ansible collections support ``httpapi``  connections.

### HTTPAPI plugins
| Name           | Description                                                 |
| -------------- | ----------------------------------------------------------- |
| opengear.om.om | Use Opengear REST API to run request on Opengear OM device. |

### Modules
| Name                         | Description                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------- |
| opengear.om.om_auth          | Configure remote authentication, authorization, accounting (AAA) servers.                     |
| opengear.om.om_conns         | Read and manipulate the network connections on the Operations Manager appliance.              |
| opengear.om.om_facts         | Collect facts from OM devices.                                                                |
| opengear.om.om_failover      | Failover endpoint is to check failover status and retrieve / change failover settings.        |
| opengear.om.om_groups        | Retrieve or update group information.                                                         |
| opengear.om.om_pdu           | Configure, monitor and control PDUs connected to the device.                                  |
| opengear.om.om_physifs       | Read and manipulate the network physical interfaces on the Operations Manager appliance.      |
| opengear.om.om_ports         | Configuring and viewing ports information.                                                    |
| opengear.om.om_services      | Used for working with the properties of the various services running on the system.           |
| opengear.om.om_static_routes | Configuring and viewing static routes.                                                        |
| opengear.om.om_system        | Used for configuring and accessing information about the Operations Manager appliance itself. |
| opengear.om.om_users         | Retrieve and update user information.                                                         |

## Installing The Collections

### Release 

You can install the latest release of an Opengear Ansible Collection with the
Ansible Galaxy CLI:
```
ansible-galaxy collection install opengear.om
```
You can also include it in a `requirements.yml` file and install it with
`ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: opengear.om
```

### GitHub
To install directly from GitHub:
```
ansible-galaxy collection install git+https://github.com/opengear/opengear.om.git
```

### Local Repository

To install all collections from this repository:
```
git clone https://github.com/opengear/opengear-ansible-collections.git
cd opengear-ansible-collections
ansible-galaxy collection install opengear/om --force
```

### Development
To install colletions locally for active development, symlink the local source
to Ansible collections:
```
git clone https://github.com/opengear/opengear-ansible-collections.git
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
as `opengear.om.om_users`.

The following example task replaces configuration changes in the existing
configuration on a Opengear OM network device, using the FQCN:

```yaml
---
  - name: Replace device configuration of users.
    openear.om.om_users:
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

Contributions are welcome! Please follow the guidelines below to help us maintain
a high quality, readable project history.

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ~~~bash
   git clone https://github.com/<your-username>/opengear-ansible-collections.git
   cd opengear-ansible-collections
   ~~~
3. Add the upstream remote so you can keep your fork up to date:
   ~~~bash
   git remote add upstream https://github.com/opengear/opengear-ansible-collections.git
   ~~~
4. Create a development branch from `main`:
   ~~~bash
   git checkout -b feature/om-add-ntp-module
   ~~~

### Keeping Your Fork Updated

Before starting new work, sync your fork with upstream:

~~~bash
git fetch upstream
git rebase upstream/main
~~~

### Configuration

No `ansible.cfg` is provided. A typical development setup for working with
this repo locally:
```
[defaults]
collections_path = /path/to/opengear-ansible-collections:~/.ansible/collections
host_key_checking = False
stdout_callback = yaml

[inventory]
enable_plugins = yaml, ini
```

### Commit Quality

We value a clean, readable git history. Please structure your work as a series of
**logical, atomic commits**; each commit should do one thing and one thing only.
Avoid commits like "WIP", "fix", or "misc changes".

Each commit message should follow this structure:

~~~
<type>: <short summary>

<body explaining why change is being made: limit 72 chars per line>
~~~

**Types:**
- `feat` — a new feature or module
- `fix` — a bug fix
- `docs` — documentation changes only
- `test` — adding or updating tests
- `refactor` — code change that is neither a fix nor a feature
- `chore` — maintenance tasks (CI, dependencies, etc.)

**Example — a well-structured branch:**

~~~
feat: add ntp module for OM device configuration

Implements get/set NTP server configuration via the REST API.
Supports multiple NTP servers and authentication.

---

test: add unit tests for ntp module

Covers server list retrieval, single/multi-server set,
and error handling for unreachable NTP hosts.

---

docs: add ntp module example playbook

Shows basic NTP configuration for a fleet of OM devices
using the new opengear.om.ntp module.
~~~

Before opening a pull request, review your branch with:

~~~bash
git log main..HEAD --oneline
~~~

If you have messy intermediate commits, clean them up with an interactive rebase
before pushing:

~~~bash
git rebase -i main
~~~

### Pull Requests

- Keep PRs focused; one feature or fix per PR
- Ensure CI passes before requesting review
- Reference any related issues in the PR description

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
