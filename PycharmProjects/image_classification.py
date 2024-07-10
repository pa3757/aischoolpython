import os
from datasets import load_dataset, Dataset, DatasetDict, Features, ClassLabel, Image
import pandas as pd
from transformers import ViTFeatureExtractor, ViTForImageClassification, TrainingArguments, Trainer
from PIL import Image
import torch

# 데이터셋 경로 설정
data_dir = 'foodimg_data'

# 데이터셋을 로드하는 함수 정의
def load_images(data_dir):
    data = []
    labels = {'food': 0}

    for label_name, label_idx in labels.items():
        folder_path = os.path.join(data_dir, label_name)
        for filename in os.listdir(folder_path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                file_path = os.path.join(folder_path, filename)
                data.append({
                    'image': file_path,
                    'label': label_idx
                })

    return data

# 데이터셋 로드
data = load_images(data_dir)
df = pd.DataFrame(data)
features = Features({
    'image': Image(),
    'label': ClassLabel(names=['food',])
})
dataset = Dataset.from_pandas(df, features=features)

# 데이터셋을 학습과 검증으로 분할
dataset = dataset.train_test_split(test_size=0.3)
dataset_dict = DatasetDict({
    'train': dataset['train'],
    'validation': dataset['test']
})

# Feature Extractor 로드
feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')

# 전처리 함수 정의
def preprocess_images(examples):
    images = [example['image'] for example in examples]
    inputs = feature_extractor(images=images, return_tensors='pt')
    return inputs

# 데이터셋 전처리
dataset = dataset_dict.map(preprocess_images, batched=True, remove_columns=['image'])

# 모델 설정
model = ViTForImageClassification.from_pretrained(
    'google/vit-base-patch16-224',
    num_labels=3
)

# 학습 설정
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=10,
    save_steps=10_000,
    save_total_limit=2,
    remove_unused_columns=False,
)

# Trainer 설정
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['validation'],
)

# 모델 학습
trainer.train()

# 학습된 모델 저장
model.save_pretrained('./fine_tuned_vit_model')

# 모델 평가
trainer.evaluate()

# 예측 함수 정의
def predict(image_path):
    image = Image.open(image_path)
    inputs = feature_extractor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()
    return model.config.id2label[predicted_class_idx]

# 테스트 이미지 예측
test_image_path = 'test/test1.jpg'  # 예측하려는 이미지 경로 설정
prediction = predict(test_image_path)
print(f'The image is classified as: {prediction}')
