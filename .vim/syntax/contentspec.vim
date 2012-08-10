if exists("b.current_syntax")
  finish
endif

syntax match cspecConstant /^CHECKSUM/
syntax match cspecConstant /^ID/
syntax match cspecConstant /^Title/
syntax match cspecConstant /^Subtitle/
syntax match cspecConstant /^Description/
syntax match cspecConstant /^Product/
syntax match cspecConstant /^Version/
syntax match cspecConstant /^Edition/
syntax match cspecConstant /^DTD/
syntax match cspecConstant /^Copyright Holder/
syntax match cspecConstant /^Brand/
syntax match cspecConstant /^publican.cfg/
syntax match cspecConstant /^pubsnumber/
syntax match cspecConstant /^Debug/


syntax match cspecHeading /^[ ]*Part/
syntax match cspecHeading /^[ ]*Chapter/
syntax match cspecHeading /^[ ]*Section/
syntax match cspecHeading /^[ ]*Appendix/
syntax match cspecHeading /^[ ]*Process/

syntax match cspecSeparator /:/
syntax match cspecSeparator /=/

syntax match cspecContainer /\[/
syntax match cspecContainer /\]/

syntax match cspecComment /#.*/

syntax match cspecTabs /\t/

syntax region cspecBracketed matchgroup=cspecContainer start=/\[/ end=/\]/ contains=cspecID
syntax match cspecID /\[[PRTL:[:digit:],]\+\]/

highlight link cspecConstant    Keyword
highlight link cspecHeading     Keyword
highlight link cspecSeparator   Delimiter
highlight link cspecContainer   Delimiter
highlight link cspecComment     Comment
highlight link cspecTabs        Error
highlight link cspecID          SpecialChar

let b:current_syntax = "contentspec"
