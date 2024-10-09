# Contributing Guide

Thank you for your interest in contributing to the Application Study Tool!
Please read this guide for general guidelines to follow, which borrows heavily
from those used by the Opentelemetry Collector.

## How to contribute

### Before you start

Comment on the issue that you want to work on so we can assign it to you and
clarify anything related to it.

If you would like to work on something that is not listed as an issue,
please create an issue and describe your proposal. It is best to do this
in advance so that maintainers can decide if the proposal is a good fit for
this repository. This will help avoid situations when you spend significant time
on something that maintainers may decide this repo is not the right place for.

Follow the instructions below to create your PR.

### Fork

In the interest of keeping this repository clean and manageable, you should
work from a fork. To create a fork, click the 'Fork' button at the top of the
repository, then clone the fork locally using `git clone
git@github.com:USERNAME/application-study-tool.git`.

You should also add this repository as an "upstream" repo to your local copy,
in order to keep it up to date. You can add this as a remote like so:

`git remote add upstream https://github.com/f5devcentral/application-study-tool.git`

Verify that the upstream exists:

`git remote -v`

To update your fork, fetch the upstream repo's branches and commits, then merge
your `development` with upstream's `development`:

```
git fetch upstream
git checkout development
git merge upstream/development
```

Remember to always work in a branch of your local copy, as you might otherwise
have to contend with conflicts in `development`.


## Required Tools

Working with the project sources requires the following tools:

1. [git](https://git-scm.com/)
4. [docker](https://www.docker.com/)

## Repository Setup

Fork the repo and checkout  by:

```
$ git clone git@github.com:f5devcentral/application-study-tool.git
```

Add your fork as an origin:

```shell
$ cd application-study-tool
$ git remote add fork git@github.com:YOUR_GITHUB_USERNAME/application-study-tool.git
```

## Creating a PR

Checkout a new branch, make modifications, build locally, and push the branch to your fork
to open a new PR:

```shell
$ git checkout development
$ git checkout -b feature
# edit
$ git commit
$ git push fork feature
```

### Commit Messages

Use descriptive commit messages. Here are [some recommendations](https://cbea.ms/git-commit/)
on how to write good commit messages.
When creating PRs GitHub will automatically copy commit messages into the PR description,
so it is a useful habit to write good commit messages before the PR is created.
Also, unless you actually want to tell a story with multiple commits make sure to squash
into a single commit before creating the PR.

When maintainers merge PRs with multiple commits, they will be squashed and GitHub will
concatenate all commit messages right before you hit the "Confirm squash and merge"
button. Maintainers must make sure to edit this concatenated message to make it right before merging.
In some cases, if the commit messages are lacking the easiest approach to have at
least something useful is copy/pasting the PR description into the commit message box
before merging (but see the above paragraph about writing good commit messages in the first place).
