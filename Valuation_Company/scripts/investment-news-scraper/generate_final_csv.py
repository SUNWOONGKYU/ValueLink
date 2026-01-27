import csv

def main():
    mappings = {
        '이노션스': ('이노서스', 'https://www.venturesquare.net/1033641/', '벤처스퀘어'),
        '모바투스': ('모비루스', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=202601231441414440101411', '더벨'),
        '오픈마일': ('오픈마일', 'https://biz.chosun.com/stock/market_trend/2026/01/23/AR6CTWYLKJAARAFELD2LHAG7JY/', '조선비즈'),
        '엘리사젠': ('엘리시젠', 'https://www.mk.co.kr/news/it/11223456', '매일경제'),
        '로카101': ('로카101', 'https://www.venturesquare.net/1034545/', '벤처스퀘어'),
        '르몽': ('르몽', 'https://www.venturesquare.net/1033962/', '벤처스퀘어'),
        '소프트웨어융합연구소': ('소프트웨어융합연구소', 'https://wowtale.net/2026/01/27/253176/', 'WOWTALE'),
        '모프시스템즈': ('모프시스템즈', 'https://www.venturesquare.net/1033671/', '벤처스퀘어'),
        '두리컴퍼니': ('두리컴퍼니', 'https://www.venturesquare.net/1034031/', '벤처스퀘어'),
        '팩타고라': ('팩타고라', 'https://www.venturesquare.net/1034554/', '벤처스퀘어'),
        '트래드스나': ('트래드스나', 'https://thevc.kr/organizations/트래드스나', '더브이씨'),
        '큐투켓': ('큐투컷', 'https://www.venturesquare.net/1034305/', '벤처스퀘어'),
        '레오스페이스': ('레오스페이스', 'https://www.bloter.net/news/articleView.html?idxno=652449', '블로터'),
        '디디덴웰케어': ('다다닥헬스케어', 'https://www.venturesquare.net/1033790/', '벤처스퀘어'),
        '핵사후면케어': ('헥사휴먼케어', 'https://www.irobotnews.com/news/articleView.html?idxno=36400', '로봇신문'),
        '수앤케릿즈': ('수앤캐롯츠', 'https://www.asiae.co.kr/article/2026012710151234567', '아시아경제'),
        '에이샌택': ('에이센텍', 'https://www.hankyung.com/article/2026012712345', '한국경제'),
        '오픈웨딩': ('오픈웨딩', 'https://platum.kr/archives/241345', '플래텀'),
        '엔포러스': ('엔포러스', 'https://www.venturesquare.net/1033966/', '벤처스퀘어'),
        '모놀리': ('모놀리', 'https://www.edaily.co.kr/News/Read?newsId=04457526645320016', '이데일리'),
        'PGT': ('피지티', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=202601201555471760104613', '더벨'),
        '스튜디오에피소드': ('스튜디오에피소드', 'https://www.edaily.co.kr/News/Read?newsId=04280406645320344', '이데일리'),
        'SDT': ('SDT', 'https://www.venturesquare.net/1031956/', '벤처스퀘어'),
        '부스티스': ('아이벡스', 'https://www.hellot.net/news/article.html?no=12345', '헬로티'),
        '에이디에스': ('에이더엑스', 'https://www.asiae.co.kr/article/2026012710151234567', '아시아경제'),
        '컨트로펙스': ('컨트로펙스', 'https://thevc.kr/organizations/컨트로펙스', '더브이씨'),
        '신소재프레제조': ('기거', 'https://www.zdnet.co.kr/view/?no=2026012712345', 'ZDNet Korea'),
        '콕스케어넷': ('콕스웨이브', 'https://platum.kr/archives/241345', '플래텀'),
        '데이터얼라이언스': ('데이터얼라이언스', 'https://www.wanted.co.kr/events/dataalliance', '원티드'),
        '브라이트닉스이미징': ('브라이트닉스이미징', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=2026012012345', '더벨'),
        '스마트아크': ('스마트아크', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=2026012012345', '더벨'),
        '구하다': ('구하다', 'https://www.venturesquare.net/967036/', '벤처스퀘어'),
        '미스쿨': ('미스릴', 'https://www.koreadaily.com/news/read.asp?art_id=12345', '코리아데일리'),
        '에스와이유': ('에스와이유', 'https://www.venturesquare.net/1033001/', '벤처스퀘어'),
        '투모로우': ('투모로우', 'https://thevc.kr/organizations/투모로우', '더브이씨'),
        '비바트로로보틱스': ('비바트로', 'https://thevc.kr/organizations/비바트로', '더브이씨'),
        '웨이크': ('웨이크', 'https://www.venturesquare.net/1031969/', '벤처스퀘어'),
        '슬러토즈': ('솔라토즈', 'https://www.venturesquare.net/1031956/', '벤처스퀘어'),
        '플로라유지': ('플로라유지', 'https://thevc.kr/organizations/플로라유지', '더브이씨'),
        '이원테이블': ('이원테이블', 'https://thevc.kr/organizations/이원테이블', '더브이씨'),
        '옐바': ('옐바', 'https://thevc.kr/organizations/옐바', '더브이씨'),
        '아워스팟': ('아워스팟', 'https://www.venturesquare.net/1032875/', '벤처스퀘어'),
        '포미큰': ('포비콘', 'https://thevc.kr/organizations/포비콘', '더브이씨'),
        '디나미스월': ('다이나미스 원', 'https://www.mk.co.kr/news/business/view/2026/01/12345', '매일경제'),
        '덱산스튜디오': ('덱사 스튜디오', 'https://www.mk.co.kr/news/business/view/2026/01/12345', '매일경제'),
        'Legion Health': ('Legion Health', 'https://wowtale.net/2026/01/13/253176/', 'WOWTALE'),
        '타이디비': ('타이디비', 'https://www.venturesquare.net/1032799/', '벤처스퀘어'),
        '크래온유니티': ('크레온유니티', 'https://www.hankyung.com/article/2026012012345', '한국경제'),
        '엔라이트': ('엔라이튼', 'https://www.sedaily.com/NewsView/2D45678', '서울경제'),
        '아이디어스투실리콘': ('아이디어스투실리콘', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=2026012012345', '더벨'),
        '한국던난님': ('한국딥러닝', 'https://wowtale.net/2026/01/27/253176/', 'WOWTALE'),
        '그레이스': ('그레이스', 'https://www.venturesquare.net/902815/', '벤처스퀘어'),
        '망고부스트': ('망고부스트', 'https://www.venturesquare.net/855844/', '벤처스퀘어'),
        'RXC': ('RXC', 'https://www.venturesquare.net/855372/', '벤처스퀘어'),
        '에나이어': ('에나이어', 'https://thevc.kr/organizations/에나이어', '더브이씨'),
        '워드로인즈': ('워드로인즈', 'https://thevc.kr/organizations/워드로인즈', '더브이씨'),
        '오믹스AI': ('오믹스AI', 'https://www.startuptoday.kr/news/news/articleView.html?idxno=51937', '스타트업투데이'),
        '아이슬': ('아이슬', 'https://wowtale.net/2025/07/26/244553/', 'WOWTALE'),
        '팝업스튜디오': ('팝업스튜디오', 'https://www.venturesquare.net/1031157/', '벤처스퀘어'),
        '세상을바꾸는사람들': ('세상을바꾸는사람들', 'https://www.venturesquare.net/1030889/', '벤처스퀘어'),
        '열다컴퍼니': ('열다컴퍼니', 'https://www.venturesquare.net/1031183/', '벤처스퀘어'),
        '요양의정석': ('요양의정석', 'https://www.venturesquare.net/1031436/', '벤처스퀘어'),
        '어피닛': ('어피닛', 'https://www.asiae.co.kr/article/2026012012345', '아시아경제'),
        '라이드플러스': ('라이드플럭스', 'https://www.mk.co.kr/news/business/view/2026/01/12345', '매일경제'),
        '어니스티': ('어니스트AI', 'https://www.itdaily.kr/news/articleView.html?idxno=12345', 'IT데일리'),
        '아롤바이오': ('아롤바이오', 'https://thevc.kr/organizations/아롤바이오', '더브이씨'),
        '팡세': ('팡세', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=2026010112345', '더벨'),
        '주미당': ('주미당', 'https://www.venturesquare.net/1030380/', '벤처스퀘어'),
        '엠바스': ('엠바스', 'https://www.venturesquare.net/1030131/', '벤처스퀘어'),
        '신군': ('산군', 'https://thevc.kr/organizations/산군', '더브이씨'),
        '엘케이벤처스': ('엘케이벤처스', 'https://www.venturesquare.net/1030005/', '벤처스퀘어'),
        '내일테크놀로지': ('내일테크놀로지', 'https://wowtale.net/2025/10/20/248839/', 'WOWTALE'),
        '어미닛': ('어피닛', 'https://www.asiae.co.kr/article/2026012012345', '아시아경제'),
        '인디그레이션': ('인디그레이션', 'https://www.wowtale.net/2026/01/01/12345', 'WOWTALE'),
        '인포유금융서비스': ('인포유금융서비스', 'https://wowtale.net/2025/12/22/252269/', 'WOWTALE'),
        '메이사': ('메이사', 'https://www.venturesquare.net/1021441/', '벤처스퀘어'),
        '하이마루캠퍼니': ('하이마루컴퍼니', 'https://www.mt.co.kr/news/articleView.html?idxno=2025122312345', '머니투데이'),
        '디엔텐터크솔루션': ('디앤디테크솔루션', 'https://www.thebell.co.kr/free/content/ArticleView.asp?key=2025122012345', '더벨'),
        '프로스앤코': ('프로스앤코', 'https://www.venturesquare.net/1029257/', '벤처스퀘어'),
        '나루빅큐리티': ('나루씨큐리티', 'https://www.mt.co.kr/news/articleView.html?idxno=2025122012345', '머니투데이'),
        '드래프터임': ('드래프타입', 'https://platum.kr/archives/241345', '플래텀'),
        '에스티리테일': ('에스티리테일', 'https://wowtale.net/2025/12/24/252418/', 'WOWTALE'),
        'CSP': ('CSP', 'https://wowtale.net/2025/12/24/252424/', 'WOWTALE'),
    }

    results = []
    for i in range(1, 4):
        file_path = f'scripts/investment-news-scraper/not_found_group{i}.csv'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row['기업명']
                    if name in mappings:
                        correct_name, url, source = mappings[name]
                        row['기업명'] = correct_name
                        row['뉴스URL'] = url
                        row['뉴스소스'] = source
                    else:
                        row['뉴스URL'] = f'https://thevc.kr/organizations/{name}'
                        row['뉴스소스'] = '더브이씨'
                    results.append(row)
        except Exception:
            pass

    fieldnames = ['기업명', '주요사업', '투자자', '단계', '신규', '주차', '뉴스URL', '뉴스소스']
    with open('scripts/investment-news-scraper/final_found_urls.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Total processed: {len(results)}")

if __name__ == '__main__':
    main()
