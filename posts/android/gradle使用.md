gradle使用
------
**create time: 2015-07-23; update time: 2015-07-24**

---------------------------------------------------------------

目前我们的项目组决定把开发工具转移到**android-studio**，以后的新项目都使用android-studio来开发。android-studio是使用**gradle**来进行构建的，所以有必要先熟悉一下 gradle。参考[官方文档](https://docs.gradle.org/current/userguide/userguide)

### 1. gradle 简介
引用官方的介绍：
> * A very flexible general purpose build tool like Ant.
> * Switchable, build-by-convention frameworks a la Maven. But we never lock you in!
> * Very powerful support for multi-project builds.
> * Very powerful dependency management (based on Apache Ivy).
> * Full support for your existing Maven or Ivy repository infrastructure.
> * Support for transitive dependency management without the need for remote repositories or pom.xml and ivy.xml files.
> * Ant tasks and builds as first class citizens.
> * Groovy build scripts.
> * A rich domain model for describing your build. 

从官方的介绍中我们大概可以知道 gradle 是一个非常灵活的构建工具，而且兼容现有的构建工具（ant, manven, Ivy），支持多工程构建，具有强大的依赖管理能力。

### 2. 基本概念
#### 2.1. project 和 task
在 gradle 中所有的东西都是基于两个基本概念：工程（project）和任务（task）。
使用 gradle 可以一次构建一个或多个工程。这里面的工程可以是各种各样的工程，可以是一个 JAR 包，可以是一个 web 应用，当然也可以是一个 android 应用。一个工程也可以不做任何构建工作，而用来完成部署工作，例如把应用部署到生产环境。
所有的工程都由一个或多个任务组成。一个任务就代表了在构建时会自动完成的一些工作。这些工作有可能是编译源文件，生成JAR包，生成文档，部署到生产环境等。
下面我们将会举几个简单的例子来说明gradle的使用。

#### 2.2 hello world
当我们运行gradle 命令时，gradle 会在当前目录寻找一个文件 `build.gradle`，我们叫它构建脚本，严格来说，应该叫它构建配置脚本。这个构建脚本定义了它的工程和它包含的任务。下面我们就以**hello world**工程来做个示范。这个工程只是打印了一行`hello world`而已。
创建一个文件，输入以下内容：
```
task hello {
    doLast {
        println 'Hello world!'
    }
}
```
然后在命令行中输入以下命令
```
D:\project\gradle>gradle -q hello
Hello world!
D:\project\gradle>
```
屏幕输出了一行`Hello world!`。这个构建定义了一个任务 hello ，这个任务有一个操作（action），当我们运行`gradle hello`时，gradle 就会执行 hello 这个任务，也就是执行你在任务中提供的操作。这些操作是将要执行 groovy 代码块。

#### 2.3. 定义任务的捷径
有一个快速定义任务的方法，看起来会更简洁：
```
task hello << {
    println 'Hello world!'
}
```
下面的例子都会采用这种形式。

#### 2.4. 构建脚本就是代码
gradle 的构建脚本中，你可以使用所有 groovy 语言的功能：
```
task upper << {
    String someString = 'mY_nAmE'
    println "Original: " + someString 
    println "Upper case: " + someString.toUpperCase()
}
```
运行gradle，结果如下：
```
D:\project\gradle>gradle -q upper
Original: mY_nAmE
Upper case: MY_NAME
D:\project\gradle>
```

#### 2.4. 任务依赖
正如你所猜的，我们可以声明一个任务叙事另一个任务：
```
task hello << {
    println 'Hello world!'
}
task intro(dependsOn: hello) << {
    println "I'm Gradle"
}
```
输出如下：
```
D:\project\gradle>gradle -q intro
Hello world!
I'm Gradle
D:\project\gradle>
```

需要说明的是任务的依赖声明可以不依赖任务的声明顺序。我们可以将 intro 任务放在 hello 任务声明之前，但需要做些修改，依赖的任务名需要用字符串的形式：
```
task intro(dependsOn: "hello") << {
    println "I'm Gradle"
}
task hello << {
    println 'Hello world!'
}
```

这个功能对于同时构建多个工程时是非常有用的。具体的后面再讨论。

#### 2.6. 默认任务
gradle 允许我们定义一个或多个默认任务，用以进行构建：
```
defaultTasks 'clean', 'run'

task clean << {
    println 'Default Cleaning!'
}

task run << {
    println 'Default Running!'
}

task other << {
    println "I'm not a default task!"
}
```
运行结果如下：
```
D:\project\gradle>gradle -q
Default Cleaning!
Default Running!
D:\project\gradle>
```

#### 2.7. 使用DAG进行配置
[gradle build lifecycle](https://docs.gradle.org/current/userguide/build_lifecycle.html)中介绍到，gradle 有一个配置阶段和一个执行阶段，配置阶段完成后，gradle 就可以知道所有将会执行的任务。gradle 提供了一个 hook 让我们可以获取这个信息。一个使用场景就是我们可以检查 release 任务是否在将会执行的任务中。根据这个，我们就可以给一些变量设置相应的值。例如：
```
task distribution << {
    println "We build the zip with version=$version"
}

task release(dependsOn: 'distribution') << {
    println 'We release now'
}

gradle.taskGraph.whenReady {taskGraph ->
    if (taskGraph.hasTask(release)) {
        version = '1.0'
    } else {
        version = '1.0-SNAPSHOT'
    }
}
```

### 3. 构建java工程
通过上面的例子，我们大概了解了工程，任务的概念。不过上面的例子中我们只是单纯的输出而已，并没有进行编译，打包，发布的实际工作。下面我们就来使用gradle构建一个工程。在这个工程上演示各种实际用法。

#### 3.1. 在android-studio上构建可执行的java程序
我看其他教程都是教用户在命令行的干活，自己手动创建工程目录结构，全手动编写构建脚本，不知道他们是不是也不使用IDE来写 java 代码，我真是醉了。。。
下面我们还是研究研究在android-stuidio上怎么构建可执行的java程序吧。后面的例子也全都是在android-studio上完成的。

新建一个工程`JavaTest`，在 android-studio中建立的工程都必须是android工程，没有纯 java 工程。我们就按它的来，先创建一个android工程。创建好工程之后：默认的结构是这样的：<br/>
![默认工程结构](http://i1.tietuku.com/a018ac5b050028e9.png)
<br/>
我们发现里面有两个`build.gradle`文件，一个`settings.gradle`文件。android-studio中工程的概念跟eclipse有点区别。它更像eclipse中的workspace概念。在android-studio中，一个工程（project）可以包含一个或多个模块（module）。工程的 build.gradle 定义了所有模块共用的编译规则，一般情况下我们不需要修改。settings.gradle 中列举了需要构建的模块。每一个模块下面都有一个自己的 build.gradle 构建脚本。
app 模块我们可以先不去管它，下面我们增加自己的纯java模块。

#### 3.2. 增加 Module
file --> new --> new module ，然后选择 java library：
<br/>
![新建java library模块](http://i3.tietuku.com/a458a3fc47d3f29d.png)
<br/>
然后修改模块名，包名，类名如下：
![修改模块信息](http://i3.tietuku.com/82730088bd295b55.png)

新模块创建好了，我们发现多了一个build.gradle文件，这个文件就是我们新模块的构建脚本。还多了一个 `hello`目录。再看 settings.gradle，里面也增加了刚才创建的新模块。
下面就让我们新建的模块可以像普通java程序一样跑起来。
修改`Hello.java`文件，增加`main`方法：
```java
package net.qiushao;

public class Hello {
    public static void main(String[] args) {
        System.out.println("hello android studio");
    }
}
```
修改hello模块的build.gradle如下：
```
apply plugin: 'java'

dependencies {
    compile fileTree(dir: 'libs', include: ['*.jar'])
}

jar {
    manifest {
        attributes 'Main-Class': 'net.qiushao.Hello'
    }
}
```
然后再 build --> make module hello 。就能编译生成一个可执行的jar文件了。生成的文件在JavaTest\hello\build\libs 目录，我们用 CMD 进入这个目录，执行命令：
```
D:\project\android-studio\JavaTest\hello\build\libs>java -jar hello.jar
hello android studio

D:\project\android-studio\JavaTest\hello\build\libs>
```
我们新建的模块是能运行起来了，但是为什么不能在android-studio中直接运行，还要跑到CMD去执行，太麻烦了。当然也可以直接在android-studio中运行。不过构建脚本要做些修改：
```
apply plugin: 'java'
apply plugin: 'application'
mainClassName = "net.qiushao.Hello"

dependencies {
    compile fileTree(dir: 'libs', include: ['*.jar'])
}

jar {
    manifest {
        attributes 'Main-Class': 'net.qiushao.Hello'
    }
}
```
我们加了两行，增加了一个插件`application`，指定了入口类`net.qiushao.Hello`。其实`application`中已经包含有了`java`插件的功能。关于这两个plugin的解释，详见官方文档[plugin java](https://docs.gradle.org/current/userguide/java_plugin.html)，[plugin application](https://docs.gradle.org/current/userguide/application_plugin.html)。
然后右击`Hello.java`文件，选择`Run Hello.main()`。程序就运行起来了。


### 4. 模块间依赖
现在我们的工程中已经有两个模块了`app`，`hello`。假如`hello`模块是作为一个库供`app`模块调用的，我们要怎样设置才能在`app`模块中调用`hello`模块中的类呢？很简单，只要在`app`模块的 build.gradle文件中加入以下配置就可以了：
```
dependencies {
    compile project(':hello')
}
```

### 5. 引用第三方library
#### 5.1. 引用本地library
假如第三方给我们提供了一个 jar 包，那我们怎么把这个 jar 包加入到我们的工程中呢？
android-studio中的视图比较多，感觉特别乱。。。
首先我们需要切换到`project`视图：
<br/>
![project视图](http://i3.tietuku.com/8af1df26b4ab7fd4.png)
<br/>
这个视图才会显示真实的目录结构。但android-studio默认的视图是 `android` ，我找了大半天，发现居然没有显示libs 目录。。。
最新版本的android-studio，只要我们将 jar 文件放到 libs目录，然后刷新一个工程就可以了。因为在构建脚本中有如下配置：
```
compile fileTree(dir: 'libs', include: ['*.jar'])
```
如果不行的话，右击这个 jar 文件件，选择 "add as library"就可以了。

#### 5.2. 引用远程仓库的library
这个更简单了，只要在模块的构建脚本中加入一行配置即可。比如我们要加入 Android-Universal-Image-Loader 库，则只要加入下面这行配置即可：
```
compile 'com.nostra13.universalimageloader:universal-image-loader:1.9.4'
```
我们需要使用哪个组件，先去它的官网查看配置方法，看看是否支持这种配置方式。
gradle会自动去下载相应的库文件。当然这种方式要求这个库已经上传到中央仓库了。目前很多开源的组件都已经上传到gradle的中央仓库了。不过这种方式比较依赖网络。