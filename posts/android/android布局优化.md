Android布局优化
------
**create time: 2015-08-04; update time: 2015-08-14**

---------------------------------------------------------------

android 开发中布局是最基本的，也是直接呈现给用户的。所以说布局是非常重要的。要实现一个好的布局，不只是实现了、显示出来就完事了，我们要有更高的追求，我们还要从页面加载速度，操作的流畅度，内存占用等方面去优化我们的布局。

### 1. 避免不必要的嵌套布局
过多的布局嵌套会导致布局的解析变慢，渲染速度变慢，内存的占用增加。所以我们要避免不必要的布局嵌套。下面举两个例子来说明问题。
假如需要实现下面这样的一个布局，你会怎样来实现呢？
<br/>
![setting](http://i1.tietuku.com/91ce28abdcd40b00.png)
<br/>
最开始可能会这样子实现：
```xml
    <LinearLayout
        android:gravity="center"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content">
        <ImageView
            android:src="@mipmap/setting"
            android:layout_marginRight="10dp"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
        <TextView
            android:text="设置"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content" />
    </LinearLayout>
```
为了实现这么一个小按钮，我们用了一个LinearLayout， 一个ImageView， 一个TextView！其实如果你知道TextView有个`drawableLeft`属性的话，这个布局就可以这样子来实现：
```xml
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:drawableLeft="@mipmap/setting"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="设置" />
```
效果跟上面使用LinearLayout布局嵌套的方法是一样的。但我们只使用了一个TextView！

再看另外一个例子：
<br/>
![music](http://i1.tietuku.com/3d532187e823489e.png)
<br/>
要实现这样的布局，在我没有熟悉RelativeLayout之前，我是这么实现的：
```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <RelativeLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:drawableLeft="@mipmap/back"
            android:drawablePadding="10dp"
            android:gravity="center"
            android:text="返回" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_alignParentRight="true"
            android:drawableLeft="@mipmap/setting"
            android:drawablePadding="10dp"
            android:gravity="center"
            android:text="设置" />
    </RelativeLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">
        <ImageView
            android:layout_width="100dp"
            android:layout_height="100dp"
            android:src="@mipmap/cd" />
        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="match_parent"
            android:layout_marginLeft="10dp"
            android:layout_marginTop="20dp"
            android:gravity="center"
            android:orientation="vertical">
            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="歌名" />
            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="演唱者" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
```
用了三层嵌套布局。而使用RelativeLayout作为根标签，可以改为这样子：
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="8dp"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/back"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:drawableLeft="@mipmap/back"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="返回" />

    <TextView
        android:id="@+id/setting"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignParentRight="true"
        android:drawableLeft="@mipmap/setting"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="设置" />

    <ImageView
        android:id="@+id/cd"
        android:layout_width="100dp"
        android:layout_height="100dp"
        android:layout_below="@id/back"
        android:src="@mipmap/cd" />

    <TextView
        android:id="@+id/song"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignTop="@id/cd"
        android:layout_marginLeft="10dp"
        android:layout_marginTop="30dp"
        android:layout_toRightOf="@id/cd"
        android:text="歌名" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignLeft="@id/song"
        android:layout_below="@id/song"
        android:text="演唱者" />
</RelativeLayout>
```
变成了一层嵌套布局！使用RelativeLayout相对于LinearLayout来说，能减少布局的嵌套层次。这也是在新版的IDE中，默认的布局根标签由LinearLayout变成了RelativeLayout的原因。官方推荐使用RelativeLayout。

### 2. 使用include标签
这个标签主要是为了使我们的布局文件模块化，便于维护。主要在两种情况使用
- 布局复杂：假如一个页面的布局很复杂，如果所有的的布局都写在同一个文件里面的话，那布局文件也会变得很复杂，维护起来比较吃力。这种情况下，我们可以把布局模块化。每一个模块的布局写在一个单独的布局文件里面，这样的话就比较清晰有条理。
- 布局复用：假如在多个布局文件中，存在公共的布局。那我们可以提取这部分布局到一个文件中。在需要用到公共布局的地方使用include标签导入即可。减少了布局的维护工作量

以上面的音乐播放器为例，假如页面顶部的返回，设置按钮其他页面也会使用到。那我们可以把它单独提取出来，这里我们把它提取到 `menu.xml`文件中：
```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content">

    <TextView
        android:id="@+id/back"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:drawableLeft="@mipmap/back"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="返回" />

    <TextView
        android:id="@+id/setting"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignParentRight="true"
        android:drawableLeft="@mipmap/setting"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="设置" />
</RelativeLayout>
```

Activity的布局文件可以修改为这样子：
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="8dp"
    tools:context=".MainActivity">

    <include android:id="@+id/menu" layout="@layout/menu"/>

    <ImageView
        android:id="@+id/cd"
        android:layout_width="100dp"
        android:layout_height="100dp"
        android:layout_below="@id/menu"
        android:src="@mipmap/cd" />

    <TextView
        android:id="@+id/song"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignTop="@id/cd"
        android:layout_marginLeft="10dp"
        android:layout_marginTop="30dp"
        android:layout_toRightOf="@id/cd"
        android:text="歌名" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_alignLeft="@id/song"
        android:layout_below="@id/song"
        android:text="演唱者" />
</RelativeLayout>
```
显示效果还是一样的，但布局文件看起来是不是清爽多了呢。

### 3. 使用merge标签
这里需要使用到一个工具 `hierarchyviewer`，这个工具是在Android SDK Tools 里面自带的。用来分析页面的布局情况，以便优化。我们打开 hierarchyviewer 分析一下前面使用 include 标签写的布局文件：
<br/>
![merge](http://i1.tietuku.com/8f030d25a4682117.png)
<br/>
我们发现RelativeLayout下面又直接嵌套了一层RelativeLayout，这就是由我们使用的include标签，导致的布局嵌套。针对这种情况我们可以使用merge标签来取消这一层不必要的嵌套。`menu.xml`文件修改如下：
```xml
<?xml version="1.0" encoding="utf-8"?>
<merge xmlns:android="http://schemas.android.com/apk/res/android">

    <TextView
        android:id="@+id/back"
        android:layout_width="wrap_content"
        android:layout_height="30dp"
        android:drawableLeft="@mipmap/back"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="返回" />

    <TextView
        android:id="@+id/setting"
        android:layout_width="wrap_content"
        android:layout_height="30dp"
        android:layout_alignParentRight="true"
        android:drawableLeft="@mipmap/setting"
        android:drawablePadding="10dp"
        android:gravity="center"
        android:text="设置" />
</merge>
```

Activity 的布局文件修改如下：
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="8dp"
    tools:context=".MainActivity">

    <include layout="@layout/menu"/>

    <ImageView
        android:id="@+id/cd"
        android:layout_marginTop="40dp"
        android:layout_width="100dp"
        android:layout_height="100dp"
        android:src="@mipmap/cd" />

	......
</RelativeLayout>
```
这里我们适当的作了些修改，ImageView 不再使用 layout_below 属性，而是设置了一个 layout_marginTop。显示效果是一样的，但我们再看看 hierarchyviewer ：
<br/>
![merge](http://i1.tietuku.com/62c1e8ec90a75c52.png)
<br/>
可以发现，少了一层嵌套。为了尽量减少布局的嵌套，我们也是煞费苦心啊。

### 4. 使用ViewStub延迟加载