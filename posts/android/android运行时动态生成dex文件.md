android 运行时动态生成 dex 文件
------
**create time: 2015-07-13; update time: 2015-07-13**

---------------------------------------------------------------

最近在研究 android 插件化开发框架[Android PluginManager](https://github.com/houkx/android-pluginmgr/)。这个框架使用了[dexmaker](https://github.com/crittercism/dexmaker)来动态生成 dex 文件。所以先来学习一下 `dexmaker`的使用方法。需要注意的是  `dexmaker`1.3 版本，使用有问题，提示错误`java.lang.NoClassDefFoundError: com.google.dexmaker.dx.rop.type.Type`，整了大半天也不知道错哪里了，看了这个[issues](https://github.com/crittercism/dexmaker/issues/18)才知道这个版本有问题，但作者好像并没有要修改的意思。所以我使用了[Android PluginManager](https://github.com/houkx/android-pluginmgr/) Demo 的 libs 中`dexmaker-1.1.jar`文件。在继续之前，我们或许应该先了解一下[dex](http://source.android.com/devices/tech/dalvik/index.html)字节码文件的格式（需要翻墙）。

未完待续

注： 1. 所有 local 变量的声明必须在任何 statement 之前。