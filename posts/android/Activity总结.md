Activity总结
------
**create time: 2015-08-17; update time: 2015-08-17**

---------------------------------------------------------------

Activity是android中四大组件之一，因为它负责控制界面的显示与交互，是用户看得见，摸得着的东西，是一个应用程序的门户。因此相对于service, contenprovider, brocast 这些不可见的组件来说，它显得更为重要。下面就从各方面来详细介绍Activity的知识点。

### 1. 生命周期
但凡有形之物，必有毁灭之时，世间万物，都有自己的生命周期，Activity也是一样。Activity定义了一系列的生命周期方法，系统在不同的时机会自动调用Activity相应的生命周期方法。如果我们需要监听处理Activity的某个生命周期，我们只需要 Override 这个生命周期方法就可以了。我们先来看看一张官方给出的 Activity 生命周期图:
<br/>
![activity生命周期](http://i3.tietuku.com/6a973c99a027cf9e.png)
<br/>
这么多的生命周期方法，它们会在什么情况下被调用呢？下面就一一说明：
- onCreate：在Activity创建时被调用，这个方法在整个生命周期中只会被调用一次，所以我们可以在这个方法中做一些只需要初始化一次的工作。比如 setContentView，findViewById 等。

- onStart：在onCreate或者onRestart之后被调用，紧接着系统会调用onResume，这个方法感觉地位有点尴尬，因为初始化工作应该放在onCreate，恢复交互的工作应该放在onResume，好像没onStart什么事。所以一般我也不会去重写这个方法。不过这个方法能说明Activity已经回到前台了，但此时还未能进行交互。

- onResume：这个方法被调用之后，我们就可以开始与用户进行交互了。这里可以播放一些动画，或者打开系统独占设备（比如摄像头）。但需要注意的是，这个方法并不能表明你的Activity已经可以被用户看见了，因为有可能系统窗口会挡在上面，比如keyguard。我们最好使用 onWindowFocusChanged 方法来确认activity是否对用户可见了。

- onPause：在activity即将进入后台之前被调用，与onResume相对应。如果我们在onResume打开了系统独占设备，我们则应该在这个方法中关闭系统独占设备。当系统内存不足时，系统有可能会回收处于pause状态的activity，所以，我们应该这在个方法里面对数据进行持久化的保存。但我们需要注意的是我们不应该在这个方法里面做耗时的工作。因为下一个activity的onResume要等当前activtiy的onPause返回后，才会被调用。为了避免影响用户的体验，所以不要在这里做耗时很长的工作。一般来说，onPause被调用后，紧接着会调用onStop，但我们看生命周期图，发现activity也有可能直接从onPause状态就转到onResume状态了。在activtiy还有部分可见的时候是处于pause状态的，只有activity完全不可见了，才会进入stop状态。比如说在弹出非全屏dialog，或者前台activity背景透明的情况下，我们是可以看到后台的activity的。

- onStop：activity完全被遮挡，不可见时被调用。这个方法是在前台activity的onResume方法被调用之后。

- onRestart：activity从stop状态重新回到前台时被调用，紧接着会调用onStart方法。

- onDestroy：activity被销毁时被调用。有可能是用户自己调用finish手动销毁，也有可能是系统内存不足时自动销毁。我们可以通过 isFinishing 方法来区分这两种情况。需要注意的是，我们不应该在这个方法里面保存用户数据！这个方法是用来释放应用的资源的，比如说线程资源。onPause释放系统资源，onDestroy释放进程资源。但有可能系统会直接杀掉这个activity所在的进程，而不调用onDestroy方法。

- onWindowFocusChanged：在Activity窗口获得或失去焦点时被调用。获得焦点时在onResume后被调用，失去焦点时在onPause后被调用。这个方法最重要特性是，`它被调用时布局已经完成了，我们可以通过View.getWidth获取各视图的大小了`。在onResume的时候我们通过View.getWidth获取视图的大小是为0的。

- onSaveInstanceState：(1)在Activity被覆盖或退居后台之后，系统资源不足将其杀死，此方法会被调用；(2)在用户改变屏幕方向时，此方法会被调用；(3)在当前Activity跳转到其他Activity或者按Home键回到主屏，自身退居后台时，此方法会被调用。第一种情况我们无法保证什么时候发生，系统根据资源紧张程度去调度；第二种是屏幕翻转方向时，系统先销毁当前的Activity，然后再重建一个新的，调用此方法时，我们可以保存一些临时数据；第三种情况系统调用此方法是为了保存当前窗口各个View组件的状态。onSaveInstanceState的调用顺序是在onPause之前。

- onRestoreInstanceState：(1)在Activity被覆盖或退居后台之后，系统资源不足将其杀死，然后用户又回到了此Activity，此方法会被调用；(2)在用户改变屏幕方向时，重建的过程中，此方法会被调用。我们可以重写此方法，以便可以恢复一些临时数据。onRestoreInstanceState的调用顺序是在onStart之后。

- onNewIntent：当有其他应用使用startActivity(Intent)方法来启动时，会被调用。

- onActivityResult：使用startActivityForResult启动一个activity，启动的activity返回结果时，此方法被调用。

后面几个回调并不属于生命周期方法，但它们与生命周期也是紧密相关的，所以也在此列出来。生命周期回调很容易理解，只要写两个activity，重写其中的生命周期方法，加上LOG，根据LOG就可以验证上面所说的各生命周期方法的调用时机了。在此就不多做演示了。

### 2. 启动模式

### 3. 任务栈task

### 4. intent-filter

### 5. activity间的交互

### 6. 横竖屏切换

### 7. HistoryRecord