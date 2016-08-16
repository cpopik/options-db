from nasdaq import *
from multiprocessing import Process, JoinableQueue, cpu_count, current_process
import json
import time
import warnings

# suppress warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

# num worker queues
numWorkerQueues = cpu_count()

def worker():
    # task codes
    # 0: get last page and add URL to queue
    # 1: get dataset from queue and ?upload?

    while True:
        task = q.get()

        if task is None:
            break
        elif task[0] == 0:
            ticker = task[1]
            ticker, lastPage = getLastPage(ticker)  # should remove ticker in future versions
            # adds to global list all the necessary pages
            for page in range(1, lastPage+1):
                # add a task with type 1 to the queue
                url = 'http://www.nasdaq.com/symbol/' + ticker + '/option-chain?dateindex=-1&page='+str(page)
                q.put([1, ticker, url])
                print('Queued:\t\t', url, '\t', time.strftime('%H:%M:%S'), '\t', current_process().name)
        elif task[0] == 1:
            ticker = task[1]
            url = task[2]
            print('Starting:\t', url, '\t', time.strftime('%H:%M:%S'), '\t', current_process().name)

            df = downloadOptionsPage(ticker, url)
            print('Calculated:\t', url, '\t', time.strftime('%H:%M:%S'), '\t', current_process().name)

            status = uploadToSQL(ticker, df)
            print('Uploaded:\t', url, '\t', time.strftime('%H:%M:%S'), '\t', current_process().name, '\t', status)


        # tell the queue that the task is done
        q.task_done()

def main():
    openFile = open('tickerList.txt', 'r+')
    tickers = json.loads(openFile.read())
    openFile.close()

    # create global queue
    global q
    q = JoinableQueue()

    # starting up
    print("\nCurrent time: ", time.strftime('%y-%m-%d %H:%M:%S'))
    print("Initializing on ", cpu_count(), ' cores...')

    # create multiple processing threads
    activeProcesses = []
    for i in range(numWorkerQueues):
        process = Process(target = worker)
        # thread.daemon = True
        process.start()
        activeProcesses.append(process)

    # starting up
    print("Adding processes...\n")
    print('Action \t\t Page \t\t\t\t\t\t\t\t\t Timestamp \t Process ID \t Status')
    print('----------- \t -------------------------------------------------------------------- \t ---------- \t ----------- \t -----------')

    for ticker in tickers:
        q.put([0, ticker])

    # block until all tasks are done
    q.join()

    # stop workers
    for i in range(numWorkerQueues):
        q.put(None)
    for p in activeProcesses:
        p.join()

if __name__ == "__main__":
    main()
