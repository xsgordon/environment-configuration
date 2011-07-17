" Show line numbers
set nu

" No wrapping
set wrap

" Keep 300 command history
set history=300

" Filetype plugins and indentation on
filetype plugin on
filetype indent on

" Automatically reload when modified externally
set autoread

" Always show the current position
set ruler

" Show matching brackets
set showmatch
set mat=2

" Turn warning bells off
set noerrorbells
set novisualbell

" Syntax highlighting
syntax enable

"set ttymouse=xterm2
"set mouse=a

" Indent based folding, particularly good for code and docbook snippets.
set foldmethod=indent

" Ensure folds are saved when leaving the buffer and loaded when entering it.
au BufWinLeave * mkview
au BufWinEnter * silent loadview

" Tab rules...
set softtabstop=4
set shiftwidth=4
set tabstop=4
set noexpandtab
set autoindent

" Support repeated block indentation
vnoremap < <gv
vnoremap > >gv


set thesaurus+=/home/sgordon/.vim/thesaurus/mthesaur.txt

if has("autocmd") && exists("+omnifunc")            
    autocmd Filetype *
    \   if &omnifunc == "" |
    \     setlocal omnifunc=syntaxcomplete#Complete |
    \   endif
endif
