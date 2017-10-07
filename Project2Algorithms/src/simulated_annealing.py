'''
Created on April 24, 2017

@author: Katherine
'''
import random

def read_google(filename):
    data = dict()
    with open(filename, "r") as fin:

        system_desc = next(fin)
        number_of_videos, number_of_endpoints, number_of_requests, number_of_caches, cache_size= system_desc.split(" ")
        number_of_videos = int(number_of_videos)
        number_of_endpoints = int(number_of_endpoints)
        number_of_requests = int(number_of_requests)
        number_of_caches = int(number_of_caches)
        cache_size = int(cache_size)
        video_ed_request = dict()
        video_size_desc = next(fin).strip().split(" ")
        for i in range(len(video_size_desc)):
            video_size_desc[i] = int(video_size_desc[i])
        ed_cache_list = []

        ### CACHE SECTION

        ep_to_cache_latency = [] 

        ep_to_dc_latency = [] 
        for i in range(number_of_endpoints):
            ep_to_dc_latency.append([])
            ep_to_cache_latency.append([])

            dc_latency, number_of_cache_i = next(fin).strip().split(" ")
            dc_latency = int(dc_latency)
            number_of_cache_i = int(number_of_cache_i)

            ep_to_dc_latency[i] = dc_latency

            for j in range(number_of_caches):
                ep_to_cache_latency[i].append(ep_to_dc_latency[i])

            cache_list = []
            for j in range(number_of_cache_i):
                cache_id, latency = next(fin).strip().split(" ")
                cache_id = int(cache_id)
                cache_list.append(cache_id)
                latency = int(latency)
                ep_to_cache_latency[i][cache_id] = latency

            ed_cache_list.append(cache_list)

        ### REQUEST SECTION
        for i in range(number_of_requests):
            video_id, ed_id, requests = next(fin).strip().split(" ")
            video_ed_request[(video_id,ed_id)] = requests


    data["number_of_videos"] = number_of_videos
    data["number_of_endpoints"] = number_of_endpoints
    data["number_of_requests"] = number_of_requests
    data["number_of_caches"] = number_of_caches
    data["cache_size"] = cache_size
    data["video_size_desc"] = video_size_desc
    data["ep_to_dc_latency"] = ep_to_dc_latency
    data["ep_to_cache_latency"] = ep_to_cache_latency
    data["ed_cache_list"] = ed_cache_list
    data["video_ed_request"] = video_ed_request

    return data


data = read_google("input/test.txt")

def make_zero_grid():
    #make grid of videos and first initialize them to zero
    number_vids = data['number_of_videos']
    caches = data['number_of_caches']
    global zero_grid
    #make grid of zeros
    zero_grid = [ [0]*number_vids for i in range(caches) ]
    return zero_grid

def find_fitness(grid):
    #iterate through video_ed_request dictionary
    requests= 0
    gains = 0
    for key, value in data['video_ed_request'].items():
        fileID = int(key[0])
        endpoint = int( key[1])
        caches =[]
        #check to see if video is even IN a cache
        cache_check = False
        for i in  range (len(grid)):
            if grid[i][fileID]==1:
                caches.append(i)
                cache_check = True
        num_requests = int(value)
        requests += num_requests
        dc_latency = data['ep_to_dc_latency'][endpoint]
        #now match endpoint with dc_latency index
        if cache_check:
            latency_ep_to_c =data["ep_to_cache_latency"][endpoint][caches[0]]
        else:
            latency_ep_to_c = dc_latency
        #if video is in more than one cache, find best (least) latency
        for i in caches:
            if data["ep_to_cache_latency"][endpoint][i] < latency_ep_to_c:
                latency_ep_to_c = data["ep_to_cache_latency"][endpoint][i]
        difference =  dc_latency - latency_ep_to_c
        gains += difference * num_requests
    fitness_score = (gains/requests)*1000 #because milliseconds
    return fitness_score


#slightly different function than others because is only one grid
def random_solution(grid):
    for cache in range (len(grid)):
        #cache size
        current_cache_size = data['cache_size']
        #track all videos in each cache in each grid
        for video in range (len(grid[cache])):
            #find individual video size
            video_size = (data['video_size_desc'][video])
            #15% chance that 0 turns to 1
            if random.random()<=0.15:
                if grid[cache][video] == 0:
                    grid[cache][video] = 1
                        #video takes up room in cache so remove video size from  available cache size
                    current_cache_size -= video_size
                        #check if cache size is completely consumed
                    if current_cache_size < 0:
                        grid[cache][video] = 0
                        current_cache_size += video_size
                            #if cache is consumed with that video, try the next vid. If that vid is out of range, try first vid in list
                        try:
                            grid[cache][video+1] = 1
                            current_cache_size -= data['video_size_desc'][video+1]
                            if current_cache_size < 0:
                                grid[cache][video+1] = 0
                                current_cache_size += data['video_size_desc'][video+1]
                        except IndexError:
                            grid[cache][0] = 1
                            current_cache_size -= data['video_size_desc'][0]
                            if current_cache_size < 0:
                                grid[cache][0] = 0
                                current_cache_size += data['video_size_desc'][0]
                else:
                    grid[cache][video] = 0
                    current_cache_size += video_size
            else:
                continue
    return grid

def make_neighbor(grid):
    #pick random cache and video to change
    #if 1 change 0 and vise versa
    random_cache = random.randint(0,data["number_of_caches"]-1)
    random_vid = random.randint(0,data["number_of_videos"]-1)
    if grid[random_cache][random_vid] == 0:
        grid[random_cache][random_vid] = 1
    else:
        grid[random_cache][random_vid] = 0
    return grid

def acceptance_prob(score1, score2, T):
    #will have to switch old and new scores because in this case I think we are aiming for the maximum score 
    #so bigger value is actually better
    numerator = (score2 - score1)
    ap = 2.71828*(numerator/T)
    return ap

def anneal(solution):
    score = find_fitness(solution)
    T = 1.0
    T_min = 0.00001
    alpha = 0.9
    while T > T_min:
        i = 1
        while i <= 100:
            new_solution = make_neighbor(solution)
            new_score = find_fitness(new_solution)
            ap = acceptance_prob(score, new_score, T)
            if ap > random.random():
                solution = new_solution
                score = new_score
            i += 1
        T = T*alpha
    return solution, score

def find_solution():
    zero_grid = make_zero_grid()
    random_grid = random_solution(zero_grid)
    solution = anneal(random_grid)
    print('best score found with simulated annealing is ', solution[1] )
    return solution[1]

find_solution()
    