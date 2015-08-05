android常用布局
------
**create time: 2015-08-04; update time: 2015-08-05**

---------------------------------------------------------------

### 1. 布局管理器
在android中我们通常是不会直接指定视图的具体位置的，我们只是指定视图的大小，相对位置，及一些布局规则，具体位置的安排就交给布局管理器去操心了。其他UI框架也基本上都是使用这种布局管理器来控制视图的摆放位置的。布局管理器，我们也可以称其为容器。

android 提供了下面这几种布局管理器：
- LinearLayout ：线性布局，可设置为水平或垂直方向排列。将视图在容器中一个接一个按指定的方向线性排列。线性布局不会自动换行，如果视图一个一个排列到尽头之后, 剩下的视图就不会显示出来。
- RelativeLayout ：相对布局，视图的位置总是相对兄弟视图，和父容器来决定的。
- FrameLayout：帧布局，这个布局管理器比较简单，所有添加到这个布局中的视图都以层叠的方式显示。第一个添加的控件被放在最底层，最后一个添加到框架布局中的视图显示在最顶层，上一层的视图会覆盖下一层的视图。这种显示方式有些类似于堆栈。
- GridLayout：网络布局，将子视图以网格的形式排布，其实跟线性布局有点相似，区别在于GridLayout会自动换行，且将子视图按网格对齐。
- TableLayout：表格布局，功能跟GridLayout相似，无论其效率还是易用性都不如GridLayout，不推荐使用。
- AbsoluteLayout ：绝对布局，使用绝对坐标来定位控件。这种方式不能适配各种各样的屏幕，不好维护，不推荐使用。

这几种布局管理器的继承关系如下图：
<br/>
![layout 继承关系图](http://i3.tietuku.com/48adb7920c694be6.png)
<br/>

可见所有的布局管理器都直接或间接地继承了 ViewGroup 类。而 ViewGroup 又继承了 View 类，所以布局管理器本身也可以作为视图添加到其他布局管理器中，以形成复杂的嵌套布局。
下面详细说明几个常用布局管理器的使用方法及注意事项。

### 2. LinearLayout
#### 2.1. 相关属性
- baselineAligned ：设置文字的基准线对齐，什么是基准线呢？这个在中文中不常见，但在以字母为书写语言的其他国家非常常见。看下图即可明白：
<br/>
![](http://i1.tietuku.com/1b8ff2b0c71d5de7.png)
<br/>
其实就是我们英文作业本上的四线中的第三条线是一个道理。设置这个属性后，这个容器里的所有子视图的文字都会对齐到这个容器的基准线上。这个属性只对水平布局有效。
- baselineAlignedChildIndex：指当前layout是 以哪个view的基准线与其他的View进行对齐。
- gravity：指定摆放子视图的位置，可以是 left , right, bottom, top 之类的，可以同时取多个值，用`|`来连接。
- measureWithLargestChild：该属性为true的时候, 所有带权重的子元素都会具有最大子元素的最小尺寸。这个属性比较少用。
- orientation：子视图排列方向，可以是水平或者垂直
- weightSum：权重的总和，如果不设置，则为所有子视图的权重的累加值。这个属性也很少使用。

#### 2.2. 简单例子
```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="100dp"
        android:background="#abcdef"
        android:gravity="center_vertical">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:background="#ff0000"
            android:text="textview1" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:background="#00ff00"
            android:text="textview2" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:background="#0000ff"
            android:text="textview3" />
    </LinearLayout>

    <LinearLayout
        android:orientation="vertical"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:layout_marginTop="20dp"
        android:gravity="right|bottom"
        android:background="#abcdef">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:background="#ff0000"
            android:text="textview1" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:background="#00ff00"
            android:text="textview2" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:background="#0000ff"
            android:text="textview3" />
    </LinearLayout>
</LinearLayout>
```
效果如下：
<br/>
![simple linear layout](http://i3.tietuku.com/b2b582c3af84826d.png)
<br/>
布局比较简单，就不详细说明了。

#### 2.3. weight 属性
假如我想实现这样的一个标题栏：左边有一个元素固定宽度，右边也有一个元素固定宽度，中间有一个元素充满剩余的空间。该怎么实现呢？我们可以通过设置子视图的 weight 属性来解决这个问题：
```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="40dp"
    android:background="#abcdef"
    android:orientation="horizontal"
    tools:context=".MainActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:background="#ff0000"
        android:gravity="center"
        android:text="textview1" />

    <TextView
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="1"
        android:background="#00ff00"
        android:gravity="center"
        android:text="textview2" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:background="#0000ff"
        android:gravity="center"
        android:text="textview3" />
</LinearLayout>
```
layout_weight值表示该组件应该增加或减少的值占**剩余空间**的比例。需要特别说明的是`剩余空间`。即容器没有被子视图填满，那这部分未被填满的空间会按比例分配给各子视图。将所有的子视图的weight 的值累加起来，得到的值(weightSum)即是剩余空间被等比例分成的份数。每个子视图占用 weight/weightSum 的比例。

效果如下：
<br/>
![linear layout weight](http://i3.tietuku.com/4bc90a9cc47067ed.png)
<br/>

### 3. RelativeLayout
#### 3.1. 相关属性
#### 3.2. 简单例子
#### 3.3. 梅花布局

### 4. FrameLayout
#### 4.1. 相关属性
#### 4.2. 简单例子
#### 4.3. 霓虹灯

### 5. GridLayout
#### 5.1. 相关属性
#### 5.2. 简单例子