import json
import torch
import clip
import torch.nn.functional as F
from tqdm import tqdm
import numpy as np

# CLIP 모델 로드
DEVICE = "cpu"
MODEL_NAME = "ViT-B/32"
model, preprocess = clip.load(MODEL_NAME, device=DEVICE)

def recommend_region(choice: str, embedding: list) -> str:
    with open("place_text_features.json", "r", encoding='utf-8') as fp:
        place_feature = json.load(fp)

        # 입력받은 임베딩 벡터를 텐서로 변환하고 DEVICE에 올립니다.
        text_features = torch.tensor(embedding).unsqueeze(0).to(DEVICE)

        # 각 지역에 대한 유사도를 저장할 딕셔너리를 초기화합니다.
        region_similarities = {}

        # 로드한 장소 특성 데이터에 대해 반복하며 각 지역과의 코사인 유사도를 계산합니다.
        for feature in place_feature:
            region = feature['region']  # 지역이름
            place = feature['place']  # 장소이름
            region_features = torch.tensor(feature['embedding']).unsqueeze(0).to(DEVICE)

            # 텍스트 특성 벡터와 지역 특성 벡터 사이의 코사인 유사도를 계산합니다.
            similarity = F.cosine_similarity(text_features, region_features).mean().item()
            # 계산된 유사도를 딕셔너리에 저장
            region_similarities[region] = similarity

        # 가중치 계산
        similarity_sum = sum([similarity ** 2 for similarity in region_similarities.values()])
        similarity_weights = [similarity ** 2 / similarity_sum for similarity in region_similarities.values()]

        # 유사도 정렬하여 관련성 높은 지역 추천 (확률 기반 선택)
        recommended_region = np.random.choice(list(region_similarities.keys()), 1, p=similarity_weights)[0]

        print(f"사용자 유형 '{choice}': 추천지역은 '{recommended_region}'.")

    return recommended_region

def recommend_places_in_region(region: str) -> list:
    # 여행지 특성 파일 열기
    with open("place_text_features.json", "r", encoding='utf-8') as fp:
        place_features = json.load(fp)

    place_similarities = {}

    for feature in place_features:
        # 추천받은 지역과 일치하는 여행지
        if feature['region'] == region:
            place = feature['place']
            # 유사성 측정하기
            similarity = F.pairwise_distance(
                torch.tensor(feature['embedding']),
                torch.tensor([0] * len(feature['embedding'])),
                p=2   # P=1 로 하면 맨해튼 거리유사도로 계산 가능
            ).sum().item()
            # 계산된 유사도 점수 저장하기
            place_similarities[place] = similarity

    # 가중치를 사용한 샘플링 수행
    similarity_sum = sum([sim ** 2 for sim in place_similarities.values()])
    similarity_weights = [sim ** 2 / similarity_sum for sim in place_similarities.values()]

    recommended_places = np.random.choice(list(place_similarities.keys()), 5, p=similarity_weights)
    recommended_places = recommended_places.tolist()

    print(f"지역에 따른 '{region}': 추천여행지 {recommended_places}.")
    return recommended_places

def recommend_music(place: str) -> list:
    with open("place_image_features.json", "r", encoding='utf-8') as fp:
        place_features = json.load(fp)
    with open("music_image_features.json", "r", encoding='utf-8') as fp:
        music_features = json.load(fp)

    # 입력된 장소 이름에 해당하는 특성을 찾는다.
    place_feat = next((p['embedding'] for p in place_features if p['place'] == place), None)

    # 장소 특성을 텐서로 변환
    place_feat_tensor = torch.tensor(place_feat, dtype=torch.float32).unsqueeze(0)

    similarities = {}

    for music in music_features:
        music_title = music['music_title']
        music_feature = torch.tensor(music['features'])  # 음악의 특성을 텐서로 변환

        # 유사성 계산 (p=1일 경우 맨해튼 거리)
        similarity = F.pairwise_distance(place_feat_tensor, music_feature, p=1).sum().item()
        similarities[music_title] = similarity

    # 가중치를 사용한 샘플링 수행
    similarity_sum = sum([sim ** 2 for sim in similarities.values()])
    similarity_weights = [sim ** 2 / similarity_sum for sim in similarities.values()]

    recommended_music = np.random.choice(list(similarities.keys()), 25, p=similarity_weights)
    recommended_music = recommended_music.tolist()

    print(f"장소 '{place}': 추천 음악 {recommended_music}.")
    return recommended_music

def process_all_recommendations(data):
    new_results = [] # 새로운 결과를 저장할 리스트 초기화

    # data 리스트의 각 아이템에 대해 반복 처리
    for item in tqdm(data, desc="추천알고리즘 실행중"):
        choice = item['choice'] # 각 아이템의 choice 키의 값을 가져옴
        embedding = item['embedding'] # embedding 키의 값을 가져옴

        # 추천 지역 받아오기
        recommended_region = recommend_region(choice, embedding)

        # 추천받은 지역을 기반으로 추천 여행지를 받아오기
        recommended_places = recommend_places_in_region(recommended_region)

        # 각 여행지에 대한 음악 추천을 저장할 딕셔너리
        place_music_map = {}

        # 각 여행지에 대한 음악 추천을 저장할 딕셔너리
        places = []

        # 추천 받은 여행지 목록에서 각 여행지에 대해 반복
        for place in recommended_places:
            # 추천 음악 목록 받아오기
            music_list = recommend_music(place)
            # 여행지와 음악 목록을 딕셔너리에 저장
            places.append({
                "place_name": place,
                "music": music_list
            })

        # 최종 결과를 new_results 리스트에 추가
        new_results.append({
            "choice": choice,
            "region": [recommended_region],  # 리스트로 변환하여 저장
            "places": places
        })

    # new_results 안의 모든 np.array를 변환
    for result in new_results:
        if isinstance(result['region'], np.ndarray):
            result['region'] = result['region'].tolist()
        for place in result['places']:
            if isinstance(place['music'], np.ndarray):
                place['music'] = place['music'].tolist()

    # 모든 결과를 저장하기
    with open('000melodymap_results.json', 'w', encoding='utf-8') as file:
        json.dump(new_results, file, ensure_ascii=False, indent=2)

    return new_results

# 데이터 불러오기
with open('extracted_choice_features.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 전체 추천 과정 실행
final_results = process_all_recommendations(data)

# 결과를 JSON 파일로 저장
with open('Recommendation_results.json', 'w', encoding='utf-8') as file:
    json.dump(final_results, file, ensure_ascii=False, indent=4)
