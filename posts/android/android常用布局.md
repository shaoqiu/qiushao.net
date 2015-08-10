android常用布局
------
**create time: 2015-08-04; update time: 2015-08-10**

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
```
// 相对于给定ID控件
android:layout_above 将该控件的底部置于给定ID的控件之上;
android:layout_below 将该控件的底部置于给定ID的控件之下;
android:layout_toLeftOf 将该控件的右边缘与给定ID的控件左边缘对齐;
android:layout_toRightOf 将该控件的左边缘与给定ID的控件右边缘对齐;

android:layout_alignBaseline 将该控件的baseline与给定ID的baseline对齐;
android:layout_alignTop 将该控件的顶部边缘与给定ID的顶部边缘对齐;
android:layout_alignBottom 将该控件的底部边缘与给定ID的底部边缘对齐;
android:layout_alignLeft 将该控件的左边缘与给定ID的左边缘对齐;
android:layout_alignRight 将该控件的右边缘与给定ID的右边缘对齐;
// 相对于父组件
android:layout_alignParentTop 如果为true,将该控件的顶部与其父控件的顶部对齐;
android:layout_alignParentBottom 如果为true,将该控件的底部与其父控件的底部对齐;
android:layout_alignParentLeft 如果为true,将该控件的左部与其父控件的左部对齐;
android:layout_alignParentRight 如果为true,将该控件的右部与其父控件的右部对齐;
```
相对布局的核心思想就是对齐方式，给定一个参照物，这个参照物可以是其他兄弟视图或者父容器。我们通过属性指定视图相对于参照物的位置。其实也就是上下左右了。下面就举两个例子来看看RelativeLayout的使用方法。
#### 3.2. 梅花布局
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:paddingBottom="@dimen/activity_vertical_margin"
    android:paddingLeft="@dimen/activity_horizontal_margin"
    android:paddingRight="@dimen/activity_horizontal_margin"
    android:paddingTop="@dimen/activity_vertical_margin"
    tools:context=".MainActivity">

    <Button
        android:layout_alignParentTop="true"
        android:layout_alignParentLeft="true"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="top left" />

    <Button
        android:layout_alignParentTop="true"
        android:layout_alignParentRight="true"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="top rigth" />

    <Button
        android:layout_alignParentBottom="true"
        android:layout_alignParentLeft="true"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="bottom left" />

    <Button
        android:layout_alignParentBottom="true"
        android:layout_alignParentRight="true"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="botton right" />


    <Button
        android:id="@+id/center"
        android:layout_margin="10dp"
        android:layout_centerInParent="true"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="center" />

    <Button
        android:text="center1"
        android:layout_above="@id/center"
        android:layout_toLeftOf="@id/center"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />

    <Button
        android:text="center2"
        android:layout_above="@id/center"
        android:layout_toRightOf="@id/center"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />

    <Button
        android:text="center3"
        android:layout_below="@id/center"
        android:layout_toLeftOf="@id/center"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />

    <Button
        android:text="center4"
        android:layout_below="@id/center"
        android:layout_toRightOf="@id/center"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</RelativeLayout>
```
这个例子演示了相对父容器及相对兄弟视图的位置。屏幕四个角落的视图是相对父容器布局的，中间的几个视图组成的梅花视图使用的是相对兄弟视图布局的。
其效果如下：
<br/>
![relative layout](http://i3.tietuku.com/b664221c5a714eee.png)
<br/>
#### 3.3. 海报布局
我们在做视频相关的应用时，通常的设计是电影海报的下方叠加显示电影的标题信息。这种布局我们也可以用RelativeLayout来实现：
```xml
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:paddingBottom="@dimen/activity_vertical_margin"
    android:paddingLeft="@dimen/activity_horizontal_margin"
    android:paddingRight="@dimen/activity_horizontal_margin"
    android:paddingTop="@dimen/activity_vertical_margin"
    tools:context=".MainActivity">
    <RelativeLayout
        android:layout_width="300dp"
        android:layout_height="400dp"
        android:layout_centerInParent="true">
        <ImageView
            android:id="@+id/image"
            android:src="@mipmap/child"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:background="#af000000" />
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_alignParentBottom="true"
            android:background="#af000000"
            android:gravity="center"
            android:text="朝花夕拾"
            android:textColor="#ffffff"
            android:textSize="32dp" />
    </RelativeLayout>
