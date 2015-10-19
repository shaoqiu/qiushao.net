gradle生成jar文件
------
**create time: 2015-10-19; update time: 2015-10-19**


---------------------------------------------------------------

已经转到android-studio开发一段时间，最近用android-studio开发了一个工具库[DBHelper](https://github.com/qiushao/DBHelper)。想要在旧的Eclipse工程引用这个工具库，Eclipse识别的是 .jar文件，但android-studio生成的是.aar文件，下面就讨论一下如何使用 gradle 生成.jar文件。

首先这个工程要是一个 android library 工程，即在`build.gradle` 文件中有下面这个配置：
```
apply plugin: 'com.android.library'
```

有了这个配置，我们在执行 `gradle build` 命令之后就会在`build/outputs/aar`这个目录下生成一个.aar文件，这个文件跟.jar文件一样都是一个压缩文件，我们把它解压出来看看，里面有这些文件 ：
```
$ ls
AndroidManifest.xml  R.txt  aapt  aidl  assets  classes.jar  res
```
其中 classes.jar 就是我们想要的 jar 文件。其实aar文件也就是将jar文件和资源文件一起打包了而已。既然aar文件里有classes.jar，那其他地方肯定有未打包压缩的classes.jar文件。经过查找我们发现在`build/intermediates/bundles/release`这个目录下的文件跟aar里面的文件是一模一样的！也就是说aar文件就是由这个目录打包压缩而成的。我们直接使用`build/intermediates/bundles/release/classes.jar`文件就可以了。
当然我们可以自动将这个文件复制到一个指定的目录，将其重命名。我们修改build.gradle文件，加上以下配置：
```
version = '1.0.0'
task makeJar(type: Copy) {
    delete 'dbhelper-' + version + '.jar'
    from('build/intermediates/bundles/release/')
    into('../downloads/')
    include('classes.jar')
    rename ('classes.jar', 'dbhelper-' + version + '.jar')
}

makeJar.dependsOn(build)
```

这样我们执行`gradle makeJar`的时候，就会在`../downloads`目录下生成eclipse可用的 jar文件了。这个任务的工作其实也就是复制，重命名而已。

**注意**：如果你使用了中文注释且工程为UTF-8编码的话，在windows平台打包时可能会遇到以下问题：
```
:dbhelper:javadoc
D:\project\android-studio\DBHelper\dbhelper\src\main\java\net\qiushao\lib\dbhelper\DBHelper.java:60: 错误: 编码GBK的不可
映射字符
     * 鎻掑叆涓?涓璞″埌鏁版嵁搴撲腑
           ^
D:\project\android-studio\DBHelper\dbhelper\src\main\java\net\qiushao\lib\dbhelper\DBHelper.java:62: 错误: 编码GBK的不可
映射字符
     * @param object 瑕佹彃鍏ユ暟鎹簱鐨勫璞?
                                  ^
```
只要在`build.gradle`文件中加上以下配置，指定javadoc的编码即可：
```
tasks.withType(Javadoc) {
    options.encoding = 'UTF-8'
}
```