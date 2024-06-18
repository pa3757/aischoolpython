from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Post 모델 정의 (게시글을 나타내는 테이블)
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)

Base.metadata.create_all(bind=engine)

# 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모든 게시글을 가져오는 엔드포인트
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

# 새로운 게시글을 추가하는 엔드포인트
@app.post("/posts")
def add_post(title: str, content: str, db: Session = Depends(get_db)):
    new_post = Post(title=title, content=content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# 기존 게시글을 수정하는 엔드포인트
@app.put("/posts/{post_id}")
def update_post(post_id: int, title: str, content: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = title
    post.content = content
    db.commit()
    db.refresh(post)
    return post

# 기존 게시글을 삭제하는 엔드포인트
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}

# 애플리케이션 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
