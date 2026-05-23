from run_model import RunHistory


# 저장
def create_run_history(db, data):

    history = RunHistory(
        user_id=data.user_id,
        pace=data.pace,
        heart_rate=data.heart_rate,
        cadence=data.cadence,
    )

    db.add(history)

    db.commit()

    db.refresh(history)

    return history


# 전체 조회
def get_run_histories(db):

    return db.query(RunHistory).all()