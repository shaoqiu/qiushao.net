grep
------
**create time: 2015-06-28; update time: 2015-07-09**

---------------------------------------------------------------

###过滤多个模式
```
#找出文件（filename）中包含123或者包含abc的行
grep -E '123|abc' filename 
```

需要加上 `-E` 选项用以支持扩展正则表达式。
因为标准的正则表达式不支持 `|` 语法。
或者同样的功能可以使用awk实现:
```
awk '/123|abc/' filename
```

###打印匹配行及前后N行
```
grep -5 'parttern' inputfile #打印匹配行的前后5行
grep -C 5 'parttern' inputfile #打印匹配行的前后5行
grep -A 5 'parttern' inputfile #打印匹配行的后5行
grep -B 5 'parttern' inputfile #打印匹配行的前5行
```