"""Run the HFSS_TASK.md test list through hfss_patch.py, one design after another.

  python sim/hfss_batch.py --project-dir C:\\hfss_work            # everything not yet done
  python sim/hfss_batch.py --only T1 T2                           # some test groups
  python sim/hfss_batch.py --commit                               # git-commit each result as it lands

A run is skipped if its results folder already has summary.json. A failing run is tried up
to three times, then recorded in results_hfss/_failed.txt and the batch moves on.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PTFE = "--er 2.55 --tand 0.0018"
BEST = f"--board B --L 37.52 --feed 7.00 --cut 3.50 {PTFE} --Gm 100"
BEST_NO_ER = "--board B --L 37.52 --feed 7.00 --cut 3.50 --tand 0.0018 --Gm 100"

# (group, results folder name, hfss_patch.py arguments)
RUNS = [
    ("T0", "plain_L31.40_f5.80_er3.66_h1.52", "--board plain"),
    ("T0", "A_L31.40_f5.80_er3.66_h1.52", "--board A"),
    ("T1", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100", BEST),
    ("T3", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_sma", f"{BEST} --sma --tag sma"),
    ("T3", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mask", f"{BEST} --mask --tag mask"),
    ("T3", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_box", f"{BEST} --box --tag box"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_fine", f"{BEST} --delta-s 0.005 --tag fine"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_vfine", f"{BEST} --delta-s 0.002 --passes 30 --tag vfine"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.52_h1.52_Gm100", f"{BEST_NO_ER} --er 2.52"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.58_h1.52_Gm100", f"{BEST_NO_ER} --er 2.58"),
    ("T2", "B_L37.22_f7.00_c3.50_er2.55_h1.52_Gm100", f"--board B --L 37.22 --feed 7.00 --cut 3.50 {PTFE} --Gm 100"),
    ("T2", "B_L37.82_f7.00_c3.50_er2.55_h1.52_Gm100", f"--board B --L 37.82 --feed 7.00 --cut 3.50 {PTFE} --Gm 100"),
    ("T2", "B_L37.56_f7.00_c3.80_er2.55_h1.52", f"--board B --L 37.56 --feed 7.00 --cut 3.80 {PTFE}"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_pec", f"{BEST} --pec --tag pec"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.54_h1.52_Gm100_er2.542", f"{BEST_NO_ER} --er 2.542 --tag er2.542"),
    ("T2", "B_L37.52_f7.00_c3.50_er2.56_h1.52_Gm100_er2.558", f"{BEST_NO_ER} --er 2.558 --tag er2.558"),
    ("T4", "A_L31.40_f5.80_er3.66_h1.52_Gm100", "--board A --Gm 100"),
    ("T4", "B_L31.54_f5.90_c3.13_er3.66_h1.52", "--board B --L 31.54 --feed 5.90 --cut 3.13"),
    ("T4", "B_L31.54_f5.90_c3.13_er3.66_h1.52_Gm100", "--board B --L 31.54 --feed 5.90 --cut 3.13 --Gm 100"),
    ("T4", "A_L37.38_f6.90_er2.55_h1.52", f"--board A --L 37.38 --feed 6.90 {PTFE}"),
    ("T4", "A_L37.38_f6.90_er2.55_h1.52_Gm100", f"--board A --L 37.38 --feed 6.90 {PTFE} --Gm 100"),
    ("T4", "B_L37.56_f7.00_c3.80_er2.55_h1.52_Gm100", f"--board B --L 37.56 --feed 7.00 --cut 3.80 {PTFE} --Gm 100"),
    ("T5", "plain_L30.66_f5.70_er3.66_h3.05", "--board plain --h 3.048 --L 30.66 --feed 5.70"),
    ("T5", "plain_L30.66_f5.70_er3.66_h3.05_Gm100", "--board plain --h 3.048 --L 30.66 --feed 5.70 --Gm 100"),
    ("T5", "plain_L36.44_f6.70_er2.55_h3.05", f"--board plain --h 3.048 --L 36.44 --feed 6.70 {PTFE}"),
    ("T5", "plain_L36.44_f6.70_er2.55_h3.05_Gm100", f"--board plain --h 3.048 --L 36.44 --feed 6.70 {PTFE} --Gm 100"),
]


def aedt_pids():
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    pids = set()
    for ln in out.splitlines():
        cols = [c.strip('"') for c in ln.split('","')]
        if len(cols) > 1 and cols[0].lower() in ("ansysedtsv.exe", "ansysedt.exe", "hf3d.exe"):
            pids.add(cols[1])
    return pids


KEEP = aedt_pids()   # AEDT windows that were already open (the user's own): never touch these


def kill_aedt():
    """After a failed run, stop the AEDT processes this batch started."""
    for pid in aedt_pids() - KEEP:
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", default=os.path.join(HERE, "hfss_projects"))
    ap.add_argument("--only", nargs="*", help="test groups (T0..T5) or folder names")
    ap.add_argument("--extra", default="", help="extra hfss_patch.py arguments for every run")
    ap.add_argument("--mesh", type=int, default=0,
                    help="rerun with a fixed mesh size (--target-tets), e.g. 40000; folders get a _mesh40k suffix")
    ap.add_argument("--commit", action="store_true", help="git add + commit each result")
    ap.add_argument("--timeout", type=float, default=25, help="minutes per attempt")
    a = ap.parse_args()

    out = os.path.join(HERE, "results_hfss")
    logs = os.path.join(a.project_dir, "logs")
    os.makedirs(logs, exist_ok=True)
    os.makedirs(out, exist_ok=True)
    for group, name, args in RUNS:
        if a.only and group not in a.only and name not in a.only:
            continue
        if a.mesh:
            if "--delta-s" in args:   # the mesh-convergence runs themselves
                continue
            name += f"_mesh{a.mesh // 1000}k"
            args += f" --target-tets {a.mesh}"
        if os.path.exists(os.path.join(out, name, "summary.json")):
            print(f"[skip] {name}", flush=True)
            continue
        done = False
        for attempt in (1, 2, 3):
            print(f"[{time.strftime('%H:%M:%S')}] {group} {name} attempt {attempt}", flush=True)
            cmd = [sys.executable, os.path.join(HERE, "hfss_patch.py"), "--project-dir", a.project_dir]
            cmd += args.split() + a.extra.split()
            log = os.path.join(logs, f"{name}_try{attempt}.log")
            with open(log, "w") as fh:
                proc = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT)
                t0 = time.time()
                while True:
                    try:
                        rc = proc.wait(timeout=20)
                        break
                    except subprocess.TimeoutExpired:
                        pass
                    # watchdog: AEDT sometimes hangs at "Solving" with no solver process. A healthy run
                    # either writes to its log or has hf3d.exe running.
                    quiet = time.time() - os.path.getmtime(log)
                    solver = "hf3d.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
                    if time.time() - t0 > a.timeout * 60 or (quiet > 240 and not solver):
                        rc = "hung" if quiet > 240 else "timeout"
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
                        break
            if rc == 0 and os.path.exists(os.path.join(out, name, "summary.json")):
                done = True
                break
            print(f"   failed ({rc}); see {log}", flush=True)
            kill_aedt()
            time.sleep(60)   # give a transient system problem time to clear
        if not done:
            with open(os.path.join(out, "_failed.txt"), "a") as fh:
                fh.write(f"{name}: failed three times ({args})\n")
            continue
        print(open(os.path.join(out, name, "summary.txt")).read(), flush=True)
        # keep the (small) project file next to the results; the solver cache stays in --project-dir
        src = os.path.join(a.project_dir, name.replace(".", "p") + ".aedt")
        keep = os.path.join(HERE, "hfss_projects")
        if os.path.exists(src) and os.path.abspath(a.project_dir) != os.path.abspath(keep):
            os.makedirs(keep, exist_ok=True)
            shutil.copy2(src, keep)
        if a.commit:
            subprocess.run(["git", "add", os.path.join(out, name), keep], cwd=HERE, capture_output=True)
            subprocess.run(["git", "commit", "-q", "-m", f"HFSS result: {name}\n\n"
                            "Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>"], cwd=HERE, capture_output=True)
    print("batch finished", flush=True)


if __name__ == "__main__":
    main()
