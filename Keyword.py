import string
from keybert import KeyBERT
import re
import os
import csv
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# 下载必要的数据
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# 初始化词形还原器
lemmatizer = WordNetLemmatizer()


# 定义函数，用于将词性标注转换为 WordNet 词性标注
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


checklist_columns = ['repo', 'checklist', 'keyword']
count_columns = ['repo', 'count']
checklist_data = []
count_data = []

folder_path = './PRT'
kw_model = KeyBERT(model="all-mpnet-base-v2")

for filename in os.listdir(folder_path):
    with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
        count = 0
        lst = filename.lower().replace(".txt", "").split("_")
        repo = lst[1] + " " + lst[2]
        lines = file.readlines()
        for line in lines:
            data = re.findall(r'- \[ \](.*)$', line)
            print(data)
            if data:
                checklist = data[0].lower().replace(lst[1], "").replace(lst[2], "")
                # 正则表达式去除所有的非英文字符，以及方括号后面的圆括号URL
                checklist = re.sub(r'[^\x00-\x7F]+', '', checklist)
                checklist = re.sub(r'\]\((.+?)\)', '', checklist)
                s = checklist.translate(str.maketrans("", "", string.punctuation))

                words = s.split()
                if len(words) < 4:
                    continue

                # 对文本进行分词和词性标注
                tokens = nltk.word_tokenize(checklist)
                tagged = nltk.pos_tag(tokens)
                # 遍历每个单词，进行词形还原
                checklist = ""
                for word, tag in tagged:
                    # 将词性标注转换为 WordNet 词性标注
                    pos = get_wordnet_pos(tag)
                    # 如果无法识别词性，则不进行词形还原
                    if pos is None:
                        checklist += word + " "
                    else:
                        # 进行词形还原，并将结果添加到还原后的文本中
                        lemmatized_word = lemmatizer.lemmatize(word.lower(), pos=pos)
                        checklist += lemmatized_word + " "

                print(checklist)
                keywords = kw_model.extract_keywords(checklist, keyphrase_ngram_range=(1, 1),
                                                     stop_words='english', top_n=1)
                print(keywords)
                if keywords:
                    count += 1
                    checklist_data.append([repo, checklist, keywords[0][0]])
        if count > 0:
            count_data.append([repo, count])

with open('./checklist.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    # 写入列名
    writer.writerow(checklist_columns)
    # 一次性写入数据
    writer.writerows(checklist_data)

with open('./count.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    # 写入列名
    writer.writerow(count_columns)
    # 一次性写入数据
    writer.writerows(count_data)

kw_model = KeyBERT(model="all-mpnet-base-v2")
with open("./PRT/prt_x.txt", "r", encoding="utf-8") as f:
    data = f.readlines()
    for d in data:
        local = re.findall(r'- \[ \](.*)$', d)
        if local:
            ls = local[0].replace('apache', '').replace('druid', '')
            print(ls)
            keywords2 = kw_model.extract_keywords(ls,
                                                  keyphrase_ngram_range=(1, 2),
                                                  stop_words='english',
                                                  top_n=1)
            print(keywords2[0][0])
