# GitHub Workflow
In order to ensure that everyone can easily keep track of their own and others' contributions to this project, we would like everyone to do their work in branches of the main repo, and then create pull requests when the code is ready to be integrated into the main branch. Laura and Lana will review each pull request, so be sure to add them as reviewers. If you need a refresher on committing work to branches, the steps to do so are below.

Be sure to use `git clone <link_to_repo>` or `git pull` to retrieve or update your local copy of the main repo.
1. Check `git status` to see which branch you're currently working on.
2. Create a new branch with `git branch <name_of_branch>`. Be sure to have a concise and descriptive name for the branch.
3. Switch to the branch with `git checkout <name_of_branch>`.
4. Check `git status` to make sure you're working on the correct branch.
5. Code!
6. Check `git status` to see which files need to be staged for commit.
7. Stage your code for commit with `git add <files>`.
8. Commit your changes to your branch with `git commit -m "description of changes"`
9. Push your local changes to GitHub with `git push origin <name_of_branch>`.
10. [Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for your branch on the repo webpage. Add a description detailing your changes, and remember to add Laura and Lana as reviewers for the pull request.

**Note:** The first time you commit to the repo, it won't know who you are. Update your email address and username in your configuration with the following commands:

`git config --global user.email "your.email@example.com"`

`git config --global user.name "Your Name"`
