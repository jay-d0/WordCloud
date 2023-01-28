def make_wcld(keyword, freq_datas, path, font, mask):
  import matplotlib.pyplot as plt
  import numpy as np
  from PIL import Image
  from wordcloud import WordCloud

  font_dict = {"cookie" : "CookieRun Bold",
               "subtitles" : "DXMSubtitlesM",
               "gmarket" : "GmarketSansTTFMedium",
               "Batang" : "KoPubBatangMedium",
               "Dotum" : "KoPubDotumMedium"}
  
  if font in font_dict.keys():
    font = font_dict[font]

  fontpath = f'fonts/{font}.ttf'
  plt.rc('font', family=font+'.ttf')

  mask = np.array(Image.open(f"mask/{mask}.png"))

  wordcl = WordCloud(font_path = fontpath,
      width = 800,
      height = 800,
      background_color="white",
      mask = mask,
      min_font_size = 3
  )

  wordcl = wordcl.generate_from_frequencies(freq_datas)
  plt.figure(figsize=(20, 20))
  plt.imshow(wordcl, interpolation="bilinear")
  plt.axis("off")
  plt.savefig(f'{path}/wordcloud_{keyword}.jpg', dpi=600)
  plt.show()