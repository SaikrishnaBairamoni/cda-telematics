import re
import sys
import matplotlib
import pandas as pd

matplotlib.use("GTK3Agg")
import warnings
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

'''
This script combines bridge logs with the messaging server logs to give the number of dropped messages from each unit.

Input: The script looks within the the argument directory for csv files from Messaging Server, Vehicle Bridge, Streets Bridge and Cloud Bridge log 
,which are parsed log output from the bridges, to calculate the number of dropped messages from each unit.

Required Input File Format: 
The csv files to be read currently need to follow a specific format. 
The messaging server parsed csv needs to start with the word "Messaging" separated by underscores
Streets bridge parsed csv file name needs to start with the word Streets separated by underscores(_)
Vehicle bridge parsed csv file name needs to start with the word Vehicle or BlueLexus or Fusion separated by underscores(_)
Cloud bridge parsed csv  file name needs to start with the word Messaging by separated underscores(_)

'''
def combineFiles(log_dir):

    # Get all csv files
    path_obj = Path(log_dir)
    print(log_dir)
    filenames = [ f.name for f in path_obj.glob('*.csv')]
    
    bridge_csv_exist = False
    bridge_csv_regex = r'.*(Streets|Vehicle|BlueLexus|Fusion|V2xHub|Cloud).*'
    bridges_csv = []

    messaging_server_csv_exist = False
    messaging_server_csv = ""

    for filename in filenames:        
        if "Messaging" in filename:
            messaging_server_csv_exist = True
            messaging_server_csv = log_dir + "/" + filename

        matched = re.match(bridge_csv_regex, filename, re.IGNORECASE)
        if matched:
            bridges_csv.append(log_dir + "/" + filename)
            bridge_csv_exist = True
            
    if not bridge_csv_exist:
        sys.exit("Did not find any Vehicle/Streets/Cloud/BlueLexus/Fusion/V2xHub bridge csv logs in directory: " +log_dir+ "")
    
    if not messaging_server_csv_exist:
        sys.exit("Did not find any Messaging server csv logs in directory: "+log_dir+ "")
    

    messaging_server_df = pd.read_csv(messaging_server_csv)
    infrastructure_units = ['streets_id', 'cloud_id']

    ############# Load messaging server logs and get a list of dataframes for all unit ids
    #### Dictionary of dataframes with unique unit ids
    messaging_server_dfs = dict(tuple(messaging_server_df.groupby('Unit Id')))

    #Remove null entries and metadata column from vehicle bridge dfs
    for key, value in messaging_server_dfs.items():
        if key not in infrastructure_units:
            value = value[~value['Message Time'].isnull()]
            # value = value.drop('Metadata',axis =1)
    
   
    #Get dataframes from bridge logs
    bridge_dfs = dict()
    for bridge_csv in bridges_csv:
        bridge_df = pd.read_csv(bridge_csv)
        bridge_dfs.update(dict(tuple(bridge_df.groupby('Unit Id'))))   

    print(bridge_dfs.keys())


    # Create combined dataframes from 
    for key in bridge_dfs:
        if key in messaging_server_dfs:
            
            bridge_df_combined = pd.merge(bridge_dfs[key], messaging_server_dfs[key],  how='left', left_on=['Topic','Payload Timestamp'], right_on = ['Topic','Message Time'])
            bridge_df_combined.to_csv(log_dir + key + "_combined.csv")

            bridge_missing_message_count = bridge_df_combined['Log_Timestamp(s)'].isnull().sum()
            bridge_total_message_count = len(bridge_df_combined['Payload Timestamp'])
            print("Message drop for unit: ", key)
            print("Missing count: ", bridge_missing_message_count)
            print("Total count: ", bridge_total_message_count)
            print("Percentage of messages received",(1 - (bridge_missing_message_count/bridge_total_message_count))*100)


            topics_with_empty_count = (bridge_df_combined['Message Time'].isnull().groupby([bridge_df_combined['Topic']]).sum().astype(int).reset_index(name='count'))
            topics_with_empty_count = topics_with_empty_count.loc[~(topics_with_empty_count['count']==0)]
            
            print("{} missed messages: ".format(key))
            print(topics_with_empty_count)

            # Plot vehicle data
            bridge_df_combined = bridge_df_combined[bridge_df_combined['Message Time'].isnull()]
            bridge_df_combined['Payload Timestamp'] = pd.to_datetime(bridge_df_combined['Payload Timestamp'], infer_datetime_format=True)
            bridge_df_combined['Message Time'] = pd.to_datetime(bridge_df_combined['Message Time'], infer_datetime_format=True)
            

            ax1 = plt.plot(bridge_df_combined['Topic'], bridge_df_combined['Payload Timestamp'], '|')
            
            #Plot start and end lines
            start_time = pd.to_datetime(messaging_server_dfs[key]['Log_Timestamp(s)'].iloc[0])
            end_time = pd.to_datetime(messaging_server_dfs[key]['Log_Timestamp(s)'].iloc[-1])

            plt.axhline(y = start_time, color = 'r', linestyle = '-', label = 'Test Start Time')
            plt.axhline(y = end_time, color = 'r', linestyle = '-', label = 'Test End Time')

            plt.title('{} : Topics against time of dropped message'.format(key))
            plt.xlabel('Topics with dropped messages hours:mins:seconds')
            plt.ylabel('Time of message drop')
            xfmt = mdates.DateFormatter('%H:%M:%S')
            plt.gcf().autofmt_xdate()
            plt.show()
            # plt.savefig('{}_Message_drop.png'.format(key))

    




def main():
    if len(sys.argv) < 2:
        print('Run with: "python3 get_message_drop.py directory_name"')
    else:
        log_dir = sys.argv[1]
        combineFiles(log_dir)


if __name__ == "__main__":
    main()