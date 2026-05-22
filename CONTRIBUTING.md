# Contributing

Contributions are welcome! Please follow the guidelines below to help us maintain
a high quality, readable project history.

## Maintainers
This project is currently maintained by:

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/avankatwyk">
        <img src="https://github.com/avankatwyk.png?size=80" width="80px;" alt="avankatwyk"/><br />
        <sub><b>avankatwyk</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/lachytech">
        <img src="https://github.com/lachytech.png?size=80" width="80px;" alt="lachytech"/><br />
        <sub><b>lachytech</b></sub>
      </a>
    </td>
  </tr>
</table>

## Getting Started

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

## Keeping Your Fork Updated

Before starting new work, sync your fork with upstream:

~~~bash
git fetch upstream
git rebase upstream/main
~~~

## Configuration

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

## Commit Quality

We value a clean, readable git history. Please structure your work as a series of
**logical, atomic commits**; each commit should do one thing and one thing only.
Avoid commits like "WIP", "fix", or "misc changes".

Each commit message should follow this structure:

~~~
<type>(<optional scope>): <short summary>

<body explaining why change is being made: limit 72 chars per line>
~~~

**Types:**
- `feat` — a new feature or module
- `fix` — a bug fix
- `docs` — documentation changes only
- `ci` — changes to CI workflows
- `test` — adding or updating tests
- `refactor` — code change that is neither a fix nor a feature
- `chore` — maintenance tasks (gitignore, dependencies, etc.)

**Example — a well-structured branch:**

~~~
feat(om_ntp): add ntp module for OM device configuration

Implements get/set NTP server configuration via the REST API.
Supports multiple NTP servers and authentication.

---

test(om_ntp): add unit tests for ntp module

Covers server list retrieval, single/multi-server set,
and error handling for unreachable NTP hosts.

---

docs(om_ntp): add ntp module example playbook

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

## Pull Requests

- Keep PRs focused; one feature or fix per PR
- Ensure CI passes before requesting review
- Reference any related issues in the PR description
