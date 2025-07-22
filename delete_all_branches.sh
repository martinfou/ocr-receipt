#!/bin/bash

# Bash script to delete all local branches except main/master
# Usage: ./delete_all_branches.sh

echo -e "\033[33mThis will delete ALL local branches except main/master!\033[0m"
read -p "Are you sure you want to continue? (y/N): " confirmation

if [ "$confirmation" = "y" ] || [ "$confirmation" = "Y" ]; then
    # Switch to main branch first
    echo -e "\033[32mSwitching to main branch...\033[0m"
    git checkout main
    
    # Get all local branches except main/master
    branches=$(git branch | grep -v "main" | grep -v "master" | sed 's/^[ *]*//')
    
    if [ -z "$branches" ]; then
        echo -e "\033[33mNo branches to delete.\033[0m"
        exit 0
    fi
    
    echo -e "\033[33mBranches to be deleted:\033[0m"
    echo "$branches"
    echo ""
    
    read -p "Proceed with deletion? (y/N): " final_confirmation
    
    if [ "$final_confirmation" = "y" ] || [ "$final_confirmation" = "Y" ]; then
        # Delete each branch
        while IFS= read -r branch; do
            if [ -n "$branch" ]; then
                echo -e "\033[32mDeleting branch: $branch\033[0m"
                git branch -D "$branch"
            fi
        done <<< "$branches"
        
        echo -e "\033[32mAll branches deleted successfully!\033[0m"
    else
        echo -e "\033[33mBranch deletion cancelled.\033[0m"
    fi
else
    echo -e "\033[33mOperation cancelled.\033[0m"
fi 