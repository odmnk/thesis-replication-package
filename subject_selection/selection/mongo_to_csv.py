import pymongo
from dotenv import load_dotenv   #for python-dotenv method
load_dotenv()                    #for python-dotenv method
import os 
import numpy as np
import pandas as pd

def setup_mongodb():

    username = os.environ.get("MONGODB_ATLAS_USER")
    password = os.environ.get("MONGODB_ATLAS_PASSWORD")
    client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.mznnc.mongodb.net/")
    db = client["final"]
    collection = db["realfinal"]
    return collection

def main():
    collection = setup_mongodb()

    subjects_meeting_criteria = collection.aggregate([
    {
        "$match" : 
        {"meets_criteria" : True, "headers_contain_preloads_or_hints" : False}},
    ])


    df = pd.DataFrame(list(subjects_meeting_criteria))
    df.to_csv("sites_meeting_criteria.csv")


if __name__ == "__main__":
    main()
