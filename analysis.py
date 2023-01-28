# data를 받아서 자주 등장하는 단어들을 freq_datas로 반환합니다.

def analysis(keyword, context):
    from stopwords import stopwords
    import pandas as pd
    import numpy as np
    from konlpy.tag import Hannanum
    from collections import Counter
    import re

    word = re.compile(f'[가-힣ㄱ-ㅎㅏ-ㆌ0-9{keyword}{keyword.upper()}{keyword.lower()}]+')
    context['내용'] = context['내용'].apply(lambda x: word.findall(str(x)))
    context['내용'] = context['내용'].apply(lambda x: ' '.join(x))

    ###
    han = Hannanum()
    sw_han = han.nouns(stopwords)
    # https://konlpy.org/ko/latest/api/konlpy.tag/#module-konlpy.tag._hannanum
    context['context_han'] = context['내용'].apply(lambda x : han.nouns(str(x)))
    word_lst = list()
    for lst in context['context_han']:
        for word in lst:
            if word not in sw_han and len(word) > 1 and word not in keyword:
                word_lst.append(word)

    count = Counter(word_lst)
    freq_datas = dict(count.most_common(n=100))

    return freq_datas

  #### Wordcloud
  ## analysis -> return freq_datas
  ## def wordcloud(keyword, mask_path, font_path):
  ## data = crawling(keyword)
  ## analysis = analysis(data)
  ## mkwordcld(mask_path, font_path)