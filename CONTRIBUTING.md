# How to work with the employment repository

GIT and GITHUB workflow
=======================

**Section 1 (General Setup)**

After creating a fork from the original Github (employment) on your own Github account:

*Copy clone url from your fork on GitHub, open Terminal, go to your code folder and clone the GitHub repository into your local folder:*

```
git clone https://github.com/<user>/employment.git
```
*Go to cloned project folder (e.g. employment) and:*

```
git remote add upstream https://github.com/hodsonjames/employment.git
git remote -v
```
*Tell git to ignore files that your IDE or editor writes automatically to project folders:*

open .gitignore file and add the folder and file names that should get ignored, then save file. 


**Section 2 (Daily Routine)**

ALWAYS when you start to work:

*Make sure that you are in master branch and fetch upstream to get latest updates from hodsonjames/employment GitHub:*

```
git checkout master
git fetch upstream
```
*Check what has changed:*

```
git branch -va
```
*Merge updates from upstream master into local git (original, without branch):*

```
git checkout master
git merge upstream/master
```
*Push updates from master (not branch!!!) to your GitHub fork:*
*Make sure you are on the master:*

```
git checkout master
```
*Then push updates*

```
git push
```
*Check if now upstream master and local original git are the same*

```
git branch -va
```
*If you have a branch that you are working on and want to get the updates from master into your branch:*

```
git checkout <branch_name>
git rebase master
```

**Section 3 (Create new Branch for your work)**

How to create a new branch to do your work:

*Make sure you are on the master:*

```
git checkout master
```
*Create the new branch:*

```
git branch <branch_name>
```
*Now change view to <branch_name>:*

```
git checkout <branch_name>
```


**Section 4 (Work on your new branch)**

Work on your new branch: 

*Make sure you are in the correct branch:*

```
git checkout <branch_name>
```
*ALWAYS repeat steps from Section 2 first, to make sure that master is up to date!*

*Then rebase master, which updates the changes from original git to branch git, so you have everything up to date:*

```
git rebase master
```

**Section 5 (push your final work and send pull request)**

*Add the file or folder you have created or changed to git (this you can do on a regular basis):*

```
git add <my filename>
```
*Reset add if you have added something accidentally:*

```
git reset HEAD docs/.DS_Store
```

*Commit everything you have added. This makes a collection of changes that is ready to be pushed:*

```
git commit -m “my message”
```
*Then push to send to GitHub:*

```
git push --set-upstream origin <branch_name>
```

*Once you have everything in your GitHub fork that you want to give to review for merging with hodsonjames/employment GitHub, send pull request:*

Open your fork on GitHub, select the branch, and send a pull request

*After your pull request has been reviewed and merged, delete the branch on your local git:*

```
git checkout master
git branch -d <branch_name>
```
*Then delete the branch from the remote to avoid clutter:*

```
# Remove branch from remote
git push origin --delete <branch_name>

#In case any remote branches have been orphaned
git fetch --prune
```

*Then list all local branches to check:*

```
git branch -a
```

*Repeat **Section 2** to bring master up-to-date. *

