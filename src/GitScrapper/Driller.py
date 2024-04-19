from git import Repo
from pydriller import Repository

import os
import shutil


def GitRepoScrapper(repo_url):
    repo_url_split = repo_url.split('/')
    
    # Directory where you want to save the commit snapshots
    save_dir = '../test/'+repo_url_split[-1]+'_training'
    local_repo_path = '../'+repo_url_split[-1]+'_original'
    
    # Clone the repository if it's not already cloned
    if not os.path.exists(local_repo_path):
        print("Cloning repository...")
        Repo.clone_from(repo_url, local_repo_path)
    else:
        print("Repository already cloned.")

    # Initialize the repository object with GitPython
    repo = Repo(local_repo_path)

    # Collect commits using PyDriller
    commits = list(Repository(local_repo_path).traverse_commits())

    # Calculate 90% of the commits
    num_commits = len(commits)
    cutoff = int(num_commits * 0.9)

    # Process each commit
    for index, commit in enumerate(commits[:cutoff]):
        # Define the folder to save this commit's snapshot
        commit_folder = os.path.join(save_dir, f"commit_{index+1}_{commit.hash[:7]}")
        if not os.path.exists(commit_folder):
            os.makedirs(commit_folder)

        # Checkout the commit using GitPython
        repo.git.checkout(commit.hash)

        # Copy all files to the folder
        for item in os.listdir(local_repo_path):
            item_path = os.path.join(local_repo_path, item)
            if os.path.isfile(item_path):
                shutil.copy(item_path, commit_folder)
            elif os.path.isdir(item_path) and item not in ['.git', '.gitignore']:
                shutil.copytree(item_path, os.path.join(commit_folder, item), symlinks=True)

        print(f"Saved commit {commit.hash} to {commit_folder}")

    # Checkout to the main branch again if needed
    repo.git.checkout('main')

    print(f"Saved 90% of commits: {cutoff} out of {num_commits} total commits.")