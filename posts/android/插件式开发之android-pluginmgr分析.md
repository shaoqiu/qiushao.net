android 插件式开发之`Android PluginManager`分析
------
**create time: 2015-07-13; update time: 2015-07-13**

---------------------------------------------------------------

最近在研究 android 插件化开发框架，发现了一个开发框架[Android PluginManager](https://github.com/houkx/android-pluginmgr/)比较有意思。这个框架的思想很特别，与其他的插件框架背道而行。其他的框架都是提供一个 lib ，lib 里面提供了一些基本组件，然后要求插件去继承这些组件，还要遵守一些开发规范。但`Android PluginManager`这个框架却对插件不做任何要求（其实目前还是有要求的，暂时还不支持在插件中使用 service）。看了作者的介绍，框架使用的是依赖倒置的思想（我猜作者是由J2EE转android的。。。），在运行时动态生成一个类，让这个类去继承插件的入口类。这个动态生成的类是在宿主程序中已经注册过的了。这个框架使用了[dexmaker](https://github.com/crittercism/dexmaker)来动态生成 dex 文件。下面详细分析一下这个框架。

未完待续