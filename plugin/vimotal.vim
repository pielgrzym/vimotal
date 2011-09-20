pyfile /home/pielgrzym/.vim/bundle/vimotal/vimotal.py
function! GetPivotalGroup(name, group)
python << EOF
import vim, sys, os
scriptdir = "/home/pielgrzym/.vim/bundle/vimotal"
sys.path.append(scriptdir)

name = vim.eval("a:name")
group = vim.eval("a:group")
pivotal = Pivotal()
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
call GetPivotalGroup(a:name, "current")
endfunction
