# Claude Hunter 🔍

A high-performance, multi-threaded Python tool that hunts for Claude AI contributions across GitHub repositories. Automatically detects and searches organizations, users, or GitHub URLs to find repositories where Claude has contributed code.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/sho-luv/claude_hunter.svg)](https://github.com/sho-luv/claude_hunter/stargazers)

## Features

⚡ **Multi-threaded scanning** - Uses 10 threads by default for blazing fast searches  
🔍 **Auto-detection** - Automatically determines if target is a user or organization  
🌐 **URL support** - Accepts GitHub URLs and extracts usernames/orgs automatically  
📊 **Detailed reporting** - Finds Claude contributions via commit signatures and contributor lists  
💾 **JSON export** - Saves comprehensive results with timestamps and contribution details  
🚀 **Simple interface** - Just specify a target, no complex flags needed

## Quick Start

### Installation

```bash
git clone https://github.com/sho-luv/claude_hunter.git
cd claude_hunter
python -m venv claude_hunter_env
source claude_hunter_env/bin/activate  # On Windows: claude_hunter_env\Scripts\activate
pip install requests
```

### Basic Usage

```bash
# Search any GitHub user or organization
python claude_hunter.py anthropics -k YOUR_GITHUB_TOKEN

# Works with URLs too
python claude_hunter.py https://github.com/sho-luv -k YOUR_TOKEN

# Limit results and customize threads
python claude_hunter.py anthropics -k YOUR_TOKEN -m 20 -t 15
```

## Command Line Options

```
usage: claude_hunter.py [-h] [--token TOKEN] [--output OUTPUT]
                        [--max-repos MAX_REPOS] [--verbose]
                        [--threads THREADS]
                        target

positional arguments:
  target                GitHub username, organization, or URL to search

optional arguments:
  -h, --help            show this help message and exit
  --token, -k TOKEN     GitHub personal access token
  --output, -o OUTPUT   Output JSON file (default: claude_repos.json)
  --max-repos, -m MAX_REPOS
                        Maximum repositories to check (default: 100)
  --verbose, -v         Enable verbose output
  --threads, -t THREADS Number of threads to use (default: 10)
```

## How It Works

Claude Hunter searches for repositories where Claude appears as:

- **Contributor** - Listed in GitHub's contributors API
- **Commit author/committer** - Commits signed with Claude's signature  
- **Commit messages** - References to Claude Code or Anthropic in commit messages

The tool automatically detects contribution patterns like:
- `🤖 Generated with [Claude Code](https://claude.ai/code)`
- `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commits from `claude[bot]` or Anthropic email addresses

## Example Output

```bash
$ python claude_hunter.py anthropics -k YOUR_TOKEN -m 5

Starting search for repositories with Claude as contributor...
Detecting if 'anthropics' is an organization or user...
✓ Detected 'anthropics' as ORGANIZATION
  - Name: Anthropic
  - Description: 
  - Public repos: 40
Searching organization: anthropics
Found 5 unique repositories to check
Using 10 threads for parallel processing...

🎉 Found 5 repositories with Claude as contributor:
  - anthropics/claude-code (17,686 stars) - https://github.com/anthropics/claude-code
    Method: commits
  - anthropics/anthropic-cookbook (17,665 stars) - https://github.com/anthropics/anthropic-cookbook
    Method: contributor
  - anthropics/courses (16,355 stars) - https://github.com/anthropics/courses
    Method: commits
  - anthropics/prompt-eng-interactive-tutorial (14,657 stars) - https://github.com/anthropics/prompt-eng-interactive-tutorial
    Method: commits
  - anthropics/dxt (791 stars) - https://github.com/anthropics/dxt
    Method: commits

⏱️ Search completed in 1.82 seconds
Results saved to claude_repos.json
```

## JSON Output Format

Results are saved in a structured JSON format:

```json
{
  "total_found": 5,
  "search_timestamp": "2025-07-06 17:03:24 UTC",
  "repositories": [
    {
      "name": "claude-code",
      "full_name": "anthropics/claude-code",
      "html_url": "https://github.com/anthropics/claude-code",
      "description": "Claude Code is an agentic coding tool...",
      "owner": "anthropics",
      "stars": 17686,
      "forks": 988,
      "language": "PowerShell",
      "claude_contributor": {
        "method": "commits",
        "commits": [
          {
            "sha": "0149827a77f6d56c7f4e41d5d1f2097d22d6b40c",
            "message": "🤖 Generated with [Claude Code](https://claude.ai/code)...",
            "author": {
              "name": "ant-kurt",
              "email": "kurt@anthropic.com",
              "date": "2025-07-03T01:09:19Z"
            }
          }
        ]
      }
    }
  ]
}
```

## GitHub Token Setup

For higher rate limits and access to private repositories, create a GitHub Personal Access Token:

1. Go to [GitHub Settings → Personal access tokens](https://github.com/settings/personal-access-tokens)
2. Generate a new token with `repo` scope
3. Use with `--token` or `-k` flag

Without a token, you're limited to 60 requests per hour. With a token, you get 5,000 requests per hour.

## Performance Tips

- **Use threading**: Default 10 threads work well, increase with `-t 15` for faster searches
- **Limit repositories**: Use `-m 50` to focus on top repositories
- **Use tokens**: Avoid rate limiting with GitHub tokens
- **Verbose mode**: Use `-v` to debug slow searches

## Use Cases

Perfect for:

- 🔬 **Researchers** studying AI-assisted development patterns
- 📊 **Developers** tracking Claude's contribution to open source
- 🏢 **Organizations** auditing AI tool usage in their repositories  
- 🤖 **AI enthusiasts** exploring the extent of AI-human collaboration
- 📈 **Data analysis** of AI adoption in software development

## Technical Details

- **Language**: Python 3.7+
- **Dependencies**: `requests` library
- **Threading**: Concurrent repository checking with configurable thread pool
- **Rate limiting**: Automatic delays and token support
- **Error handling**: Graceful handling of API errors and network issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for research and educational purposes. It searches public GitHub data through official APIs. Respect GitHub's terms of service and rate limits.

---

⭐ **Found this useful?** Star the repository to help others discover Claude Hunter!

🐛 **Found a bug?** Please open an issue with details about the problem.

💡 **Have an idea?** Contributions and feature requests are always welcome!