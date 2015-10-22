android动画总结
------
**create time: 2015-10-22; update time: 2015-10-22**


---------------------------------------------------------------

android的动画主要分三大类：
- 补间动画
- 帧动画
- 属性动画

每种动画分类有它们的应用场景。下面我们详细的介绍一下这几种动画的原理和使用方法。

### 1. 补间动画（Tween  Animation）
补间动画的原理是给出起点和终点两个关键帧，通过在两个关键帧之间补充渐变的动画效果。目前补间动画支持五种动画效果：
- 位移：TranslateAnimation，xml标签为`<translate/>`
- 缩放：ScaleAnimation，xml标签为`<scale/>`
- 旋转：RotateAnimation，xml标签为`<rotate/>`
- 透明：AlphaAnimation，xml标签为`<alpha/>`
- 组合以上四种动画：AnimationSet，xml标签为`<set/>`

这五个类都是继承了Animation类:
<br/>
![Animation继承关系](https://raw.githubusercontent.com/android-cn/android-open-project-analysis/master/tech/animation/image/tweenhirachy.png)


Animation的属性（也即这五种动画的共用属性）有：
- duration：动画周期，单位为毫秒。
- startOffset：在调用start函数之后等待开始运行的时间，单位为毫秒。
- fillEnabled：When set to true, the value of fillBefore is taken into account. 
- fillBefore：该动画转化是否在动画开始前被应用
- fillAfter：该动画转化是否在动画结束后被应用，即保持终态的效果。若为false的话，动画结束后，会恢复到起始状态。
- repeatCount：动画重复次数， "-1" 为一直循环播放。
- repeatMode：动画重复方式，"restart" 为从头开始，"reverse" 为反向动画，即从终点到起点，类似于钟摆的效果，往返运动。
- zAdjustment：运行时在z轴上的位置，默认为normal。normal保持内容当前的z轴顺序，top运行时在最顶层显示，bottom运行时在最底层显示。
- detachWallpaper：Special option for window animations: if this window is on top of a wallpaper, don't animate the wallpaper with it.  
- interpolator：插值器，系统默认提供了几种插值器：线性（@android:anim/linear_interpolator），加速度（@android:anim/accelerate_interpolator）等，具体效果可以自己一个一个尝试。

其中有几个属性比较让人迷惑：fillEnabled， fillBefore。它们的关系文档中也说得不明不白，具体效果还是实际动手试试吧。

#### 1.1 位移
位移动画的效果为将View在X轴，Y轴上平移，支持XML属性如下：
- fromXDelta ：X轴起点
- fromYDelta：Y轴起点
- toXDelta：X轴终点
- toYDelta：Y轴终点

这几个属性有三种取值方式：
- 浮点数：相对自身原始位置的像素值。
- num%：相对于自己的百分比，比如 toXDelta 定义为 100%，就表示在 X 方向上移动自己的 1 倍距离。
- num%p：相对于父视图的百分比，比如 toXDelta  定义为 50%p，就表示在X方向上移动父视图的一半距离。

动画资源文件定义，res/anim/move.xml：
```
<?xml version="1.0" encoding="utf-8"?>
<translate xmlns:android="http://schemas.android.com/apk/res/android"
           android:duration="5000"
           android:fromXDelta="-50%p"
           android:fromYDelta="0"
           android:toXDelta="50%p"
           android:toYDelta="0"
           android:fillAfter="true"
           android:interpolator="@android:anim/linear_interpolator"
    >
</translate>
```

假如 view在父视图的X轴方向居中，这个动画的效果就是view从父视图的左边移动到父视图右边。

#### 1.2 缩放
缩放动画的效果为将 view 放大或缩小，支持的XML属性如下：
- fromXScale：
- fromYScale：
- toXScale：
- toYScale：

浮点值，为动画起始到结束时，X、Y 坐标上的伸缩尺寸。0.0 表示收缩到没有，1.0 表示正常无伸缩 。
- pivotX：X轴缩放的中心坐标
- pivotY：Y轴缩放的中心坐标

动画资源文件定义，res/anim/scale.xml：
```
<?xml version="1.0" encoding="utf-8"?>
<scale xmlns:android="http://schemas.android.com/apk/res/android"
       android:duration="2000"
       android:interpolator="@android:anim/accelerate_interpolator"
       android:pivotX="50%"
       android:pivotY="50%"
       android:fromXScale="1"
       android:fromYScale="1"
       android:toXScale="1.2"
       android:toYScale="1.2">

</scale>
```
将 view 从原始状态放大到1.2倍。

#### 1.3 旋转
旋转动画的效果是将 view 进行顺时针或逆时针旋转，最常见的应用场景就是音乐播放器的CD旋转效果了。支持的XML属性如下：
- fromDegrees：起始角度， 0-360度
- toDegrees：最终角度， 0-360度
- pivotX：X 轴旋转中心坐标
- pivotY：Y 轴旋转中心坐标

动画资源文件定义，res/anim/rotate.xml：
```
<?xml version="1.0" encoding="utf-8"?>
<rotate xmlns:android="http://schemas.android.com/apk/res/android"
        android:interpolator="@android:anim/linear_interpolator"
        android:duration="10000"
        android:fromDegrees="0"
        android:toDegrees="360"
        android:pivotX="50%"
        android:pivotY="50%"
        android:repeatCount="-1"
    >
</rotate>
```
以中心点顺时针旋转360度，不断重复。


#### 1.4 透明
透明动画的效果为改变view的透明度，达到一种若隐若现的视觉效果，或者突然闪现的效果，比如闪电的隐现就可以使用透明动画实现。支持的XML属性如下：
- fromAlpha：起始透明度
- toAlpha：终点透明度

浮点数，0.0为完全透明，1.0为完全不透明。
动画资源文件定义，res/anim/alpha.xml：
```
<?xml version="1.0" encoding="utf-8"?>
<alpha xmlns:android="http://schemas.android.com/apk/res/android"
       android:duration="2000"
       android:interpolator="@android:anim/accelerate_decelerate_interpolator"
       android:repeatCount="-1"
       android:repeatMode="reverse"
       android:fromAlpha="1.0"
       android:toAlpha="0.5">

</alpha>
```
从完全不透明渐变到半透明，然后由半透明渐变到完全不透明，如此重复变化。

#### 1.5 组合动画
当你需要应用多种动画效果时，就可以使用组合动画，组合动画相当于一个容器，可以放置多种动画效果。
支持的XML属性如下：
- shareInterpolator：容器内的动画是否共用一个插值器，设置为 true 的话我们就可以在`<set />`中指定插值器就可以了，容器内的其他动画就不用再一一设置插值器了。

动画资源文件定义，res/anim/set.xml：
```
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
     android:shareInterpolator="true"
     android:interpolator="@android:anim/linear_interpolator"
    >
    <translate
        android:duration="2000"
        android:fromXDelta="-200"
        android:fromYDelta="0"
        android:repeatCount="-1"
        android:repeatMode="reverse"
        android:toXDelta="200"
        android:toYDelta="0"
        >
    </translate>

    <rotate
        android:duration="10000"
        android:fromDegrees="0"
        android:pivotX="50%"
        android:pivotY="50%"
        android:repeatCount="-1"
        android:toDegrees="360"
        >
    </rotate>

    <scale
        android:duration="1000"
        android:fromXScale="0.8"
        android:fromYScale="0.8"
        android:pivotX="50%"
        android:pivotY="50%"
        android:repeatCount="-1"
        android:repeatMode="reverse"
        android:toXScale="1.2"
        android:toYScale="1.2">
    </scale>

    <alpha
        android:duration="2000"
        android:fromAlpha="1.0"
        android:repeatCount="-1"
        android:repeatMode="reverse"
        android:toAlpha="0.5">
    </alpha>
</set>
```
同时应用位移，缩放，旋转，透明度渐变动画。

我们在上面定义了这么多动画效果，要怎么应用到view上呢？非常简单：
```
Animation animation = AnimationUtils.loadAnimation(this, R.anim.move);
view.startAnimation(animation);
```
使用 AnimationUtils 从资源文件中加载动画，然后使用View 的startAnimation 方法即可。

### 2. 帧动画
帧动画原理是连续播放给出的每一帧图片而形成动画效果。 因为帧动画的帧序列内容不一样，不但给制作增加了负担而且最终输出的文件量也很大，但它的优势也很明显：帧动画具有非常大的灵活性，几乎可以表现任何想表现的内容，而它类似与电影的播放模式，很适合于表现细腻的动画。
#### 2.1 `<animation-list>`
帧动画需要以`<animation-list>`作为资源文件的根标签，其作为一个容器，放置所有的帧序列图片。其支持的属性如下：
- oneshot：如果为true，表示动画只播放一次停止在最后一帧上，如果设置为false表示动画循环播放。
- variablePadding：If true, allows the drawable’s padding to change based on the current state that is selected。
- visible：drawable的初始可见性，默认为flase，需要我们调用代码进入播放后，drawable才变成可见的。

#### 2.2 `<item>`
`<item>` 标签作为 `<animation-list>`的子标签，每一个 item 就是一个动画帧。有两个属性：
- drawable：一个帧画面
- duration：这个帧画面显示的时长

下面举个帧动画的实际例子：
首先准备下面六张图片，将其导入工程中，命名为 icon1 - icon6：
<table>
<tr>
<td>
<img src="http://i13.tietuku.com/d9ef4560bea8f608.png" /> 
<td/>
<td>
<img src="http://i13.tietuku.com/89be29322b5db7ee.png" />
<td/>
<td>
<img src="http://i13.tietuku.com/4a23cc92cdb28d6a.png" />
<td/>
<td>
<img src="http://i13.tietuku.com/f6e9fc67b9899e5c.png" />
<td/>
<td>
<img src="http://i13.tietuku.com/f6e9fc67b9899e5c.png" />
<td/>
<td>
<img src="http://i13.tietuku.com/9e5814c2639ffb10.png" />
<td/>
<tr/>
<table/>
定义动画资源文件，res/anim/frame.xml
```
<?xml version="1.0" encoding="utf-8"?>
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
                android:oneshot="false"
                android:variablePadding="true"
                android:visible="true"
    >
    <item android:drawable="@mipmap/icon1" android:duration="200" />
    <item android:drawable="@mipmap/icon2" android:duration="200" />
    <item android:drawable="@mipmap/icon3" android:duration="200" />
    <item android:drawable="@mipmap/icon4" android:duration="200" />
    <item android:drawable="@mipmap/icon5" android:duration="200" />
    <item android:drawable="@mipmap/icon6" android:duration="200" />
</animation-list>
```

这个帧动画有六个帧画面，每一帧的持续时间为200 毫秒。
布局文件中，将动画设置为 ImageView 的 src：
```
...
<ImageView
        android:id="@+id/view"
        android:src="@anim/frame"
        android:layout_centerInParent="true"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"/>
...
```

在代码中启动动画效果：
```
AnimationDrawable frame = (AnimationDrawable) view.getDrawable();
frame.start();
```

动画效果如下：<br />
<img src="http://i13.tietuku.com/0c41fcaa576c47f2.gif">

### 3. 属性动画