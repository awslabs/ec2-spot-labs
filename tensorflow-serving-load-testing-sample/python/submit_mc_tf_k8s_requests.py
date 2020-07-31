#!/usr/bin/env python3

from multiprocessing import Pool
import requests
import time
import json
import argparse
from functools import reduce
from tqdm import tqdm
import sys
import base64

url = ""
IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'
dl_request = requests.get(IMAGE_URL, stream=True)
dl_request.raise_for_status()
# Compose a JSON Predict request (send JPEG image in base64).
jpeg_bytes = base64.b64encode(dl_request.content).decode('utf-8')
predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes

def getUrl(url):
    try:
        response = requests.post(url, data=predict_request)
        response.raise_for_status()
        return response
    except Exception as e:
        return None
    
def runParallelRequests(processes=10, queued_requests_per_process=10,url=""):
    the_url = url 
    queue_of_urls = [ the_url for x in range(processes * queued_requests_per_process) ]
    print("Total processes: {}\nNumber of Requests: {}\ncontent of queue_of_urls: {}".format(
        processes,
        len(queue_of_urls), 
        queue_of_urls[0]))
    pool = Pool(processes)
    try:
        sucess=0
        fail=0
        total_time = 0
        for res in tqdm(pool.imap_unordered(getUrl, queue_of_urls), total=len(queue_of_urls)):
            if res is not None and res.status_code == 200:
                total_time += res.elapsed.total_seconds()
                prediction = res.json()['predictions'][0]['classes']
                sucess+=1
            else:
                fail+=1
        print('Number of Sucessful Requests ', sucess)
        print('Number of Dropped Requests ', fail)
        print('Avg latency: {} ms'.format((total_time*1000)/(queued_requests_per_process*processes)))
    finally:
        pool.close()
        pool.join()

def main():

    
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--processes',dest='processes',type=int,default=10, help="Number of parallel processes to use as clients")
    parser.add_argument('-r','--requests',dest='req',type=int,default=10, help="Number of requests each client process will run")
    parser.add_argument('-u','--url',dest='url',type=str, default=url, help="URL that will be used to do the POST request")
    args = parser.parse_args()
   
    runParallelRequests(
        processes=args.processes,
        queued_requests_per_process=args.req,
        url=args.url
    )


if __name__ == "__main__":
    main()

