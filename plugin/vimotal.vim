
function! GetPivotalGroup(name, group)
python << EOF
import vim, sys, os
vimotal_file = vim.eval('pathogen#runtime_findfile("vimotal.py", 0)')
sys.path.append(os.path.dirname(vimotal_file))
from vimotal import pivotal

name = vim.eval("a:name")
group = vim.eval("a:group")
project = pivotal.projects[name]
iterations = project.printIterations(group)
vim.current.buffer[:] = [ a.encode('utf-8') for a in iterations.split('\n')]
EOF
endfunction

function! OpenPivotalProject(name)
exec 'tabnew pivotal_'.a:name.'_current'
setlocal buftype=nofile
setlocal bufhidden=hide
setlocal nobuflisted
setlocal noswapfile
setlocal syntax=vimotal
call GetPivotalGroup(a:name, "current")
endfunction
