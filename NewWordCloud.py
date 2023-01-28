def make_wcld(keyword, save_path=None, speed='normal',
              font="cookie", mask="cloud", print_check_time=None):
    import crawling
    from analysis import analysis
    from word_cloud import make_wcld
    import datetime
    import nest_asyncio
    import asyncio

    if print_check_time:
        t0 = datetime.datetime.now()
        print('시작시간 : ', t0)

    if not save_path:
        save_path = f'wordcloud/{datetime.datetime.today().strftime("%y.%m.%d")}'
        import os
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
        except OSError:
            print("Error: Failed to create the directory.")
        

    nest_asyncio.apply()

    context_db = asyncio.run(crawling.crawling(keyword, speed))

    analysis_dict = analysis(keyword, context_db)
    make_wcld(keyword, analysis_dict, save_path, font, mask)

    if print_check_time:
        t1 = datetime.datetime.now()
        print('종료시간 :', t1)
        print('소요시간 : ', t1 - t0)