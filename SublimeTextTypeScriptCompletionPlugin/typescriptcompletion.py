import sublime, sublime_plugin, os, json, subprocess

# https://gist.github.com/1027906
def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    Backported from Python 2.7 as it's implemented as pure python on stdlib.

    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2
	"""

    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output

def system(command):
	startupinfo = None
	return check_output(command, startupinfo=startupinfo)

def get_completions(view, settings):
	comp = settings.get('typescript_completion_command')
	if comp is None:
		comp = 'tsc-completion'

	path = settings.get('path')
	if path is not None:
	    os.environ['PATH'] += ':' + path

	point = view.sel()[0].a
	row, col = view.rowcol(point)
	point = point + row

	command = [
		'tsc-completion', view.file_name(), str(point), '1'
	]

	try:
		ret = system(command)
		return json.loads(ret)
	except subprocess.CalledProcessError:
		return []


class TypeScriptCompletionListener(sublime_plugin.EventListener):
	def __init__(self):
		self.settings = sublime.load_settings("TypeScriptCompletion.sublime-settings");

	def on_query_completions(self, view, prefix, locations):
		if not view.file_name().endswith('.ts'):
			return []

		words = get_completions(view, self.settings)
		entries = words["entries"]
		words = [(w["name"] + " " + w["type"], w["name"]) for w in entries]

		return words
