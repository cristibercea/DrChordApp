import subprocess, sys, os

def main():
    print("Running all frontend tests using Behave + Playwright...")
    testing_dir = os.path.dirname(os.path.abspath(__file__)) # check if behave can be run from this path
    result = subprocess.run(["behave", "features/"], cwd=testing_dir) # run behave on the features folder
    sys.exit(result.returncode) # get behave command return status

if __name__ == "__main__": main()