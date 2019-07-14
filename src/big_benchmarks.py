import os

from multiprocessing import Pool


jobs = []

for fn in os.listdir("CSV"):
    if fn.endswith(".csv"):
        inputFile = f"CSV/{fn}"
        for cc0 in ["","_cc0"]:
            outputFile = f"CSV/{fn[:-len('.csv')]}{cc0}.output"
            if not os.path.exists(outputFile):
                print(inputFile,outputFile)
                jobs.append((inputFile,outputFile))

def process_job(io):
    inputFile = io[0]
    outputFile = io[1]
    if "cc0" in outputFile:
        os.system(f"timeout 24h time python matrix.py --cc0 {inputFile} > {outputFile} 2>&1")
    else:
        os.system(f"timeout 24h time python matrix.py {inputFile} > {outputFile} 2>&1")


            
Pool(8).map(process_job, jobs)
