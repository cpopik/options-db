# -*- coding: utf-8 -*-
"""
@author: Connor Popik
"""

from nasdaqOptions import *
from threading import Thread
from queue import Queue
import json

# num worker queues
numWorkerQueues = 10

def worker():
    # task codes
    # 0: get last page and add URL to queue
    # 1: get dataset from queue and ?upload?

    while True:
        task = q.get()

        # break when there are no more tasks
        if task is None:
            break
        elif task[0] == 0:
            ticker = task[1]
            ticker, lastPage = getLastPage(ticker)  # should remove ticker in future versions
            # adds to global list all the necessary pages
            for page in range(1, lastPage+1):
                # add a task with type 1 to the queue
                url = 'http://www.nasdaq.com/symbol/' + ticker + '/option-chain?money=all&dateindex=-1&page='+str(page)
                q.put([1, ticker, url])
                print('Added: ', url)
        elif task[0] == 1:
            ticker = task[1]
            url = task[2]
            downloadOptionsPage(ticker, url)
            print('Uploaded: ', url)

        # tell the queue that the task is done
        q.task_done()

def main():
    openFile = open('tickerList.txt', 'r+')
    tickers = json.loads(openFile.read())
    openFile.close()

    global q
    q = Queue()

    threads = []
    for i in range(numWorkerQueues):
        thread = threading.Thread(target = worker)
        # thread.daemon = True
        thread.start()
        threads.append(thread)

    for ticker in tickers:
        q.put([0, ticker])

    # block until all tasks are done
    q.join()
    # stop workers
    for i in range(numWorkerQueues):
        q.put(None)
    for t in threads:
        thread.join()

if __name__ == "__main__":
    main()
