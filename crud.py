from run_model import AICoaching
from run_schema import CoachingUpdate
from run_model import AICoachingReport


def create_ai_coaching(db, data, feedback_text: str, focus_point: str, rec_exercise: str):
    coaching = AICoaching(
        activity_id=data.activity_id,
        feedback_text=feedback_text,
        focus_point=focus_point,
        rec_exercise=rec_exercise,
    )

    db.add(coaching)
    db.commit()
    db.refresh(coaching)

    return coaching

def create_ai_coaching_report(
    db,
    activity_id: int,
    summary_title: str,
    total_coaching_count: int,
    items: list,
):
    report = AICoachingReport(
        activity_id=activity_id,
        summary_title=summary_title,
        total_coaching_count=total_coaching_count,
        items_json=items,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_ai_coaching_report_by_activity_id(db, activity_id: int):
    return (
        db.query(AICoachingReport)
        .filter(AICoachingReport.activity_id == activity_id)
        .first()
    )

def get_ai_coaching(db, coaching_id: int):
    return db.query(AICoaching).filter(AICoaching.coaching_id == coaching_id).first()


def get_ai_coachings(db, activity_id: int | None = None):
    query = db.query(AICoaching).order_by(AICoaching.coaching_id.desc())

    if activity_id is not None:
        query = query.filter(AICoaching.activity_id == activity_id)

    return query.all()


def update_ai_coaching(db, coaching: AICoaching, data: CoachingUpdate):
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(coaching, key, value)

    db.commit()
    db.refresh(coaching)

    return coaching


def delete_ai_coaching(db, coaching: AICoaching):
    db.delete(coaching)
    db.commit()