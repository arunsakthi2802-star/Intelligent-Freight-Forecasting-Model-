import os
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    print("Getting list of untracked files...")
    stdout, stderr, code = run_cmd("git ls-files --others --exclude-standard")
    
    if not stdout:
        print("No untracked files found.")
        return

    untracked_files = [f for f in stdout.split('\n') if f]
    
    large_files = []
    pushed_count = 0
    
    for file in untracked_files:
        if not os.path.exists(file):
            continue
            
        size_mb = os.path.getsize(file) / (1024 * 1024)
        
        if size_mb > 90:
            print(f"Skipping large file ({size_mb:.2f} MB): {file}")
            large_files.append(file)
            continue
            
        print(f"Adding and committing ({size_mb:.2f} MB): {file}")
        
        # Add file
        run_cmd(f'git add "{file}"')
        
        # Commit file
        commit_msg = f"add dataset file: {os.path.basename(file)}"
        out, err, c = run_cmd(f'git commit -m "{commit_msg}"')
        
        if c == 0:
            pushed_count += 1
            
    print(f"\nCommitting {pushed_count} files completed.")
    
    if large_files:
        print(f"\nFound {len(large_files)} files over 90MB. Adding them to .gitignore.")
        with open('.gitignore', 'a', encoding='utf-8') as f:
            f.write("\n# Large dataset files (>90MB) excluded automatically\n")
            for lf in large_files:
                f.write(f"{lf}\n")
        
        # commit the updated .gitignore
        run_cmd('git add .gitignore')
        run_cmd('git commit -m "chore: ignore large dataset files over 90MB"')
        
    print("\nPushing all commits to GitHub...")
    out, err, c = run_cmd("git push")
    if c == 0:
        print("Push successful!")
    else:
        print("Push failed!")
        print(err)

if __name__ == "__main__":
    main()
