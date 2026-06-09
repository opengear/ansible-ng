# Contributing

Contributions are welcome! Please follow the guidelines below to help us maintain
a high quality, readable project history.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ~~~bash
   git clone https://github.com/<your-username>/ansible-collections.git opengear-ansible-collections
   cd opengear-ansible-collections
   ~~~
3. Add the upstream remote so you can keep your fork up to date:
   ~~~bash
   git remote add upstream https://github.com/opengear/ansible-collections.git
   ~~~
4. Create a development branch from `main`:
   ~~~bash
   git checkout -b feature/ng-add-ntp-module
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
feat(ng/ntp): add ntp module for device configuration

Implements get/set NTP server configuration via the REST API.
Supports multiple NTP servers and authentication.

---

test(ng/ntp): add unit tests for ntp module

Covers server list retrieval, single/multi-server set,
and error handling for unreachable NTP hosts.

---

docs(ng/ntp): add ntp module example playbook

Shows basic NTP configuration for a fleet of devices
using the new opengear.ng.ntp module.
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
