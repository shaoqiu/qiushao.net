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

以上即为Activity的所有生命周期方法，这些生命周期方法的调用时机是确定的，每一种生命周期方法被调用，则说明这个Activity进入了某种状态。就像一个状态机的状态转换一样。
此外，有几个回调方法，虽然不是生命周期，但与生命周期也是紧密相关的，顺便也提一下：

- onWindowFocusChanged：在Activity窗口获得或失去焦点时被调用。获得焦点时在onResume后被调用，失去焦点时在onPause后被调用。这个方法最重要特性是，`它被调用时布局已经完成了，我们可以通过View.getWidth获取各视图的大小了`。在onResume的时候我们通过View.getWidth获取视图的大小是为0的。

- onSaveInstanceState：是用来保存UI状态的，通常onSaveInstanceState()只适合用于保存一些临时性的状态，而onPause()适合用于数据的持久化保存。通过使用一个Bundle来保存UI的临时状态，以便在activity被杀掉，随后又被启动时恢复之前的状态。这个bundle在重建activity时会被传给onRestoreInstanceState和 onCreate方法。这个方法在用户按back键主动退出activity时是不会被调用的。
如果我们没有覆写onSaveInstanceState()方法, 此方法的默认实现会自动保存activity中的某些状态数据, 比如activity中各种UI控件的状态.。android应用框架中定义的几乎所有UI控件都恰当的实现了onSaveInstanceState()方法,因此当activity被摧毁和重建时, 这些UI控件会自动保存和恢复状态数据. 比如EditText控件会自动保存和恢复输入的数据,而CheckBox控件会自动保存和恢复选中状态.开发者只需要为这些控件指定一个唯一的ID(通过设置android:id属性即可), 剩余的事情就可以自动完成了.如果没有为控件指定ID, 则这个控件就不会进行自动的数据保存和恢复操作。

- onRestoreInstanceState：activity被杀掉后，又重建时，该方法被调用，用以恢复被杀掉之前的状态。

### 2. 启动模式
启动模式（launchMode）在多个Activity跳转的过程中扮演着重要的角色，它可以决定是否生成新的Activity实例，是否重用已存在的Activity实例，是否和其他Activity实例共用一个任务栈。Activity 有以下几种启动模式：
- standard：默认的启动模式，不管三七二十一，每次启动都生成新的实例。系统中可能会有多个对应的activity实例。

- singleTop：如果在某个任务栈有对应的Activity实例正位于栈顶，则重复利用，不再生成新的实例。其他情况生成新的实例。系统中可能会有多个对应的activity实例。

- singleTask：如果在某个任务栈中有对应的Activity实例，则将此Activity实例之上的其他实例全部出栈（即销毁），使其位于栈顶。系统中只有一个对应的activity实例。

- singleInstance：启用一个新的栈结构，将对应的Acitvity放置于这个新的栈结构中，并保证不再有其他Activity实例进入。系统中只有一个对应的activity实例。
 
### 3. 任务栈task
task是一个具有栈结构的容器，可以放置多个Activity实例。以栈的形式组织。遵守先进先出原则。所有的activity都归属于某一个栈，那系统怎么确定activity的归属栈呢？与三个方面相关：launchMode； taskAffinity；Intent Flags。launchMode前面已经说过了，这里就不再细说，下面我们来说说另外两个。
#### 3.1. taskAffinity
Affinity 翻译为亲和力，taskAffinity意味着task对activity的亲和力。指定自己要放在哪个栈中。拥有相同taskAffinity的多个Activity理论同属于一个task，task自身的taskAffinity决定于根Activity的taskAffinity值。
默认情况下，一个应用内的所有Activity都具有相同的taskAffinity，都是从Application继承而来，而Application默认的taskAffinity是应用的包名，我们可以为Application设置taskAffinity属性值，这样可以应用到Application下的所有activity，也可以单独为某个Activity设置taskAffinity。

#### 3.2. Intent Flags

### 4. Intent Filter

### 5. Activity间的交互

### 6. 横竖屏切换

### 7. HistoryRecord