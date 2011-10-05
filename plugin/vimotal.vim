let g:vimotal_path = expand("<sfile>:p:h")

function! GetPivotalGroup(name, group)
python << EOF
import vim, sys, os
vimotal_dir = vim.eval('g:vimotal_path')
vimotal_module = os.path.join(vimotal_dir, 'vimotal')
sys.path.append(os.path.dirname(vimotal_module))
# vimotal_file = vim.eval('pathogen#runtime_findfile("vimotal.py", 0)')
# sys.path.append(os.path.dirname(vimotal_file))
# vim.current.buffer[:] = [vimotal_module]
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

function! PivotalPrepareBuffer(name)
        setlocal buftype=nofile
        setlocal bufhidden=hide
        setlocal nobuflisted
        setlocal noswapfile
        setlocal syntax=vimotal
        nmap q :call ClosePivotal()<CR>
endfunction

function! ClosePivotal()
        silent windo setlocal bufhidden=wipe
        let moveLeft = tabpagenr() == tabpagenr('$') ? 0 : 1
        tabc
        if moveLeft && tabpagenr() != 1
            tabp
        endif
endfunction

function! OpenPivotalProject(name)
        exec 'tabnew pivotal_'.a:name.'_icebox'
        call PivotalPrepareBuffer(a:name)
        call GetPivotalGroup(a:name, "icebox")

        exec 'vs pivotal_'.a:name.'_backlog'
        call PivotalPrepareBuffer(a:name)
        call GetPivotalGroup(a:name, "backlog")

        exec 'vs pivotal_'.a:name.'_current'
        call PivotalPrepareBuffer(a:name)
        call GetPivotalGroup(a:name, "current")
endfunction

function! InvokeVimotal()
        call inputsave()
        let project_name = input('Enter project name: ')
        call inputrestore()
        silent call OpenPivotalProject(project_name)
endfunction

nmap <Leader>p :call InvokeVimotal()<CR>
