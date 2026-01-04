import json
import asyncio
from openai import AsyncOpenAI
import asyncio

promt_impact = "myprm" 

promt_for_unite = "myprtmt" 

aclient = AsyncOpenAI(api_key='mykey', base_url="https://api.deepseek.com")


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


async def analyze_chunk(chunk: str, chunk_num: int) -> tuple[str, int]:
    try:
        msg = [
            {"role": "system", "content": "Ты психолог с многолетним опытом работы."},
            {"role": "user", "content": promt_impact + chunk}
        ]
        
        response = await aclient.chat.completions.create(
            model="deepseek-chat",
            messages=msg,
            stream=False
        )
        
        return (response.choices[0].message.content, chunk_num)
    except Exception as e:
        return (f"Ошибка при анализе чанка {chunk_num}: {str(e)}", chunk_num)


async def parse_conversation_async(file_path: str, output_file: str, chunk_size: int = 250000):

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk)
    

    tasks = [analyze_chunk(chunk, i) for i, chunk in enumerate(chunks)]
    
    results = await asyncio.gather(*tasks, return_exceptions=False)

    results.sort(key=lambda x: x[1])
    with open(output_file, 'w', encoding='utf-8') as f:
        for content, chunk_num in results:
            f.write(f"\n{'='*50}\nАнализ чанка {chunk_num + 1}:\n{'='*50}\n")
            f.write(content)
            f.write("\n")
    
    all_responses = "\n".join([content for content, _ in results])
    
    return all_responses


async def final_unite_analysis(all_responses: str) -> str:
    msg = [
        {"role": "system", "content": "Ты психолог с многолетним опытом работы."},
        {"role": "user", "content": promt_for_unite + all_responses}
    ]
    
    try:
        response = await aclient.chat.completions.create(
            model="deepseek-reasoner",
            messages=msg,
            stream=False,
            max_tokens=30000,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        content = response.choices[0].message.content
        
        return content
    
    except Exception as e:
        return f"Ошибка при финальном анализе: {str(e)}"


async def run_analyze_async(filepath: str, chunk_size: int = 250000) -> str:
    parse_telegram_txt(filepath)
    
    new_file = filepath.replace(".json", ".txt")
    result_file = new_file.replace(".txt", "") + "_result.txt"

    all_responses = await parse_conversation_async(
        file_path=new_file,
        output_file=result_file,
        chunk_size=chunk_size
    )
    final_result = await final_unite_analysis(all_responses)
    
    return final_result


