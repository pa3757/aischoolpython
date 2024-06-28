import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Place:
    img_rname: str
    poi_desc: str
    # poi_info: str
    poi_name: str
    poi_region: str
    poi_tag: str

    def to_dict(self):
        return {
            "img_rname": self.img_rname,
            "poi_desc": self.poi_desc,
            # "poi_info": self.poi_info,
            "poi_name": self.poi_name,
            "poi_region": self.poi_region,
            "poi_tag": self.poi_tag
        }

@dataclass
class Music:
    music_genre: str
    music_image: str
    music_lyric: str
    music_singer: str
    music_title: str

    def to_dict(self):
        return {
            "music_genre": self.music_genre,
            "music_image": self.music_image,
            "music_lyric": self.music_lyric,
            "music_singer": self.music_singer,
            "music_title": self.music_title
        }

@dataclass
class Recommendation:
    result_choice: str
    count: int
    music: List[Music]
    places: List[Place]

    def to_dict(self):
        return {
            "result_choice": self.result_choice,
            "count": self.count,
            "music": [m.to_dict() for m in self.music],
            "places": [p.to_dict() for p in self.places]
        }

def merge_recommendations(existing_place: List[Dict[str, str]], existing_music: List[Dict[str, str]], recommendation_results: List[Dict[str, str]]) -> List[Recommendation]:
    merged_data = []

    for idx, result in enumerate(recommendation_results):
        choice = result["choice"]
        recommended_region = result["region"][0]  # recommended_region은 리스트로 저장되어 있음
        places = result["places"]

        places_objects = []
        music_objects = []

        for place in places:
            place_name = place["place_name"]
            music_list = place["music"]

            place_info = next((p for p in existing_place if p["poi_name"] == place_name), None)
            if place_info:
                places_obj= Place(
                    img_rname=place_info["img_rname"],
                    poi_desc=place_info["poi_desc"],
                    # poi_info=place_info.get("poi_info", "정보 없음"),
                    poi_name=place_info["poi_name"],
                    poi_region=place_info["poi_region"],
                    poi_tag=place_info["poi_tag"]
                )
                places_objects.append(places_obj)

        for music_title in music_list:
            music_info = next((music for music in existing_music if music["music_title"] == music_title), None)
            if music_info:
                    music_obj = Music(
                        music_genre=music_info["music_genre"],
                        music_image=music_info["music_image"],
                        music_lyric=music_info["music_lyric"],
                        music_singer=music_info["music_singer"],
                        music_title=music_title
                    )
                    music_objects.append(music_obj)

        merged_data.append(Recommendation(
            result_choice=choice,
            count=0,  # 예시로 0으로 설정, 필요시 다른 값으로 수정 가능
            music=music_objects,
            places=places_objects
        ))

    return merged_data

# 기존 데이터 파일 로드
with open("Travle_Data.json", "r", encoding='utf-8') as fp:
    existing_place = json.load(fp)

with open("Music_Data.json","r",encoding='utf-8') as fp:
    existing_music = json.load(fp)

# 추천 결과 파일 로드
with open("000melodymap_results.json", "r", encoding='utf-8') as fp:
    recommendation_results = json.load(fp)

# 추천 결과와 기존 데이터 병합
merged_results = merge_recommendations(existing_place, existing_music, recommendation_results)

# 병합된 결과를 JSON 파일로 저장
with open('FINAL.json', 'w', encoding='utf-8') as file:
    json.dump([result.to_dict() for result in merged_results], file, ensure_ascii=False, indent=2)
