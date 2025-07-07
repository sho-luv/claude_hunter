#!/usr/bin/env python3
"""
GitHub Claude Contributor Finder

This script searches GitHub for repositories where Claude (Anthropic's AI assistant) 
appears as a contributor. Since there's no direct API to search by contributor,
this script uses multiple strategies to find repositories with Claude contributions.

Usage:
    python claude_hunter.py [--token YOUR_GITHUB_TOKEN] [--output results.json]
"""

import requests
import json
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Repository:
    name: str
    full_name: str
    html_url: str
    description: Optional[str]
    owner: str
    stars: int
    forks: int
    language: Optional[str]
    claude_contributor: Dict[str, any]


class GitHubClaudeContributorFinder:
    """Find repositories where Claude appears as a contributor."""
    
    def __init__(self, token: Optional[str] = None, verbose: bool = False, max_threads: int = 10):
        self.token = token
        self.verbose = verbose
        self.max_threads = max_threads
        self.session = requests.Session()
        self.progress_lock = threading.Lock()
        self.completed_count = 0
        
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Claude-Contributor-Finder/1.0"
        })
        
        # Common Claude-related usernames/names to search for
        self.claude_identifiers = [
            "claude",
            "anthropic",
            "Claude",
            "claude-ai",
            "claude-anthropic",
            "noreply@anthropic.com",
            "Claude <noreply@anthropic.com>",
            "claude[bot]",
            "claude-bot",
            "claude-anthropic-bot"
        ]
    
    def search_repositories_by_keywords(self, keywords: List[str], max_results: int = 100) -> List[Dict]:
        """Search for repositories using keywords that might indicate Claude involvement."""
        repositories = []
        
        for keyword in keywords:
            print(f"Searching for repositories with keyword: {keyword}")
            
            url = "https://api.github.com/search/repositories"
            params = {
                "q": keyword,
                "sort": "stars",
                "order": "desc",
                "per_page": min(max_results, 100)
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                repositories.extend(data.get("items", []))
                
                # Rate limiting
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error searching repositories with keyword '{keyword}': {e}")
                continue
        
        return repositories
    
    def get_organization_repositories(self, org_name: str, max_results: int = 100) -> List[Dict]:
        """Get all repositories for a specific organization."""
        repositories = []
        page = 1
        per_page = min(max_results, 100)
        
        while len(repositories) < max_results:
            print(f"Fetching {org_name} repositories (page {page})...")
            
            url = f"https://api.github.com/orgs/{org_name}/repos"
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                repositories.extend(data)
                
                if len(data) < per_page:
                    break
                
                page += 1
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories for organization '{org_name}': {e}")
                break
        
        return repositories[:max_results]
    
    def get_user_repositories(self, username: str, max_results: int = 100) -> List[Dict]:
        """Get all repositories for a specific user."""
        repositories = []
        page = 1
        per_page = min(max_results, 100)
        
        while len(repositories) < max_results:
            print(f"Fetching {username} repositories (page {page})...")
            
            url = f"https://api.github.com/users/{username}/repos"
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                repositories.extend(data)
                
                if len(data) < per_page:
                    break
                
                page += 1
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories for user '{username}': {e}")
                break
        
        return repositories[:max_results]
    
    def detect_target_type(self, target_name: str) -> Optional[str]:
        """Detect if target is an organization or user."""
        print(f"Detecting if '{target_name}' is an organization or user...")
        
        # First try as organization
        org_url = f"https://api.github.com/orgs/{target_name}"
        try:
            response = self.session.get(org_url)
            if response.status_code == 200:
                org_data = response.json()
                print(f"✓ Detected '{target_name}' as ORGANIZATION")
                print(f"  - Name: {org_data.get('name', 'N/A')}")
                print(f"  - Description: {org_data.get('description', 'N/A')}")
                print(f"  - Public repos: {org_data.get('public_repos', 'N/A')}")
                return "org"
        except requests.exceptions.RequestException:
            pass
        
        # Then try as user
        user_url = f"https://api.github.com/users/{target_name}"
        try:
            response = self.session.get(user_url)
            if response.status_code == 200:
                user_data = response.json()
                account_type = user_data.get('type', 'User')
                
                if account_type == 'Organization':
                    print(f"✓ Detected '{target_name}' as ORGANIZATION (via users endpoint)")
                    print(f"  - Name: {user_data.get('name', 'N/A')}")
                    print(f"  - Description: {user_data.get('bio', 'N/A')}")
                    print(f"  - Public repos: {user_data.get('public_repos', 'N/A')}")
                    return "org"
                else:
                    print(f"✓ Detected '{target_name}' as USER")
                    print(f"  - Name: {user_data.get('name', 'N/A')}")
                    print(f"  - Bio: {user_data.get('bio', 'N/A')}")
                    print(f"  - Public repos: {user_data.get('public_repos', 'N/A')}")
                    return "user"
        except requests.exceptions.RequestException:
            pass
        
        print(f"❌ Could not detect type for '{target_name}' - may not exist or be private")
        return None
    
    def get_repository_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Get contributors for a specific repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            contributors = response.json()
            return contributors
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting contributors for {owner}/{repo}: {e}")
            return []
    
    def check_commits_for_claude(self, owner: str, repo: str, max_commits: int = 100) -> List[Dict]:
        """Check recent commits for Claude-related author information."""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {"per_page": min(max_commits, 100)}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            commits = response.json()
            claude_commits = []
            
            if self.verbose:
                print(f"  Checking {len(commits)} commits for Claude signatures...")
            
            for commit in commits:
                author = commit.get("commit", {}).get("author", {})
                committer = commit.get("commit", {}).get("committer", {})
                message = commit.get("commit", {}).get("message", "")
                
                if self.verbose:
                    print(f"    Commit {commit['sha'][:8]}: author={author.get('name', 'N/A')} <{author.get('email', 'N/A')}>")
                
                # Check author and committer info
                for person_type, person in [("author", author), ("committer", committer)]:
                    name = person.get("name", "").lower()
                    email = person.get("email", "").lower()
                    
                    if self.verbose:
                        print(f"      {person_type}: '{name}' <{email}>")
                    
                    # Check if any Claude identifier matches
                    for identifier in self.claude_identifiers:
                        if identifier.lower() in name or identifier.lower() in email:
                            if self.verbose:
                                print(f"      ✓ Found Claude match: '{identifier}' in {person_type}")
                            claude_commits.append({
                                "sha": commit["sha"],
                                "message": message,
                                "author": author,
                                "committer": committer,
                                "date": commit["commit"]["author"]["date"]
                            })
                            break
                    else:
                        continue
                    break
                
                # Also check commit message for Claude signatures
                if "claude" in message.lower() or "anthropic" in message.lower():
                    if self.verbose:
                        print(f"      ✓ Found Claude reference in commit message")
                    if not any(c["sha"] == commit["sha"] for c in claude_commits):
                        claude_commits.append({
                            "sha": commit["sha"],
                            "message": message,
                            "author": author,
                            "committer": committer,
                            "date": commit["commit"]["author"]["date"]
                        })
            
            if self.verbose:
                print(f"  Found {len(claude_commits)} Claude-related commits")
            
            return claude_commits
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking commits for {owner}/{repo}: {e}")
            return []
    
    def find_claude_contributor(self, repo_data: Dict) -> Optional[Dict]:
        """Check if Claude is a contributor to a repository."""
        owner = repo_data["owner"]["login"]
        repo_name = repo_data["name"]
        
        # Thread-safe progress tracking
        with self.progress_lock:
            self.completed_count += 1
            progress_msg = f"[{self.completed_count}] Checking {owner}/{repo_name}..."
            print(progress_msg)
        
        # Strategy 1: Check contributors list
        contributors = self.get_repository_contributors(owner, repo_name)
        
        if self.verbose:
            with self.progress_lock:
                print(f"  Found {len(contributors)} contributors:")
                for contributor in contributors:
                    login = contributor.get("login", "N/A")
                    print(f"    - {login}")
        
        for contributor in contributors:
            login = contributor.get("login", "").lower()
            
            if self.verbose:
                with self.progress_lock:
                    print(f"  Checking contributor login: '{login}'")
            
            if any(identifier.lower() in login for identifier in self.claude_identifiers):
                if self.verbose:
                    with self.progress_lock:
                        print(f"  ✓ Found Claude contributor match: {login}")
                return {
                    "method": "contributor",
                    "contributor_data": contributor
                }
        
        # Strategy 2: Check recent commits for Claude signatures
        claude_commits = self.check_commits_for_claude(owner, repo_name)
        
        if claude_commits:
            if self.verbose:
                with self.progress_lock:
                    print(f"  ✓ Found {len(claude_commits)} Claude commits")
            return {
                "method": "commits",
                "commits": claude_commits[:5]  # Limit to first 5 matches
            }
        
        if self.verbose:
            with self.progress_lock:
                print(f"  ✗ No Claude contributions found")
        
        return None
    
    def check_repository_worker(self, repo_data: Dict) -> Optional[Repository]:
        """Worker function for multi-threaded repository checking."""
        claude_info = self.find_claude_contributor(repo_data)
        
        if claude_info:
            repository = Repository(
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                html_url=repo_data["html_url"],
                description=repo_data.get("description"),
                owner=repo_data["owner"]["login"],
                stars=repo_data["stargazers_count"],
                forks=repo_data["forks_count"],
                language=repo_data.get("language"),
                claude_contributor=claude_info
            )
            
            with self.progress_lock:
                print(f"✓ Found Claude contribution in {repository.full_name}")
            
            return repository
        
        return None
    
    def search_claude_repositories(self, max_repos: int = 500, target_org: str = None, target_user: str = None, target: str = None) -> List[Repository]:
        """Main method to search for repositories with Claude as contributor using multi-threading."""
        print("Starting search for repositories with Claude as contributor...")
        
        repo_candidates = []
        
        if target:
            # Auto-detect if target is organization or user
            target_type = self.detect_target_type(target)
            if target_type == "org":
                print(f"Searching organization: {target}")
                repo_candidates = self.get_organization_repositories(target, max_repos)
            elif target_type == "user":
                print(f"Searching user: {target}")
                repo_candidates = self.get_user_repositories(target, max_repos)
            else:
                print(f"Could not determine type for '{target}', falling back to keyword search...")
                # Fall back to keyword search with the target name
                repo_candidates = self.search_repositories_by_keywords([target], max_repos)
        elif target_org:
            # Search specific organization
            print(f"Searching organization: {target_org}")
            repo_candidates = self.get_organization_repositories(target_org, max_repos)
        elif target_user:
            # Search specific user
            print(f"Searching user: {target_user}")
            repo_candidates = self.get_user_repositories(target_user, max_repos)
        else:
            # General keyword search
            search_keywords = [
                "anthropic claude",
                "claude ai",
                "claude assistant",
                "claude code",
                "claude generated",
                "co-authored-by claude",
                "generated with claude"
            ]
            
            print("Searching for potential repositories...")
            repo_candidates = self.search_repositories_by_keywords(search_keywords, max_repos)
        
        # Remove duplicates
        unique_repos = {}
        for repo in repo_candidates:
            unique_repos[repo["full_name"]] = repo
        
        repos_to_check = list(unique_repos.values())[:max_repos]
        print(f"Found {len(repos_to_check)} unique repositories to check")
        print(f"Using {self.max_threads} threads for parallel processing...")
        
        # Reset progress counter
        self.completed_count = 0
        
        # Check repositories for Claude contributions using thread pool
        claude_repos = []
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all repository checking tasks
            future_to_repo = {
                executor.submit(self.check_repository_worker, repo_data): repo_data 
                for repo_data in repos_to_check
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_repo):
                repo_data = future_to_repo[future]
                try:
                    result = future.result()
                    if result:
                        claude_repos.append(result)
                except Exception as exc:
                    print(f"Repository {repo_data['full_name']} generated an exception: {exc}")
        
        return claude_repos
    
    def save_results(self, repositories: List[Repository], filename: str):
        """Save results to JSON file."""
        results = {
            "total_found": len(repositories),
            "search_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "repositories": [asdict(repo) for repo in repositories]
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description="Find GitHub repositories with Claude as contributor")
    parser.add_argument("target", help="GitHub username, organization, or URL to search")
    parser.add_argument("--token", "-k", help="GitHub personal access token")
    parser.add_argument("--output", "-o", default="claude_repos.json", help="Output JSON file")
    parser.add_argument("--max-repos", "-m", type=int, default=100, help="Maximum repositories to check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--threads", "-t", type=int, default=10, help="Number of threads to use (default: 10)")
    
    args = parser.parse_args()
    
    # Extract target from URL if provided
    target = args.target
    if target.startswith("https://github.com/"):
        # Extract username/org from GitHub URL
        parts = target.rstrip("/").split("/")
        if len(parts) >= 4:
            target = parts[3]  # github.com/username
            print(f"Extracted '{target}' from GitHub URL")
    
    if args.threads < 1 or args.threads > 20:
        print("Error: Thread count must be between 1 and 20.")
        return
    
    finder = GitHubClaudeContributorFinder(args.token, args.verbose, args.threads)
    
    try:
        start_time = time.time()
        repositories = finder.search_claude_repositories(args.max_repos, None, None, target)
        end_time = time.time()
        
        if repositories:
            print(f"\n🎉 Found {len(repositories)} repositories with Claude as contributor:")
            for repo in repositories:
                print(f"  - {repo.full_name} ({repo.stars} stars) - {repo.html_url}")
                print(f"    Method: {repo.claude_contributor['method']}")
        else:
            print("\n❌ No repositories found with Claude as contributor.")
        
        print(f"\n⏱️  Search completed in {end_time - start_time:.2f} seconds")
        finder.save_results(repositories, args.output)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during search: {e}")


if __name__ == "__main__":
    main()