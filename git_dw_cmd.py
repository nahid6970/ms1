#!/usr/bin/env python3
"""
GitHub Folder Downloader - Interactive Version
Downloads a specific folder from a specific commit using sparse checkout
"""

import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

class GitHubFolderDownloader:
    def __init__(self):
        self.temp_dirs = []  # Keep track of temp directories for cleanup
    
    def parse_github_url(self, url):
        """Parse GitHub URL and extract components"""
        # Pattern: https://github.com/user/repo/tree/commit-hash/folder/path
        pattern = r'^https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)$'
        match = re.match(pattern, url)
        
        if not match:
            return None
        
        return {
            'user': match.group(1),
            'repo': match.group(2),
            'commit_hash': match.group(3),
            'folder_path': match.group(4),
            'repo_url': f"https://github.com/{match.group(1)}/{match.group(2)}.git"
        }
    
    def run_command(self, command, cwd=None):
        """Run a shell command and return success status"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def get_user_input(self):
        """Get GitHub URL and download directory from user"""
        print("🐙 GitHub Folder Downloader")
        print("=" * 40)
        print()
        
        # Get GitHub URL
        while True:
            print("📖 Expected format: https://github.com/user/repo/tree/commit-hash/folder/path")
            print("📖 Example: https://github.com/nahid6970/test/tree/640671009edfee1dd07c7412c6e125a5cafaed99/FolderSync")
            print()
            
            github_url = input("🔗 Enter GitHub URL: ").strip()
            
            if not github_url:
                print("❌ URL cannot be empty. Please try again.\n")
                continue
            
            # Validate URL format
            if self.parse_github_url(github_url):
                break
            else:
                print("❌ Invalid URL format. Please check and try again.\n")
        
        # Get download directory
        home_dir = os.path.expanduser("~")
        print(f"\n📁 Default download location: {home_dir}")
        
        while True:
            download_dir = input(f"📂 Download directory (press Enter for default): ").strip()
            
            if not download_dir:
                download_dir = home_dir
                break
            
            # Check if directory exists or can be created
            try:
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir, exist_ok=True)
                
                if os.path.isdir(download_dir):
                    break
                else:
                    print(f"❌ '{download_dir}' is not a valid directory. Please try again.")
            except Exception as e:
                print(f"❌ Cannot access directory '{download_dir}': {e}")
        
        return github_url, download_dir
    
    def download_folder(self, github_url, download_dir=None):
        """Main function to download folder from GitHub"""
        if download_dir is None:
            download_dir = os.path.expanduser("~")  # Default to home directory
        
        print("\n🔍 Parsing GitHub URL...")
        
        # Parse URL
        parsed = self.parse_github_url(github_url)
        if not parsed:
            print("❌ Error: Invalid GitHub URL format")
            print("📖 Expected format: https://github.com/user/repo/tree/commit-hash/folder/path")
            return False
        
        user = parsed['user']
        repo = parsed['repo']
        commit_hash = parsed['commit_hash']
        folder_path = parsed['folder_path']
        repo_url = parsed['repo_url']
        
        # Create temporary directory name in download directory
        temp_dir = os.path.join(download_dir, f"{repo}_{commit_hash[:8]}_temp")
        
        print(f"🔍 Parsed URL:")
        print(f"   👤 User: {user}")
        print(f"   📦 Repository: {repo}")
        print(f"   🔗 Commit: {commit_hash[:12]}...")
        print(f"   📁 Folder: {folder_path}")
        print(f"   📂 Download to: {download_dir}")
        print()
        
        # Check if temp directory exists
        if os.path.exists(temp_dir):
            print(f"⚠️  Temporary directory '{temp_dir}' already exists!")
            response = input("❓ Do you want to remove it and continue? (y/n): ")
            if response.lower() in ['y', 'yes']:
                shutil.rmtree(temp_dir)
            else:
                print("❌ Aborted.")
                return False
        
        self.temp_dirs.append(temp_dir)
        
        try:
            # Clone with sparse checkout
            print("⬇️  Cloning repository with sparse checkout...")
            success, output = self.run_command(
                f"git clone --filter=blob:none --sparse {repo_url} \"{temp_dir}\""
            )
            
            if not success:
                print(f"❌ Failed to clone repository: {output}")
                return False
            
            # Checkout specific commit
            print(f"🔄 Checking out commit: {commit_hash}")
            success, output = self.run_command(
                f"git checkout {commit_hash}",
                cwd=temp_dir
            )
            
            if not success:
                print(f"❌ Failed to checkout commit: {output}")
                return False
            
            # Set sparse checkout
            print(f"📁 Setting up sparse checkout for: {folder_path}")
            success, output = self.run_command(
                f"git sparse-checkout set {folder_path}",
                cwd=temp_dir
            )
            
            if not success:
                print(f"❌ Failed to set sparse checkout: {output}")
                return False
            
            # Check if folder exists
            folder_full_path = os.path.join(temp_dir, folder_path)
            if not os.path.exists(folder_full_path):
                print(f"❌ Folder '{folder_path}' not found at commit {commit_hash}")
                return False
            
            # Create final directory name
            folder_name = os.path.basename(folder_path)
            final_dir = os.path.join(download_dir, f"{folder_name}_{commit_hash[:8]}")
            
            # Remove final directory if it exists
            if os.path.exists(final_dir):
                print(f"⚠️  Target directory '{final_dir}' already exists!")
                response = input("❓ Do you want to overwrite it? (y/n): ")
                if response.lower() in ['y', 'yes']:
                    shutil.rmtree(final_dir)
                else:
                    print("❌ Aborted.")
                    return False
            
            # Copy folder to download directory
            shutil.copytree(folder_full_path, final_dir)
            
            print(f"✅ Success! Folder downloaded to: {final_dir}")
            print("📊 Contents:")
            
            # List contents
            try:
                total_files = 0
                total_size = 0
                for item in os.listdir(final_dir):
                    item_path = os.path.join(final_dir, item)
                    if os.path.isdir(item_path):
                        # Count files in subdirectory
                        subdir_files = sum(len(files) for _, _, files in os.walk(item_path))
                        print(f"   📁 {item}/ ({subdir_files} files)")
                        total_files += subdir_files
                    else:
                        size = os.path.getsize(item_path)
                        print(f"   📄 {item} ({size} bytes)")
                        total_files += 1
                        total_size += size
                
                print(f"\n📈 Summary: {total_files} files downloaded")
                if total_size > 0:
                    if total_size > 1024 * 1024:
                        print(f"💾 Total size: {total_size / (1024 * 1024):.2f} MB")
                    elif total_size > 1024:
                        print(f"💾 Total size: {total_size / 1024:.2f} KB")
                    else:
                        print(f"💾 Total size: {total_size} bytes")
                        
            except Exception as e:
                print(f"   Could not list contents: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        finally:
            # Cleanup
            self.cleanup()
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"⚠️  Could not remove temp directory {temp_dir}: {e}")
        self.temp_dirs.clear()

def main():
    """Main function"""
    downloader = GitHubFolderDownloader()
    
    # Check if URL is provided as command line argument
    if len(sys.argv) == 2:
        # Command line mode
        github_url = sys.argv[1]
        success = downloader.download_folder(github_url)
    else:
        # Interactive mode
        try:
            github_url, download_dir = downloader.get_user_input()
            success = downloader.download_folder(github_url, download_dir)
        except KeyboardInterrupt:
            print("\n\n❌ Download cancelled by user.")
            success = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Download completed successfully!")
    else:
        print("💔 Download failed.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()