</RelativeLayout>
```
效果如下：
<br/>
![relative layout](http://i3.tietuku.com/af06112e37f2a370.png)
<br/>
在此使用了同事画的一幅图，特别怀念童年的感觉。

### 4. FrameLayout
帧布局是android中功能最简单的布局，帧布局默认把所有的子视图都对齐到左上角，当然我们可以通过 layout_gravity 指定其他的对齐方式。帧布局只是把子视图按声明的先后顺序一层一层的叠加起来而已。下层的帧会被上层的帧给遮住。我们可以使用 bringChildToFront 方法
#### 4.1. 相关属性
- foreground：前景图像，这个图像是一直放在顶层的，不会被其他帧给覆盖
- foregroundGravity：前景图像的位置
- measureAllChildren：布尔型值，设置在onMeasure时，是否只布局 VISIBLE or INVISIBLE 的子视图，忽略 GONE 的子视图。默认为false， 因此，默认当一个子视图被设置为GONE时，则不会占据父容器的空间。但VISIBLE or INVISIBLE 还是会占据相应的空间的，只不过看不到而已。

#### 4.2. 海报布局
前一小节我们使用相对布局来实现电影海报的布局。其实使用FrameLayout也同样可以实现：
```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <FrameLayout
        android:layout_gravity="center"
        android:layout_width="300dp"
        android:layout_height="400dp">

        <ImageView
            android:id="@+id/image"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:background="#af000000"
            android:src="@mipmap/child" />

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_gravity="bottom"
            android:background="#af000000"
            android:gravity="center"
            android:text="朝花夕拾"
            android:textColor="#ffffff"
            android:textSize="32dp" />
    </FrameLayout>
</FrameLayout>
```

显示效果跟前一节用相对布局来实现是一样的。


### 5. GridLayout
GridLayout 是在android4.0的时候引入的。在android4.0版本之前，如果想要达到网格布局的效果，首先可以考虑使用最常见的LinearLayout布局，但是这样产生一些问题：
- 不能同时在X，Y轴方向上进行控件的对齐。
- 当多层布局嵌套时会有性能问题。

或者使用表格布局TabelLayout，这种方式会把包含的元素以行和列的形式进行排列，每行为一个TableRow对象，也可以是一个View对象，而在TableRow中还可以继续添加其他的控件，每添加一个子控件就成为一列。但是使用这种布局可能会出现不能将控件占据多个行或列的问题，而且渲染速度也不能得到很好的保证。

为了解决这些问题，所以产生了网格布局。下面就简单的介绍一下网格布局的使用。

#### 5.1. 相关属性
- orientation ：元素排列方向，水平或垂直，默认为水平方向。网格布局中的元素并不需要指定在某行某列，加入的组件会按顺序由左至右、由上至下摆放。如果指定为垂直方向则由上至下，由左至右摆放。
- rowCount：有多少行
- columnCount：有多少列
- useDefaultMargins：When set to true, tells GridLayout to use default margins when none are specified in a view's layout parameters. The default value is false.
- rowOrderPreserved：When set to true, forces row boundaries to appear in the same order as row indices.
- columnOrderPreserved：When set to true, forces column boundaries to appear in the same order as column indices. The default is true.


#### 5.2. 计算器布局
```xml
<?xml version="1.0" encoding="utf-8"?>
<GridLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:columnCount="4"
    android:orientation="horizontal"
    android:rowCount="5">
    <Button
        android:id="@+id/one"
        android:text="1" />
    <Button
        android:id="@+id/two"
        android:text="2" />
    <Button
        android:id="@+id/three"
        android:text="3" />
    <Button
        android:id="@+id/devide"
        android:text="/" />
    <Button
        android:id="@+id/four"
        android:text="4" />
    <Button
        android:id="@+id/five"
        android:text="5" />
    <Button
        android:id="@+id/six"
        android:text="6" />
    <Button
        android:id="@+id/multiply"
        android:text="×" />
    <Button
        android:id="@+id/seven"
        android:text="7" />
    <Button
        android:id="@+id/eight"
        android:text="8" />
    <Button
        android:id="@+id/nine"
        android:text="9" />
    <Button
        android:id="@+id/minus"
        android:text="-" />
    <Button
        android:id="@+id/zero"
        android:layout_columnSpan="2"
        android:layout_gravity="fill"
        android:text="0" />
    <Button
        android:id="@+id/point"
        android:text="." />
    <Button
        android:id="@+id/plus"
        android:layout_gravity="fill"
        android:layout_rowSpan="2"
        android:text="+" />
    <Button
        android:id="@+id/equal"
        android:layout_columnSpan="3"
        android:layout_gravity="fill"
        android:text="=" />
</GridLayout>
```

显示效果如下：
![caculator](http://i3.tietuku.com/a9003c7f7929966d.png)