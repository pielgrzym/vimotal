
function! GetPivotalGroup(name, group)
python << EOF
import vim, sys, os
vimotal_file = vim.eval('pathogen#runtime_findfile("vimotal.vim", 0)')
sys.path.append(os.path.dirname(vimotal_file))
from vimotal import pivotal

name = vim.eval("a:name")
group = vim.eval("a:group")
project = pivotal.projects[name]
if group == 'current':
        iterations = project.current
elif group == 'backlog':
        iterations = project.backlog
elif group == 'icebox':
        iterations = project.icebox
else:
        raise ValueError("No such group")
vim.current.buffer[:] = [ a.encode('utf-8') for a in iterations.split('\n')]
EOF
endfunction

function! PivotalPrepareBuffer()
setlocal buftype=nofile
setlocal bufhidden=hide
setlocal nobuflisted
setlocal noswapfile
setlocal syntax=vimotal
endfunction

function! OpenPivotalProject(name)
exec 'tabnew pivotal_'.a:name.'_icebox'
call PivotalPrepareBuffer()
call GetPivotalGroup(a:name, "icebox")

exec 'vs pivotal_'.a:name.'_backlog'
call PivotalPrepareBuffer()
call GetPivotalGroup(a:name, "backlog")

exec 'vs pivotal_'.a:name.'_current'
call PivotalPrepareBuffer()
call GetPivotalGroup(a:name, "current")
endfunction
