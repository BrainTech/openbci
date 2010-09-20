import subprocess
import re


def running_screens(screen_names):
    alive_names = set()
    my_sessions_re = re.compile(
            ".*(%s)" %
                "|".join(["\." + x + "\t"
                    for x in map(re.escape, screen_names)]))
    sessions = subprocess.Popen(['screen', '-ls'], stdout=subprocess.PIPE) \
            .communicate()[0].split("\n")
    if len(sessions) < 5:
        return []
    sessions = sessions[1:-3]
    for sessinfo in sessions:
        match = my_sessions_re.match(sessinfo)
        if match:
            alive_names.add(match.group(1)[1:-1])
    return list(alive_names)

def close_screen(screen_name):
    subprocess.Popen(['screen', '-x', screen_name, '-X', 'quit']).wait()

def start_screen(screen_name, cmd, cwd=None, env={}, bash_debug=True, bash_after=True, date_at_the_beginning=True):
    if bash_after:
        cmd += " ; date ; exec bash -i"
    if date_at_the_beginning:
        cmd = 'date ; ' + cmd
    if not cwd:
        cwd = None
    subprocess.Popen(
            ['screen', '-S', screen_name, '-d', '-m', 'bash', '-xc' if bash_debug else '-x', cmd],
            env=env, cwd=cwd
            ).wait()

