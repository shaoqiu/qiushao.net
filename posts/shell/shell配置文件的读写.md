shell配置文件的读写
------
**create time: 2015-07-13; update time: 2015-07-13**

---------------------------------------------------------------

今天跟同事探讨了一下 shell 脚本中对配置文件的读写问题。在此总结一下常用的配置文件的读写方式。

大多数的配置文件都是以`key=value`形式存在的。配置项完全由键值对组成。这样的配置文件读写也是最简单的，假如有以下配置文件`user.conf`：
```
id=1
name=shaoqiu
phone=1234567890
```
配置的读取很简单，只要将其**source**进来即可：
```
shaoqiu@shaoqiu-HP440:~/project/shell$ cat setup.sh 
#!/bin/bash

source user.conf
echo "id = $id"
echo "name = $name"
echo "phone = $phone"

shaoqiu@shaoqiu-HP440:~/project/shell$ ./setup.sh 
id = 1
name = shaoqiu
phone = 1234567890
shaoqiu@shaoqiu-HP440:~/project/shell$ 
```

但这样可能会有问题，要求`=`两边不能有空格，万一用户不小心多加了空白符呢。为防止这样的情况出现，还是换另一种写法比较安全：
```
shaoqiu@shaoqiu-HP440:~/project/shell$ cat user.conf 
id=1
name=shaoqiu
phone=1234567890

shaoqiu@shaoqiu-HP440:~/project/shell$ cat setup.sh 
#!/bin/bash

function get_config() {
    local configPath=$1
    local configName=$2
    sed -n 's/^[[:space:]]*'$configName'[[:space:]]*=[[:space:]]*\(.*[^[:space:]]\)\([[:space:]]*\)$/\1/p' $configPath
}

function set_config() {
    local configPath=$1
    local configName=$2
    local confgValue=$3
    sed -i 's/^[[:space:]]*'$configName'[[:space:]]*=.*/'$configName'='$confgValue'/g' $configPath
}

get_config user.conf name
set_config user.conf name qiushao
get_config user.conf name
shaoqiu@shaoqiu-HP440:~/project/shell$ ./setup.sh 
shaoqiu
qiushao
shaoqiu@shaoqiu-HP440:~/project/shell$ cat user.conf 
id=1
name=qiushao
phone=1234567890

shaoqiu@shaoqiu-HP440:~/project/shell$ 
```

假如配置文件是由多个 **section** 组成的呢，就像下面这样：
```
[id=1]
name=shaoqiu
phone=1234567890

[id=2]
name=shaojiang
phone=5678901234

[id=3]
name=zhaotong
phone=8901234567
```
需要根据输入的`id`来读写相应的配置项。这样就不能简单的使用前面介绍的方法了。遇到这种情况，可以使用下面这种方法，将配置文件拆分成多个，分别存放到不同的目录中：
```
config
	-id1
		-user.conf
	-id2
		-user.conf
	-id3
		-user.conf
```
根据`id`读取不同目录下的配置文件即可。如果配置信息很多的话，推荐使用这种方法，目前在82平台上的机型配置就是使用这种方法来实现的。但若是配置信息很少，且可能有其他脚本也使用到了这个配置文件的时候，拆分配置文件可能就行不通了，需要寻找其他方法。要读写这种格式的配置文件比较复杂，下面是我使用的方法：
```
shaoqiu@shaoqiu-HP440:~/project/shell$ cat user.conf 
[id=1]
name=shaoqiu
phone=1234567890

[id=2]
name=shaojiang
phone=5678901234

[id=3]
name=zhaotong
phone=8901234567

shaoqiu@shaoqiu-HP440:~/project/shell$ cat setup.sh 
#!/bin/bash

function string_trim()
{
    echo "$1" | sed 's/^[[:space:]]*\(.*[^[:space:]]\)\([[:space:]]*\)$/\1/g'
}

function get_region() {
    local configPath=$1
    local userID=$2
    cat -n $configPath | grep "\\[id=.*\\]" | grep -A 1 "\\[id=$userID\\]" | awk '{print $1}' | xargs
}

function get_config() {
    local configPath=$1
    local userID=$2
    local configName=$3

    local region=$(get_region $configPath $userID)
    local startLine=$(echo $region | awk '{print $1}')
    local endLine=$(echo $region | awk '{print $2}')
    string_trim $(sed -n "${startLine}, ${endLine} s/\(${configName}.*=.*\)/\1/p" $configPath | awk -F= '{print $2}')
}

function set_config() {
    local configPath=$1
    local userID=$2
    local configName=$3
    local confgValue=$4

    local region=$(get_region $configPath $userID)
    local startLine=$(echo $region | awk '{print $1}')
    local endLine=$(echo $region | awk '{print $2}')
    sed -i "${startLine}, ${endLine} s/${configName}.*=.*/${configName}=${confgValue}/g" $configPath
}

get_config user.conf 2 name
set_config user.conf 2 name qiushao
get_config user.conf 2 name
shaoqiu@shaoqiu-HP440:~/project/shell$ ./setup.sh 
shaojiang
qiushao
shaoqiu@shaoqiu-HP440:~/project/shell$ 
```
这种方法的思想是先找出指定`id`的配置所在的区域，即从哪行开始，到哪行结束。只要找到这个区间就好办了，因为`sed`可以指定只处理的区间。获取区间的方法解释如下：
```
cat -n $configPath #给每一行加上行号
| grep "\\[id=.*\\]" #打印所有的`id`配置行
| grep -A 1 "\\[id=$userID\\]" #打印匹配的ID行，及下一行，下一行即为下一个配置section的起始行
| awk '{print $1}' | xargs #提取两个行号，即所需section的起始行和下一个配置section的起始行。
```

这种方法当时也是突发其想，想出来的。现在回头看看，其实使用倒推法应该不难想出这种方法。即最后应该是使用`sed`处理指定区间的文本。那前提就是需要找出section的区间了。而区间也就是两个行号，自然想到要`cat -n`了。