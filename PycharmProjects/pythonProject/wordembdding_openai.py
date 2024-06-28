import json
import configparser
from openai import OpenAI
import pandas as pd
from tqdm import tqdm

# 환경 설정 파일에서 API 키 읽기
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['openai']['api_key']

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

def extract_features_from_data():
    """ CSV파일에서 데이터를 읽어 임베딩을 추출합니다. """
    df = pd.read_csv('Travle/TravleData - TravleData.csv')

    # 모든 관련 속성을 하나의 문자열로 결합
    df['info'] =df.apply(lambda row: ' '.join([
        str(row['poi_region']),
        str(row['poi_name']),
        ' '.join(eval(row['poi_tag'])),  # 태그는 리스트로 저장되어 있다고 가정 (eval 사용)
        str(row['img_rname']),
        str(row['poi_desc'])
    ]), axis=1)

    features_list = []

    for poi_region,poi_name, info in tqdm(zip(df['poi_region'],df['poi_name'],df['info']), desc="임베딩 중", total=df.shape[0]):
        try:
            response = client.embeddings.create(
                input=[info],
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            features_list.append({
                "region": poi_region,
                "place": poi_name,
                "embedding": embedding
                })
        except Exception as e:
            print(f"{['poi_name']} 처리 중 오류 발생: {e}")
            continue

    # 추출된 특징을 JSON 파일로 저장
    with open("extracted_place_features.json", "w", encoding='utf-8') as fp:
        json.dump(features_list, fp, ensure_ascii=False, indent=4)

# 함수 호출
extract_features_from_data()