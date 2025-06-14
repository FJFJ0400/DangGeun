from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import os, shutil, datetime
import models, database, schemas
import re
import traceback

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

@app.post("/group/create")
def create_group(name: str, db: Session = Depends(database.get_db)):
    group = db.query(models.StudyGroup).filter_by(name=name).first()
    if group:
        return {"group_id": group.id, "name": group.name}
    group = models.StudyGroup(name=name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return {"group_id": group.id, "name": group.name}

@app.get("/group/list")
def list_groups(db: Session = Depends(database.get_db)):
    groups = db.query(models.StudyGroup).all()
    return [{"group_id": g.id, "name": g.name} for g in groups]

@app.post("/upload")
def upload_study_log(
    request: Request,
    group_id: int = Form(...),
    image: UploadFile = File(...),
    comment: str = Form(...),
    db: Session = Depends(database.get_db)
):
    ip = request.client.host
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', image.filename)
        filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/static/uploads/{filename}"
        log = models.StudyLog(group_id=group_id, user_id=ip, image_url=image_url, comment=comment)
        db.add(log)
        db.commit()
        db.refresh(log)
        # 통계 갱신 (group_id별)
        stat = db.query(models.StudyStat).filter_by(group_id=group_id, user_id=ip).first()
        now = datetime.datetime.now().date()
        if not stat:
            stat = models.StudyStat(group_id=group_id, user_id=ip, total_logs=1, total_likes=0, streak_days=1, last_log_date=now)
            db.add(stat)
        else:
            stat.total_logs += 1
            last_log_date = stat.last_log_date
            if last_log_date is not None:
                if isinstance(last_log_date, datetime.datetime):
                    last_log_date = last_log_date.date()
                days_diff = (now - last_log_date).days
                if days_diff == 1:
                    stat.streak_days += 1
                elif days_diff > 1:
                    stat.streak_days = 1
            else:
                stat.streak_days = 1
            stat.last_log_date = now
        db.commit()
        return {"status": "success", "log_id": log.id, "image_url": image_url}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"업로드 실패: {e}")

@app.get("/feed")
def get_feed(group_id: int, sort: Optional[str] = "recent", db: Session = Depends(database.get_db)):
    logs = db.query(models.StudyLog).filter_by(group_id=group_id).order_by(models.StudyLog.created_at.desc()).all()
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
def get_stats(ip: str, group_id: int, db: Session = Depends(database.get_db)):
    stat = db.query(models.StudyStat).filter_by(group_id=group_id, user_id=ip).first()
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
    group_id: int = Form(...),
    set_seconds: int = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    db: Session = Depends(database.get_db)
):
    ip = request.client.host
    start_dt = datetime.datetime.fromisoformat(start_time)
    end_dt = datetime.datetime.fromisoformat(end_time)
    log = models.TimerLog(group_id=group_id, user_id=ip, set_seconds=set_seconds, start_time=start_dt, end_time=end_dt)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"status": "success", "log_id": log.id}

@app.get("/timerlog/feed")
def get_timer_log_feed(request: Request, group_id: int, db: Session = Depends(database.get_db)):
    ip = request.client.host
    logs = db.query(models.TimerLog).filter_by(group_id=group_id, user_id=ip).order_by(models.TimerLog.created_at.desc()).all()
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