markdown基本语法
------
**create time: 2015-06-25; update time: 2015-07-09**

---------------------------------------------------------------

这个博客的所有文章都是使用`Markdown`语法来写的。`Markdown`是一种非常适合写文章的语法。有很多网站都支持使用`Markdown`来写文章或评论。比如[Github](http://github.com/)的仓库介绍文件`README.md`就可以用`Markdown`语法来写。[stackoverflow](http://stackoverflow.com/)也是使用`Markdown`语法来写评论，提问题的。国内的各大博客网站也都支持`Markdown`语法。比如[CSDN](http://www.csdn.net/),[oschina](http://www.oschina.net/)。

那么问题来了，使用什么工具来写`Markdown`呢。这里推荐两个在线的编辑工具[马克飞象](http://maxiang.info/)和[作业部落](https://www.zybuluo.com/mdeditor)。都是非常优秀的产品。
下面介绍一下`Markdown`的基本语法：

### 1. 标题
markdown 中有两种方法标志某一行为标题。
#### 1.1. 行首为 `#` 号
此种形式称为  **atx**  形式。`#` 的个数为1 ～ 6个，有多少个 `#` 则表示几级标题，例如：
```
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

其显示效果为：
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题

--------------------------

#### 1.2. 底线形式 ====== 和 ------ 
这种形式称为 **setext**形式。`=`表示大标题， `-`标示小标题，其个数对效果无影响，例如：
```
大标题
======
小标题
------
```

其显示效果为：
大标题
======

小标题
------

------


### 2. 引用
markdown 中可以使用 `>` 来表示一个区块引用，例如：
```
> just for today
> I will try to study
> I will learn something usefull
```

其显示效果为：
> just for today
> I will try to study
> I will learn something usefull

引用也可以进行嵌套：
```
> this is the fire level of quoting
> 
>> this is the nested blockquote
>
> back to the first level
```

其显示效果如下：

> this is the fire level of quoting
> 
>> this is the nested blockquote
>
> back to the first level


引用的区块内也可以使用其他 markdown 语法，包括标题，列表，代码块等，例如：
````
> ##这是一个标题
> ### 1.sub title 1
> ### 2.sub title 2
> 代码块
> ```
> printf("just for today") 
> ```
````

其显示效果如下：
> ## 这是一个标题
> ### 1.sub title 1
> text here
> ### 2.sub title 2
> text there
> 代码块
> ```
> printf("just for today") 
> ```

----------------

### 3. 列表
在Markdown 下，列表的显示只需要在文字前加上 `-` 或 `*` 或 `+` ，即可变为无序列表，
有序列表则直接在文字前加上 `1. ` `2. ` `3. `，编号与文字间加一个空格。
#### 3.1. 无序列表
```
* item 1
* item 2
* item 3
```
或
```
- item 1
- item 2
- item 3
``` 
或 
``` 
+ item 1
+ item 2
+ item 3
```

其显示效果是一样的：
* item  1
* item  2
* item  3

若想嵌套列表，则可以如下表示，只要子列表相对父列表项缩进一个`TAB`即可：

```
* item 1
    * sub item1
    * sub item2
* item 2
    * sub item1
    * sub item2
* item 3
    * sub item1
    * sub item2
    * sub item3
```

其显示效果如下：

* item 1
    * sub item1
    * sub item2
* item 2
    * sub item1
    * sub item2
* item 3
    * sub item1
    * sub item2
    * sub item3

----------------------

### 3.2. 有序列表
其实跟无序列表的表示方式一样，只不过把`*`换成了数字序号`1`,`2`,`3`而已
例如：
```
1. item 1
    1. sub item 1
    2. sub item 2
2. item 2
    1. sub item 1
    2. sub item 2
3. item 3
```

其显示效果如下
1. item 1
    1. sub item 1
    2. sub item 2
2. item 2
    1. sub item 1
    2. sub item 2
3. item 3

-------------------------------

### 4. 代码块
对于一个程序员来说，在写文章，作笔记时代码块几乎是少不了的，正如 Linus 所说 **talk is cheap, show me your code**。在 Markdown 中表示一个代码块非常简单，只要用反引号把代码块给包起来即可，例如：
````
```
int main(void)
{
    printf("just for today")
}
```
````

其显示效果如下：
```
int main(void)
{
    printf("just for today")
}
```


哈，那我是如何显示上面那一段markdown语法的呢？在markdown代码块外再包一层反引号，
这层反引号是连续四个，如下：
`````
````
```
int main(void)
{
    printf("just for today")
}
```
````
`````

----------------------------------------

### 5.分隔线
你可以在一行中用三个或以上的`*`,`-`,`_`来建立一条华丽的分隔线，行内不能有其他字符（空白符除外）
```
***
```
***

or 
```
---
```
---

or
```
___
```
___


### 6. 图片与连接
在Markdown中插入图片或链接的语法相似，只是插入图片语法多了一个`!`而已

插入链接： `[title](url)`:
```
[简书Markdown语法介绍](http://www.jianshu.com/p/1e402922ee32)
```
[简书Markdown语法介绍](http://www.jianshu.com/p/1e402922ee32)


插入图片： `![title](url)`：
```
![简书](http://ww2.sinaimg.cn/large/6aee7dbbgw1efffa67voyj20ix0ctq3n.jpg)
```
![简书](http://ww2.sinaimg.cn/large/6aee7dbbgw1efffa67voyj20ix0ctq3n.jpg)


不过目前Markdown语法还不支持指定图片的大小，如果需要指定大小的话，则可以使用HTML标签
```
<img src="http://ww2.sinaimg.cn/large/6aee7dbbgw1efffa67voyj20ix0ctq3n.jpg" width="128" height="128" />
```
<img src="http://ww2.sinaimg.cn/large/6aee7dbbgw1efffa67voyj20ix0ctq3n.jpg" width="128" height="128" />

---------------------------------

### 7. 强调
我们一般使用 * 斜体 * 或 ** 粗体 ** 来进行强调，在Markdown中使用`*`或`_`将需要进行强调的文字包起来即可，一个`*`表示 * 斜体 *，两个`*`表示 ** 粗体 **，例如：

```
我们一般使用 * 斜体 * 或 ** 粗体 ** 来进行强调
```

其显示效果如本文第一行


----------------------------------

### 8. 字符转义
Markdown 支持在下面这些符号前面加上反斜杠`\`来帮助插入普通的符号：
```
\   反斜杠
`   反引号
*   星号
_   底线
{}  大括号
[]  方括号
()  括号
#   井字号
+    加号
-    减号
.   英文句点
!   惊叹号
```