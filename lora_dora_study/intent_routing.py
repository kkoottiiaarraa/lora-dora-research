"""Small deterministic tool-ID protocol helpers; external system text is supplied."""
import hashlib
import json
import re
import string

IDS=string.ascii_lowercase+string.ascii_uppercase


def gold_id(example):
    tools=example['available_tools']
    if len(tools)>len(IDS):raise ValueError('More tools than positional labels')
    names=[str(tool['name']).lower() for tool in tools]
    if len(set(names))!=len(names):raise ValueError('Ambiguous tool-name mapping')
    answer=str(example['answer']).strip().lower()
    if answer=='none':return '-'
    if answer not in names:raise ValueError('Gold tool is absent')
    return IDS[names.index(answer)]


def chat_messages(example,system,with_answer=False):
    gold=gold_id(example)
    table='\n'.join(['ID | Name | Description']+[
        f"{IDS[i]} | {tool['name']} | {tool['description']}" for i,tool in enumerate(example['available_tools'])])
    text=f"Available Tools:\n{table}\nUser Request:\n{example['user_request']}\n\nSelected Tool:"
    result=[dict(role='system',content=system),dict(role='user',content=text)]
    if with_answer:result.append(dict(role='assistant',content=gold))
    return result


def extract_id(text):
    cleaned=re.sub(r'<think>.*?</think>','',text,flags=re.DOTALL).strip()
    for line in cleaned.splitlines():
        value=line.strip().strip('*_`"\'')
        prefix='selected tool:'
        if value.lower().startswith(prefix):value=value[len(prefix):].strip().strip('*_`"\'')
        words=value.split()
        if words:return words[0].rstrip('.,;:()')
    return ''


def case_digest(example):
    return hashlib.sha256(json.dumps(example,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
