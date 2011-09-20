" Vim syntax file
" Language:     Pivotal tracker output
" Maintainer:   Jakub Nawalaniec <pielgrzym@prymityw.pl>
" Last Change: 2011-09-20
"

if exists("b:current_syntax")
    finish
endif

syn match vimotalIteration /^◆\d | .*/
syn region vimotalStoryAccepted start=/^\./ end="$" contains=vimotalStory,vimotalStoryBug,vimotalStoryChore
syn region vimotalStoryUnstarted start=/^\,/ end="$" contains=vimotalStory,vimotalStoryBug,vimotalStoryChore
syn region vimotalStoryStarted start="_" end="$" contains=vimotalStory,vimotalStoryBug,vimotalStoryChore
syn match vimotalStory /★ /
syn match vimotalStoryBug /✗ /
syn match vimotalStoryChore /◎ /

highlight default vimotalIteration      ctermbg=grey ctermfg=black   guibg=Grey guifg=black
highlight default vimotalStoryAccepted  ctermfg=green   guifg=DarkGreen
highlight default vimotalStoryUnstarted  ctermfg=grey   guifg=LightBlue
highlight default vimotalStoryStarted  ctermfg=yellow   guifg=Yellow
highlight default vimotalStory          ctermfg=yellow  guifg=yellow1
highlight default vimotalStoryBug       ctermfg=red     guifg=red
highlight default vimotalStoryChore     ctermfg=blue    guifg=LightBlue

