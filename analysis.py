import os
from openai import OpenAI
import json


promt_impact = "mypromt" 

promt_for_unite = "mypromt"

msg = [{"role": "system", "content": "Ты психолог с многолетним опытом работы."},
        {"role": "user", "content": ""}]

msg[1]['content'] = '' + promt_impact + '\n'

client = OpenAI(api_key='mykey', base_url="https://api.deepseek.com")


def parse_telegram_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    to_write = open(file_path.replace(".json", "")+".txt", 'w')
    for msg in data['messages']:
        try:
            to_write.write(msg['from'] + ": ")
        except:
            to_write.write("пересланное сообщение" + ": ")
        if isinstance(msg.get('text'), list):
            for item in msg['text']:
                if isinstance(item, dict):
                    to_write.write(str(item.get('text', '')))
                else:
                    to_write.write(str(item))
        elif msg.get('text'):
            to_write.write(str(msg['text']))
        to_write.write('\n')

def parse_conversation(file_path, file_2):

    chunk_size = 250000
    file = open(file_path, 'r')

    for line in file.readlines():
        msg[1]['content'] += line

        if len(msg[1]['content']) >= chunk_size:

            response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=msg,
                    stream=False)
            msg[1]['content'] = '' + promt_impact + '\n'
            file_2.write("----")
            file_2.write(str(response.choices[0].message.content))

    # for last part
    response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=msg,
                    stream=False)
    msg[1]['content'] = '' + promt_for_unite + '\n'
    file_2.write("----")
    file_2.write(str(response.choices[0].message.content))
    file_2.close()

    return


def run_analyze(filepath):

    parse_telegram_txt(file_path=filepath)
    new_file = filepath.replace(".json", ".txt")
    result_file = new_file.replace(".txt", "") + "_result.txt"
    result_file_w = open(result_file, 'w')
    parse_conversation(file_path=new_file, file_2=result_file_w)

    read_analysis = open(result_file, 'r')

    for line in read_analysis.readlines():
        msg[1]['content'] += line

    response = client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=msg,
                    stream=False,
                    max_tokens=30000,
                    extra_body={"thinking": {"type": "enabled"}}

                )

    return "**Размышления:** " + str(response.choices[0].message.reasoning_content) + "\n\r**Ответ:** " + str(response.choices[0].message.content)
