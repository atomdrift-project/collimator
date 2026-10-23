#!/usr/bin/env python3
"""Python entry-point wrapper used only by the isolated profiling make target."""

from pathlib import Path
import runpy
import sys

from collimator.profiling import profile


def main():
    args = sys.argv[1:]
    while args and args[0] in ("-u", "-B"):
        args.pop(0)
    if not args:
        raise SystemExit("profile_python requires a script, -m module, or -c code")
    if args[0] in ("-m", "-c"):
        mode, target, *tail = args
    else:
        mode, target, *tail = "script", *args
    label = "command" if mode == "-c" else Path(target).stem.replace(".", "-")
    with profile(label):
        sys.argv = [target if mode != "-c" else "-c", *tail]
        if mode == "-m":
            runpy.run_module(target, run_name="__main__", alter_sys=True)
        elif mode == "-c":
            exec(compile(target, "<string>", "exec"), {"__name__": "__main__"})
        else:
            sys.path[0] = str(Path(target).resolve().parent)
            runpy.run_path(target, run_name="__main__")


if __name__ == "__main__":
    main()
