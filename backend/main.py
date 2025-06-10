from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import os, shutil, datetime
import models, database, schemas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
def upload_study_log(
    request: Request,
    image: UploadFile = File(...),
    comment: str = Form(...),
    db: Session = Depends(database.get_db)
):
    ip = request.client.host
    filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    image_url = f"/{file_path}"
    log = models.StudyLog(user_id=ip, image_url=image_url, comment=comment)
    db.add(log)
    db.commit()
    db.refresh(log)
    # 통계 갱신
    stat = db.query(models.StudyStat).filter_by(user_id=ip).first()
    now = datetime.datetime.now().date()
    if not stat:
        stat = models.StudyStat(user_id=ip, total_logs=1, total_likes=0, streak_days=1, last_log_date=now)
        db.add(stat)
    else:
        stat.total_logs += 1
        if stat.last_log_date is not None and (now - stat.last_log_date).days == 1:
            stat.streak_days += 1
        elif stat.last_log_date is None or (now - stat.last_log_date).days > 1:
            stat.streak_days = 1
        stat.last_log_date = now
    db.commit()
    return {"status": "success", "log_id": log.id}

@app.get("/feed")
def get_feed(sort: Optional[str] = "recent", db: Session = Depends(database.get_db)):
    logs = db.query(models.StudyLog).order_by(models.StudyLog.created_at.desc()).all()
    if sort == "popular":
        logs = sorted(logs, key=lambda l: len(db.query(models.Like).filter_by(study_log_id=l.id).all()), reverse=True)
    feed = []
    for log in logs:
        likes = db.query(models.Like).filter_by(study_log_id=log.id).count()
        comments = db.query(models.Comment).filter_by(study_log_id=log.id).count()
        feed.append({
            "log_id": log.id,
            "user_id": log.user_id,
            "image_url": log.image_url,
            "comment": log.comment,
            "likes": likes,
            "comments": comments,
            "created_at": log.created_at
        })
    return feed

@app.post("/like")
def like_log(user_id: int = Form(...), log_id: int = Form(...), db: Session = Depends(database.get_db)):
    # 중복 좋아요 방지
    exist = db.query(models.Like).filter_by(user_id=user_id, study_log_id=log_id).first()
    if exist:
        raise HTTPException(status_code=400, detail="이미 좋아요를 누르셨습니다.")
    like = models.Like(user_id=user_id, study_log_id=log_id)
    db.add(like)
    # 통계 갱신
    stat = db.query(models.StudyStat).filter_by(user_id=user_id).first()
    if stat:
        stat.total_likes += 1
    db.commit()
    return {"status": "liked"}

@app.post("/comment")
def add_comment(user_id: int = Form(...), log_id: int = Form(...), content: str = Form(...), db: Session = Depends(database.get_db)):
    comment = models.Comment(user_id=user_id, study_log_id=log_id, content=content)
    db.add(comment)
    db.commit()
    return {"status": "commented"}

@app.get("/stats/{ip}")
def get_stats(ip: str, db: Session = Depends(database.get_db)):
    stat = db.query(models.StudyStat).filter_by(user_id=ip).first()
    today = datetime.datetime.now().date()
    today_logged = False
    if stat and stat.last_log_date and stat.last_log_date == today:
        today_logged = True
    return {
        "total_logs": stat.total_logs if stat else 0,
        "total_likes": stat.total_likes if stat else 0,
        "streak_days": stat.streak_days if stat else 0,
        "today_logged": today_logged
    }

@app.post("/timerlog/upload")
def upload_timer_log(
    request: Request,
    set_seconds: int = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    db: Session = Depends(database.get_db)
):
    ip = request.client.host
    start_dt = datetime.datetime.fromisoformat(start_time)
    end_dt = datetime.datetime.fromisoformat(end_time)
    log = models.TimerLog(user_id=ip, set_seconds=set_seconds, start_time=start_dt, end_time=end_dt)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"status": "success", "log_id": log.id}

@app.get("/timerlog/feed")
def get_timer_log_feed(request: Request, db: Session = Depends(database.get_db)):
    ip = request.client.host
    logs = db.query(models.TimerLog).filter_by(user_id=ip).order_by(models.TimerLog.created_at.desc()).all()
    return [
        {
            "id": log.id,
            "set_seconds": log.set_seconds,
            "start_time": log.start_time.isoformat(),
            "end_time": log.end_time.isoformat() if log.end_time else None,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ] 