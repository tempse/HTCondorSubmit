import os
import argparse
import subprocess

condorExecutable = """
#!/bin/bash
export SCRAM_ARCH={SCRAM_ARCH}
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd {FOLDER}
$@
"""

condorSubmit = """
universe               = vanilla
executable             = condorExecutable.sh
getenv                 = True
"""

condorSubmitAdd = """
output                 = logs/run{runNum}/{logname}_{index}.out
log                    = logs/run{runNum}/{logname}_{index}.log
error                  = logs/run{runNum}/{logname}_{index}.err
arguments              = {ARGS}
max_retries            = {maxretries}
should_transfer_files  = NO
+JobFlavour            = "{flavour}"
RequestCpus            = {num_cpus}
queue 1
"""

# get rid of empty lines in the condor scripts
# if condorExecutable starts with a blank line, it won't run at all!!
# the other blank lines are just for sanity, at this point
def stripEmptyLines(string):
    if string[0] == "\n":
        string = string[1:]
    return string


condorExecutable = stripEmptyLines(condorExecutable)
condorSubmit = stripEmptyLines(condorSubmit)
condorSubmitAdd = stripEmptyLines(condorSubmitAdd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE")
    parser.add_argument(
        "--flavour",
        "-f",
        dest="FLAVOR",
        type=str,
        default="longlunch",
        choices=[
            "espresso",
            "microcentury",
            "longlunch",
            "workday",
            "tomorrow",
            "testmatch",
            "nextweek",
        ],
    )
    parser.add_argument("--cpus", dest="CPUS", type=int, default=1)
    parser.add_argument("--max-retries", "-r", dest="MAXRETRIES", type=int, default=3)
    args = parser.parse_args()

    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    SCRAM_ARCH = os.environ["SCRAM_ARCH"]
    CMSSW_BASE = os.environ["CMSSW_BASE"]
    FOLDER = os.getcwd().replace(CMSSW_BASE, "").replace("/src/", "")
    executableName = "condorExecutable.sh"
    with open(executableName, "w") as f:
        f.write(condorExecutable.format(**locals()))

    # get the number of existing run* directories and make the next one
    try:
        numberOfExistingRuns = int(
            subprocess.check_output(
                "ls -d logs/run* 2>/dev/null | wc -l", shell=True
            ).strip("\n")
        )
    except subprocess.CalledProcessError:
        numberOfExistingRuns = 0

    runNum = numberOfExistingRuns + 1
    os.makedirs("logs/run{}".format(runNum))

    ArgsList = []
    with open(args.FILE, "r") as f:
        for line in f.readlines():
            ArgsList.append(line.strip("\n"))

    # make the submit file
    submitName = "condorSubmitFile"
    for index, ARGS in enumerate(ArgsList):
        condorSubmit += condorSubmitAdd.format(
            runNum=runNum,
            logname=os.path.splitext(args.FILE)[0],
            index=index,
            ARGS=ARGS,
            flavour=args.FLAVOR,
            num_cpus=args.CPUS,
            maxretries=args.MAXRETRIES,
        )

    with open(submitName, "w") as f:
        f.write(condorSubmit)

    os.system("chmod +x {}".format(executableName))
    os.system("condor_submit {}".format(submitName))
    os.system("cp {} {} logs/run{}".format(executableName, submitName, runNum))
    os.system("rm {}".format(submitName))
