# HTCondorSubmit

Submit any command (or a list of commands) to CERN's HTCondor infrastructure.

# Setup

Clone this repository into your favorite CMSSW release and compile.
```
cmsrel <your-favorite-CMSSW-release>
cd <your-favorite-CMSSW-release>/src/
git clone https://github.com/tempse/HTCondorSubmit.git
scram b -j 8
```

# Usage

## Send a single command to Condor
The following example submits the Python script `hello.py` (which takes, say, a string as argument) to the Condor "espresso" queue with a specified number of max. job retries:
```
python scripts/condorSubmit.py "python hello.py 'world'" --flavour espresso --max-retries 1
```

## Bulk submit multiple commands to Condor

1.  Prepare a simple text file that contains all commands (one per line).

    Example file `myjobs.txt`:
    ```
    python hello.py world
    python hello.py everybody
    ```

2.  Use the script `condorSubmitFromFile.py` to submit everything at once:
    ```
    python scripts/condorSubmitFromFile.py myjobs.txt --flavour espresso --max-retries 1
    ```
