import csv
from tqdm import tqdm
import numpy as np
from datetime import datetime
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

def cnt_mapping(cnt):
    return cnt**(5/7)*8

def read_file(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return [tuple(row) for row in reader][1:]

def comp_time_string(time_str, start_t, end_t):
    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    start_time = datetime(*start_t)
    end_time = datetime(*end_t)
    if start_time <= time_obj <= end_time:
        return True

def get_color(base_color, cnt):
    base_color = np.array(base_color)
    base_color = np.array([255,255,255])-255/(255-min(base_color))*(np.array([255,255,255])-base_color)
    color = base_color*cnt_mapping(cnt)+np.array([255, 255, 255])*(256-cnt_mapping(cnt))/256
    for i in range(3):
        if color[i] < 0:
            color[i] =0
        elif color[i] > 255:
            color[i] = 255
    return "#{:02X}{:02X}{:02X}".format(int(color[0]), int(color[1]), int(color[2]))

def create_pic(name,timetable,base_color,rank,send_message,receive_message,real_name_list):
    image = Image.new('RGB', (660, 340), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("yahei.ttf", 10)
    large_font = ImageFont.truetype("yahei.ttf", 16)
    for y in range(timetable.shape[0]):
        for x in range(timetable.shape[1]):
            draw.ellipse((x*20+40, y*20+60, (x+1)*20+38, (y+1)*20+58), fill=get_color(base_color,timetable[y][x]))
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    caption = "The annual message distribution of "+real_name_list[rank-1]+ " and 阿白 in 2024"

    draw.text((100, 10), caption, fill="black", font=large_font)
    for y in range(timetable.shape[0]):
        draw.text((10, y*20+60), months[y], fill="black", font=font)
    for x in range(1, 32):
        draw.text((x*19.9+25, 45), str(x), fill="black", font=font)
    draw.text((30, 30), 
              "Name: "+real_name_list[rank-1]+
              "      Sent: "+str(send_message)+"      Received:"+str(receive_message)+
              "      Total: "+str(send_message+receive_message)+
              "      Rank: "+str(rank)+
              "      R/S ratio: "+str(round(receive_message/send_message, 3)),fill="black", font=font)
    
    draw.text((20, 300), "Sent: Messages I sent to you this year.      Received: Messages I recieved from you this year", fill="black", font=font)
    draw.text((20, 320), "R/S: The expected response I receive from you for every message.      Rank: The total rank of number of messages", fill="black", font=font)
    image.save('output'+name+'2024.png')
    pass

def get_real_name(filtered_list,rank_name_list):
    real_name_list=[]
    for name, count in rank_name_list:
        person_query=[t for t in filtered_list if t[-3] == name]
        real_name_list.append(person_query[0][-2])
    return real_name_list

def filter_time(tuples_list, start_time, end_time):
    start_time = tuple(start_time)
    end_time = tuple(end_time)
    return [t for t in tuples_list if comp_time_string(t[-4], start_time, end_time)]

def rank_name(filtered_list,capacity):
    counter = Counter([t[-3] for t in filtered_list if t[-3] != ''])
    return counter.most_common(capacity)

def individual_query(filtered_list, query_name,rank):
    person_query=[t for t in filtered_list if t[-3] == query_name]
    total_message = len(person_query)
    send_message = 0
    for person in person_query:
        if person[4]=='1':
            send_message+=1
    receive_message = total_message - send_message
    print(f'{query_name} send {send_message} messages and receive {receive_message} messages in total {total_message} messages, rank {rank}')
    timetable=np.ones((12,31))
    for t in person_query:
        month = int(t[-4][5:7])
        day = int(t[-4][8:10])
        timetable[month-1][day-1]+=1
    timetable.clip(0,255)
    return timetable,send_message,receive_message
    

if __name__ == '__main__':
    csv_file_path = 'messages.csv'
    start_time = [2024, 1, 1, 0, 0, 0]
    end_time = [2024, 12, 31, 23, 59, 59]
    tuples_list = read_file(csv_file_path)
    filtered_list = filter_time(tuples_list, start_time, end_time)
    rank_name_list = rank_name(filtered_list, 20)
    base_color = np.array([255, 0, 0])
    rank = 0
    color_list=[[197,150,184],[243,179,193],[153,78,68],[138,161,143],
                [175,171,159],[64,80,41],[0,0,0],[212,180,191],[228,217,189],[180,91,93],[253,163,142],
                [158,168,152],[87,100,108],[155,20,14],[244,210,201],
                [164,232,235],[0,255,0],[255,0,0],[255,255,0],[255,255,0],[0,255,0],[255,0,0],[255,255,0],[255,255,0],[0,0,255]]
    for name, count in tqdm(rank_name_list):
        rank += 1
        individual_list,send_message, receive_message = individual_query(filtered_list, name, rank)
        real_name_list = get_real_name(filtered_list,rank_name_list)
        create_pic(name,individual_list,color_list[rank-1],rank,send_message,receive_message,real_name_list)

    

