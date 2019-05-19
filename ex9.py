import json
import os
import random
import shutil
import time
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import HTTPError

url = "http://ws.clarin-pl.eu/nlprest2/base"
user = "szeremet@student.agh.edu.pl"
task = "any2txt|wcrft2|liner2({\"model\":\"n82\"})"


def upload(file):
    with open(file, "rb") as myfile:
        doc = myfile.read()
    return urlopen(Request(url + "/upload/", doc, {"Content-Type": "binary/octet-stream"})).read()


def process(data):
    taskid = ""
    dt = json.dumps(data).encode("utf-8")
    try:
        taskid = urlopen(
            Request(url + "/startTask/", data=dt, headers={"Content-Type": "application/json"})).read().decode("utf-8")
    except HTTPError as e:
        content = e.read()
        print(content)
        exit(1)
    print(taskid)
    time.sleep(0.2)
    resp = urlopen(Request(url + "/getStatus/" + taskid))
    data = json.load(resp)
    while data["status"] == "QUEUE" or data["status"] == "PROCESSING":
        time.sleep(0.5)
        resp = urlopen(Request(url + "/getStatus/" + taskid))
        data = json.load(resp)
        print(data["status"])
        print(data["value"] if "value" in data else "no_val")
    if data["status"] == "ERROR":
        print("Error " + data["value"])
        return None
    return data["value"]


def one_hundred_random_files(filenames):
    return random.sample(filenames, 100)


def read_filenames():
    filenames = []
    for filename in os.listdir(os.getcwd() + "/ustawy"):
        filenames.append(filename)
    return filenames


def copy_to_zip_catalog(filenames):
    for filename in filenames:
        shutil.copyfile(os.getcwd() + "/ustawy/" + filename, os.getcwd() + "/to_zip/" + filename)


def make_input_zip():
    sample = one_hundred_random_files(read_filenames())
    copy_to_zip_catalog(sample)
    shutil.make_archive("input", "zip", os.getcwd() + "/to_zip")


def analyze_with_ner():
    global_time = time.time()
    fileid = upload("input.zip").decode("utf-8")
    lpmn = "filezip(" + fileid + ")|" + task + "|dir|makezip"
    print(lpmn)
    data = {"lpmn": lpmn, "user": user}
    data = process(data)
    if data is not None:
        data = data[0]["fileID"]
        content = urlopen(Request(url + "/download" + data)).read()
        with open("output.zip", "wb") as outfile:
            outfile.write(content)
    print("GLOBAL %s seconds ---" % (time.time() - global_time))


def parse_output():
    channels_occurences = {}
    named_entities_occurences = {}
    for filename in os.listdir(os.getcwd() + "/output"):
        chunk_list = ET.parse("./output/" + filename).getroot()
        for chunk in chunk_list:
            for sentence in chunk:
                entity = ""
                channel = ""
                value = 0
                entities_with_channels_in_sentence = {}
                for tok in sentence:
                    if tok.tag == "tok" and tok is not None:
                        word = tok[0].text
                        (next_channel, next_value) = get_non_zero_annotation_channel(tok)
                        if next_channel is not None and next_value is not None:
                            if channel == "":
                                channel = next_channel
                                value = next_value
                                entity = word + " " if word != "." else word
                            elif channel == next_channel and value == next_value:
                                entity += word + " " if word != "." else word
                            elif (channel != next_channel or value != next_value) and entity.rstrip() != "":
                                if (entity, channel) in entities_with_channels_in_sentence:
                                    entities_with_channels_in_sentence[(entity, channel)] += 1
                                else:
                                    entities_with_channels_in_sentence[(entity, channel)] = 1
                                channel = next_channel
                                entity = ""
                                value = next_value
                for key, val in entities_with_channels_in_sentence.items():
                    if key[1] in channels_occurences:
                        channels_occurences[key[1]] += val
                    else:
                        channels_occurences[key[1]] = val
                    if key in named_entities_occurences:
                        named_entities_occurences[key] += val
                    else:
                        named_entities_occurences[key] = val
    return channels_occurences, named_entities_occurences


def get_non_zero_annotation_channel(tok):
    annotations = list(filter(lambda x: x.tag == "ann" and int(x.text) > 0, tok))
    return (annotations[0].attrib["chan"], int(annotations[0].text)) if len(annotations) > 0 else (None, None)


def get_coarse(fine):
    splitted = fine.split("_")
    return splitted[0] + "_" + splitted[1] if len(splitted) >= 2 else None


def get_coarse_dict(channels):
    coarse_dict = {}
    for key, val in channels.items():
        if get_coarse(key) in coarse_dict:
            coarse_dict[get_coarse(key)] += val
        else:
            coarse_dict[get_coarse(key)] = val
    return coarse_dict


def draw_hist(channels, title):
    vals = list(channels.values())
    keys = list(channels.keys())
    plt.yscale("log")
    plt.bar(keys, vals)
    plt.xticks(range(len(keys)), keys, rotation=90)
    plt.xlabel('Categories')
    plt.ylabel('occurences')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(title + ".png")

    plt.close()


def display_fifty_most_frequent(entities):
    sorted_entities = sorted(entities.items(), key=lambda item: (-item[1], item[0]))[:50]
    print("Top 50 named entities")
    for entity in sorted_entities:
        print("Entity: " + entity[0][0])
        print("Channel: " + entity[0][1])
        print("Count: " + str(entity[1]))


def parse_entities_to_extract_coarse_channels(entities):
    coarse = {}
    for entity in entities.items():
        coarse_channel = get_coarse(entity[0][1])
        if coarse_channel in coarse:
            coarse[coarse_channel].append((entity[0][0], entity[1]))
        else:
            coarse[coarse_channel] = [(entity[0][0], entity[1])]
    return coarse


def display_ten_most_frequent_for_each_coarse(coarse_channels_to_lists):
    for channel_to_list in coarse_channels_to_lists.items():
        channel = channel_to_list[0]
        sorted_top_ten = sorted(channel_to_list[1], key=lambda item: (-item[1], item[0]))[:10]
        print("Coarse channel: " + channel)
        print("Top ten entities:")
        for entity in sorted_top_ten:
            print("Entity: " + entity[0])
            print("Count: " + str(entity[1]))


def main():
    channels, entities = parse_output()
    coarse = get_coarse_dict(channels)
    # draw_hist(channels, "fine grained channels")
    # draw_hist(coarse, "coarse grained channels")
    # display_fifty_most_frequent(entities)
    coarse_to_entities = parse_entities_to_extract_coarse_channels(entities)
    display_ten_most_frequent_for_each_coarse(coarse_to_entities)


if __name__ == "__main__":
    main()
