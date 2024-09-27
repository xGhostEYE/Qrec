import configparser
import json
from git import Repo
from pydriller import Repository

import os
import shutil

config = configparser.ConfigParser()
# Read the configuration file
config.read('../config.ini')

def Git_Train_RepoScrapper(repo_url):
    repo_url_split = repo_url.split('/')
    
    # Directory where you want to save the commit snapshots
    save_dir = '../train/'+repo_url_split[-1]+'_training'
    local_repo_path = '../'+repo_url_split[-1]+'_original'
    
    # Clone the repository if it's not already cloned
    if not os.path.exists(local_repo_path):
        print("Cloning repository...")
        Repo.clone_from(repo_url, local_repo_path)
    else:
        print("Repository already cloned.")

    # Initialize the repository object with GitPython
    repo = Repo(local_repo_path)
    repo.git.checkout('main')
    
    
    # Collect commits using PyDriller
    commits = list(Repository(local_repo_path).traverse_commits())

    # Calculate 90% of the commits
    num_commits = len(commits)
    cutoff = int(num_commits * 0.9)

    # Process each commit
    for index, commit in enumerate(commits[:cutoff]):
        if (not commit.merge):
            # Define the folder to save this commit's snapshot
            commit_folder = os.path.join(save_dir, f"commit_{index+1}_{commit.hash[:7]}")
            if not os.path.exists(commit_folder):
                os.makedirs(commit_folder)
            
            # Checkout the commit using GitPython
            repo.git.checkout(commit.hash)
            
            #Populate json dict file
            modified_file_dict = {}
            for modified_file in commit.modified_files:
                if modified_file.filename.endswith(".py"):
                    
                    if (modified_file.change_type.name == "MODIFY" or modified_file.change_type.name == "RENAME" or modified_file.change_type.name == "ADD"):
                        modified_line_dict = {}
                        for item in modified_file.diff_parsed["added"]:
                            line_no = item[0]
                            changed_code = item[1]
                            modified_line_dict[line_no] = changed_code

                        modified_file_path = os.path.join(commit_folder,modified_file.new_path)
                        modified_file_dict[modified_file_path] = modified_line_dict
            
            json_file_name = config.get("User", "json_file_name")
            json_file_path = commit_folder + "/" + json_file_name   
            file = open(json_file_path, "w+")   
            file.close()             
            with open(json_file_path, 'a', encoding='utf-8') as f:
                json.dump(modified_file_dict, f, ensure_ascii=False)
    

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
    
def Git_Test_RepoScrapper(repo_url):
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
    repo.git.checkout('main')

    # Collect commits using PyDriller
    commits = list(Repository(local_repo_path).traverse_commits())

    # Calculate the last 10% of commits, using [cutoff:] where cutoff = 90% of num commits
    num_commits = len(commits)
    cutoff = int(num_commits * 0.9)

    # Process each commit
    for index, commit in enumerate(commits[cutoff:]):
        if (not commit.merge):
            # Define the folder to save this commit's snapshot
            commit_folder = os.path.join(save_dir, f"commit_{index+1}_{commit.hash[:7]}")
            if not os.path.exists(commit_folder):
                os.makedirs(commit_folder)

            # Checkout the commit using GitPython
            repo.git.checkout(commit.hash)
            
            #Populate json dict file
            modified_file_dict = {}
            for modified_file in commit.modified_files:
                if modified_file.filename.endswith(".py"):
                
                    if (modified_file.change_type.name == "MODIFY" or modified_file.change_type.name == "RENAME" or modified_file.change_type.name == "ADD"):
                        modified_line_dict = {}
                        for item in modified_file.diff_parsed["added"]:
                            line_no = item[0]
                            changed_code = item[1]
                            modified_line_dict[line_no] = changed_code

                        modified_file_path = os.path.join(commit_folder,modified_file.new_path)
                        modified_file_dict[modified_file_path] = modified_line_dict            

            json_file_name = config.get("User", "json_file_name")
            json_file_path = commit_folder + "/" + json_file_name       
            file = open(json_file_path, "w+")
            file.close()             
            with open(json_file_path, 'a', encoding='utf-8') as f:
                json.dump(modified_file_dict, f, ensure_ascii=False)


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
