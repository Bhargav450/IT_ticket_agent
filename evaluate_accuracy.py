#!/usr/bin/env python3
"""
Autonomous IT Support Agent - Comprehensive Accuracy & Benchmark Evaluation Suite
Evaluates Triage accuracy, RAG precision, Diagnostic accuracy, and HITL safety across all use cases.
"""

import sys
import os

# Auto-switch to virtualenv if not already active
venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv/bin/python"))
if os.path.exists(venv_python) and sys.executable != venv_python:
    os.execl(venv_python, venv_python, *sys.argv)

# Ensure backend is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal, Base, engine
from app.services.benchmark_suite import run_benchmark_evaluation

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print("\n" + "="*80)
    print_colored("  🛡️  AEGISOPS AUTONOMOUS IT SUPPORT AGENT - ACCURACY BENCHMARK SUITE", "1;36")
    print("="*80)
    print("  Evaluating all operational scenarios against ground truth specifications...\n")

    report = run_benchmark_evaluation(db)
    summary = report["summary"]
    results = report["usecase_results"]

    # Print Use Cases Table
    print(f"{'ID':<7} | {'USE CASE NAME':<40} | {'TRIAGE':<8} | {'RAG':<6} | {'DIAG':<6} | {'HITL/SAFE':<9} | {'STATUS'}")
    print("-" * 95)
    
    for r in results:
        status_str = "\033[1;32mPASS\033[0m" if r["passed"] else "\033[1;31mFAIL\033[0m"
        triage_str = "OK" if r["triage"]["passed"] else "FAIL"
        rag_str = "OK" if r["rag"]["passed"] else "FAIL"
        diag_str = "OK" if r["diagnostic"]["passed"] else "FAIL"
        hitl_str = "OK" if r["safety_hitl"]["passed"] else "FAIL"
        
        print(f"{r['use_case_id']:<7} | {r['name'][:38]:<40} | {triage_str:<8} | {rag_str:<6} | {diag_str:<6} | {hitl_str:<9} | {status_str}")

    print("-" * 95)

    # Print Summary Metrics
    print("\n" + "="*80)
    print_colored("  📊 ACCURACY BENCHMARK SCORECARD", "1;33")
    print("="*80)
    
    acc = summary['overall_accuracy_percent']
    acc_color = "1;32" if acc >= 90 else "1;33"
    print_colored(f"  🏆 Overall Agent Accuracy:          {acc}% ({summary['passed_usecases']}/{summary['total_usecases']} Scenarios Fully Passed)", acc_color)
    print(f"  🎯 Triage Accuracy:                 {summary['triage_accuracy_percent']}% (Severity, Category & Service Classification)")
    print(f"  📚 RAG Retrieval Precision:         {summary['rag_precision_percent']}% (Runbook Citations & Excerpts Found)")
    print(f"  🔍 Diagnostic Precision:            {summary['diagnostic_accuracy_percent']}% (Root Cause Analysis Accuracy)")
    print(f"  🛑 Human-in-the-Loop Safety Gate:   {summary['safety_hitl_accuracy_percent']}% (Risky Actions Halted & Safe Actions Allowed)")
    print(f"  ⚡ Resolution & Verification:       {summary['resolution_success_percent']}% (Post-Remediation Synthetic Probing)")
    print(f"  ⏱️  Total Evaluation Time:           {summary['benchmark_duration_seconds']}s")
    print("="*80 + "\n")

    db.close()

if __name__ == "__main__":
    main()

