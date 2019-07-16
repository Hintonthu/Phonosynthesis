import os

from multiprocessing import Pool, cpu_count


jobs = []
alternations = []

for fn in os.listdir("CSV"):
    if fn.endswith(".csv"):
        inputFile = f"CSV/{fn}"
        alternation = False
        with open(inputFile,"r") as handle:
            for ln in handle:
                alternation = alternation or ln.startswith(u"U,")
        if alternation:
            outputFile = f"CSV/{fn[:-len('.csv')]}.output"
            alternations.append(fn)
            os.system(f"time python alternation.py {inputFile} > {outputFile}  2>&1")
        else:
            for cc0 in ["","_cc0"]:
                outputFile = f"CSV/{fn[:-len('.csv')]}{cc0}.output"
                if not os.path.exists(outputFile):
                    print(inputFile,outputFile)
                    jobs.append((inputFile,outputFile))
print(f"I handled the following {len(alternations)} alternations: {alternations}")
def process_job(io):
    inputFile = io[0]
    outputFile = io[1]
    if "cc0" in outputFile:
        os.system(f"timeout 24h time python matrix.py --cc0 {inputFile} > {outputFile} 2>&1")
    else:
        os.system(f"timeout 24h time python matrix.py {inputFile} > {outputFile} 2>&1")


            
Pool(cpu_count()).map(process_job, jobs)
