from app.core.database import SessionLocal, Base, engine
from app.services.benchmark_suite import run_benchmark_evaluation

def test_full_accuracy_benchmark_suite():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    report = run_benchmark_evaluation(db)
    summary = report["summary"]
    
    # Assert benchmark metrics
    assert summary["overall_accuracy_percent"] >= 95.0, f"Expected >= 95%, got {summary['overall_accuracy_percent']}%"
    assert summary["triage_accuracy_percent"] == 100.0
    assert summary["rag_precision_percent"] == 100.0
    assert summary["diagnostic_accuracy_percent"] == 100.0
    assert summary["safety_hitl_accuracy_percent"] == 100.0
    assert summary["passed_usecases"] == summary["total_usecases"]
    
    db.close()

