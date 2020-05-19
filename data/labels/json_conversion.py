import pandas as pd
import json

df = pd.read_csv('snipped_labels.csv', names=["personNumber",
                                      "frameNumber",
                                      "headValid", 
                                      "bodyValid", 
                                      "headLeft", 
                                      "headTop", 
                                      "headRight", 
                                      "headBottom", 
                                      "bodyLeft", 
                                      "bodyTop", 
                                      "bodyRight", 
                                      "bodyBottom"])
print(df.head())

data = []
for i in range(len(df)):
    dict_obj = {
        "_id": "placeholder",
        "confidence": 1.00,
        "ymax": int(round(df['headBottom'][i])),
        "label": "person",
        "xmax": int(round(df['headLeft'][i])),
        "xmin": int(round(df['headRight'][i])),
        "ymin": int(round(df['headTop'][i])),
        "frame_number": f"{df['frameNumber'][i] + 1}",
        "time_offset": 0.00,
        "sequence_number": 0.00,
        "infer_id": "placeholder",        
    }
    data.append(dict_obj)

    if i == 0:
        print(data)

with open('snipped_labels.json', 'w') as outfile:
    json.dump(data, outfile)