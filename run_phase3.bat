@echo off
cd /d C:\Users\Administrator\Desktop\aettl-research
set PYTHONUNBUFFERED=1
python -u mm_epc_phase3_significance.py > experiments\phase3_v4.log 2>&1
echo DONE > experiments\phase3_done.txt