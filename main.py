import requests
import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from pg_data import Reloads, create_tables
from datetime import datetime
import time

f = open('files/data_source.json', encoding='utf-8')
data_load = json.load(f)
url = data_load['url']
headers = data_load['headers']
intance_to_parse = data_load['intance_to_parse']
timestamp_from = data_load['timestamp_from']
timestamp_to = data_load['timestamp_to']
dsn = f"postgresql://{data_load['pg_data']['user']}:{data_load['password_pg']}@{data_load['pg_data']['ip_addr']}:5432/{data_load['pg_data']['database']}"


def get_all_activities(url, headers) -> dict:
  response = requests.get(f'{url}', headers=headers)
  json_data = json.loads(response.text)

  return json_data

def parse_yt_data(data_from_yt, intance_to_parse, timestamp_from, timestamp_to) -> dict:
    '''
    стандартные данные:
    Эколайф
    Даты с 01.01.2023 по 08.05.2023
    ---
    чтобы изменить, скорректировать files\data_source.json
    '''
    empty_dict = {}
    try:
        for text_1 in range(len(data_from_yt)):
            if data_from_yt[text_1]['created'] >= timestamp_from and data_from_yt[text_1]['updated']>= timestamp_from and data_from_yt[text_1]['created'] <= timestamp_to and data_from_yt[text_1]['updated'] <= timestamp_to: #если даты с 2023-01 по 2023-04
                for i in range(len(data_from_yt[6043]['customFields'])):
                    if data_from_yt[text_1]['customFields'][i]['value'] is not None: #если в value есть значение и там не пусто
                        if type(data_from_yt[text_1]['customFields'][i]) == dict: #если тип dict
                            if type(data_from_yt[text_1]['customFields'][i]['value']) == dict:
                                pass
                            if type(data_from_yt[text_1]['customFields'][i]['value']) == list:
                                for y in range(len(data_from_yt[text_1]['customFields'][i]['value'])):
                                    if data_from_yt[text_1]['customFields'][i]['value'][y]['name'] == intance_to_parse:
                                        issue = data_from_yt[text_1]['idReadable']                                                          #   issue
                                        updated = data_from_yt[text_1]['updated']                                                           #   updated
                                        updated = datetime.fromtimestamp(updated/1000)
                                        created = data_from_yt[text_1]['created']                                                           #   created
                                        created = datetime.fromtimestamp(created/1000)
                                        instance_name = data_from_yt[text_1]['customFields'][i]['value'][y]['name']                         #   instance_name
                                        summary = data_from_yt[text_1]['summary']                                                           #   summary
                                        task_type = data_from_yt[text_1]['customFields'][4]['value']['name']                                #   task_type 
                                        assigneer = data_from_yt[text_1]['customFields'][2]['value']['name']
                                        status = data_from_yt[text_1]['customFields'][3]['value']['name']
                                        creator = data_from_yt[text_1]['reporter']['name']
                                        if data_from_yt[text_1]['customFields'][7]['value'] is not None:
                                            elapsed_time = data_from_yt[text_1]['customFields'][7]['value']['presentation']                 #   elapsed_time
                                        else: elapsed_time = 'None'
                                        empty_dict[issue] = {'updated': updated,'created': created, 'instance_name': instance_name, 'summary': summary, 'task_type': task_type, 'elapsed_time': elapsed_time, 'assigneer': assigneer, 'status': status, 'creator': creator}
                                    else: pass
                            else: pass
                        else: pass
                    else: pass

    except Exception as err:
        print(err)
        pass
    return empty_dict

def inser_data_to_pg(parsed_data, dsn) -> None:
    '''
    example DSN:
    'postgresql://postgres:postgres@localhost:5432/database_name'
    '''
    check_data = select_actual_data(dsn)
    engine = sqlalchemy.create_engine(dsn)
    create_tables(engine)
    Session = sessionmaker(bind = engine)
    session = Session()

    for digit_inf in parsed_data:
        if digit_inf in check_data:
            pass
        
        else:
            data_fill = Reloads(issue = digit_inf, updated = parsed_data[digit_inf]['updated'], created = parsed_data[digit_inf]['created'], instance_name = parsed_data[digit_inf]['instance_name'], summary = parsed_data[digit_inf]['summary'], task_type = parsed_data[digit_inf]['task_type'], elapsed_time = parsed_data[digit_inf]['elapsed_time'], status = parsed_data[digit_inf]['status'], creator = parsed_data[digit_inf]['creator'], assigneer = parsed_data[digit_inf]['assigneer'] )
            session.add(data_fill)
    session.commit()
    session.close()

def select_actual_data (dsn: str) -> list:
    resultset: list = []
    engine = sqlalchemy.create_engine(dsn)
    create_tables(engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    my_query = session.query(Reloads.issue)
    for lines in my_query:
        resultset.append(lines[0])
    session.close()
    return resultset

if __name__ == "__main__":
    
    while True:
        now = datetime.datetime.now()
        if '03:00:00' in str(now):
            data_yt = get_all_activities(url, headers)
            parsed_data = parse_yt_data(data_yt, intance_to_parse,timestamp_from, timestamp_to)
            inser_data_to_pg(parsed_data, dsn)
            time.sleep(60)



